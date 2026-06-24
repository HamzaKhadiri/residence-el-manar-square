import streamlit as st
import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from supabase import create_client

# 1. إعدادات الصفحة الأولى
st.set_page_config(page_title="Résidence El Manar Square", page_icon="🏢", layout="wide")

# 2. تصميم الـ CSS لمحاكاة موقع eDary
st.markdown("""
<style>

/* Main */
.main {
    background-color: #f5f7fb;
}

/* Cards */
.edary-box-card{
    background:gris;
    border-radius:50px;
    padding:10px;
    box-shadow:0 2px 12px rgba(0,0,0,.08);
    border-left:5px solid #d91c23;
    transition:0.3s;
}

.edary-box-card:hover{
    transform:translateY(-3px);
    box-shadow:0 6px 18px rgba(0,0,0,.15);
}

.edary-box-title{
    color:#666;
    font-size:20px;
    margin-bottom:15px;
}

.edary-box-value{
    font-size:40px;
    font-weight:bold;
}

/* Buttons */
.stButton>button{
    border-radius:40px;
    font-weight:bold;
    height:60px;
}

/* DataFrame */
[data-testid="stDataFrame"]{
    border-radius:40px;
    overflow:hidden;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:#b5121b;
}

section[data-testid="stSidebar"] *{
    color:black;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* تنسيق الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: #b5121b;
    }
    
    /* جعل نصوص العناوين والملصقات في الشريط الجانبي بيضاء لتكون واضحة */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    
    /* تنسيق مربعات الإدخال في الشريط الجانبي */
    [data-testid="stSidebar"] input {
        color: black !important; /* النص المكتوب داخل المربع يكون أسود للوضوح */
    }
</style>
""", unsafe_allow_html=True)

# 3. إعدادات الأشهر والعمارات والسنوات
months_cols = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
immeubles_list = ["Imm A", "Imm B", "Imm C", "Imm D", "Imm E", "Imm F", "Imm G", "Bureau"]
years_list = ["2025", "2026", "2027", "2028"]

excel_file = "syndic_data.xlsx"
expenses_file = "expenses_data.xlsx"

# دالة جلب بيانات الاشتراكات وتصحيحها أوتوماتيكياً
def load_data():
    if os.path.exists(excel_file):
        try:
            df_existing = pd.read_excel(excel_file)
            if "Année / السنة" not in df_existing.columns:
                df_existing["Année / السنة"] = "2026"
            for m in months_cols:
                if m not in df_existing.columns:
                    df_existing[m] = "Non Payé"
            return df_existing
        except:
            pass
    
    all_rows = []
    for imm in immeubles_list:
        for i in range(1, 11):
            row = {
                "Immeuble / الإقامة": imm,
                "Appartement / الشقة": f"N° {i}",
                "Nom et prénom / الاسم الكامل": f"Résident {imm[-1]}-{i}",
                          "Téléphone / الهاتف": f"060000000{i}" f"070000000{i}",
                "Année / السنة": "2026"
            }
            for m in months_cols:
                row[m] = "Non Payé"
            all_rows.append(row)
            
            for y in ["2024", "2025", "2027", "2028"]:
                row_y = row.copy()
                row_y["Année / السنة"] = y
                all_rows.append(row_y)
                
    df = pd.DataFrame(all_rows)
    df.to_excel(excel_file, index=False)
    return df

# دالة ذكية ومصححة لجلب المصاريف وإضافة أعمدة السنة والشهر تلقائياً إذا كانت ناقصة
def load_expenses():
    if os.path.exists(expenses_file):
        try:
            df_exp = pd.read_excel(expenses_file)
            
            # إصلاح تلقائي إذا كانت الأعمدة ناقصة في الملف القديم
            if "ANNEE" not in df_exp.columns or "MOIS" not in df_exp.columns:
                annees = []
                mois = []
                for idx, row in df_exp.iterrows():
                    try:
                        date_str = str(row["DATE"])
                        dt = pd.to_datetime(date_str, dayfirst=True)
                        annees.append(str(dt.year))
                        mois.append(str(dt.month))
                    except:
                        annees.append(str(datetime.now().year))
                        mois.append(str(datetime.now().month))
                df_exp["ANNEE"] = annees
                df_exp["MOIS"] = mois
                # حفظ التعديلات في الملف فوراً بعد الإصلاح
                df_exp.to_excel(expenses_file, index=False)
            return df_exp
        except Exception as e:
            st.error(f"Erreur lors du chargement des dépenses: {e}")
            
    # إنشاء الملف إذا لم يكن موجوداً
    today = datetime.now() # تم تصحيح الاسم ليكون مطابقاً
    data = {
        "DATE": [today.strftime("%d/%m/%Y")],
        "ANNEE": [str(today.year)],
        "MOIS": [str(today.month)],
        "MODE DE PAIEMENT": ["ESPECE"],
        "CATEGORIE": ["Trésorerie initiale"],
        "DESIGNATION": ["Trésorerie initiale"],
        "DEPENSE": [0.0],
    }
    df = pd.DataFrame(data)
    df.to_excel(expenses_file, index=False)
    return df
df = load_data()
df_expenses = load_expenses()
excel_file = "syndic_data.xlsx"
df_check = pd.read_excel(excel_file) if os.path.exists(excel_file) else pd.DataFrame()
 
# --- في كود تسجيل الدخول ---
# 1. تهيئة الحالة الأساسية (يجب أن تكون دائماً في الأعلى)
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# 2. تحميل البيانات
# (قم بوضع دوال load_data و load_expenses هنا)
df_check = pd.read_excel("syndic_data.xlsx") if os.path.exists("syndic_data.xlsx") else pd.DataFrame()

# 3. منطق تسجيل الدخول
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center;'>🔐 Résidence El Manar Square</h1>", unsafe_allow_html=True)
    input_name = st.text_input("أدخل اسمك الكامل / Entrez votre nom complet:")
    
    if st.button("دخول / Connexion"):
        input_name_clean = input_name.strip().lower()
        input_parts = input_name_clean.split()
        
        # --- حل مشكلة الـ float: تنظيف البيانات أولاً ---
        # 1. تحويل العمود إلى نص 
        # 2. استبدال القيم الفارغة (NaN/nan) بنص فارغ ""
        df_check["Nom et prénom / الاسم الكامل"] = df_check["Nom et prénom / الاسم الكامل"].astype(str).replace('nan', '')
        
        found = False
        user_found = None
        
        for name_in_db in df_check["Nom et prénom / الاسم الكامل"].tolist():
            # تحويل اسم قاعدة البيانات لنص صغير قبل البحث
            db_name_clean = str(name_in_db).strip().lower()
            
            # التحقق: هل كل أجزاء الاسم المدخل موجودة في الاسم الموجود في الإكسيل؟
            if db_name_clean != "" and all(part in db_name_clean for part in input_parts):
                found = True
                user_found = db_name_clean
                break
        
        if input_name_clean == "admin":
            st.session_state.user_name = "Admin"
            st.rerun()
        elif found:
            st.session_state.user_name = user_found
            st.rerun()
        else:
            st.error("الاسم غير موجود أو خطأ في الكتابة!")
    st.stop() # إيقاف الكود هنا إذا لم يسجل المستخدم دخوله

# 4. بعد تسجيل الدخول، يمكننا الآن تعريف صلاحية الأدمن
is_admin = (st.session_state.user_name == "Admin")

# --- 5. البانر وزر الخروج ---
st.markdown(f'<div class="edary-banner">🏢 Résidence El Manar Square - Espace: {st.session_state.user_name}</div>', unsafe_allow_html=True)
if st.sidebar.button("خروج / Déconnexion"):
    st.session_state.user_name = None
    st.rerun()

# --- 6. التنقل ---
if "current_page" not in st.session_state: st.session_state.current_page = "Tableau de bord"
nav_cols = st.columns(3)
if nav_cols[0].button("📊 Tableau de bord"): st.session_state.current_page = "Tableau de bord"
if nav_cols[1].button("💵 Cotisations"): st.session_state.current_page = "Cotisations"
if nav_cols[2].button("🏦 Trésorerie"): st.session_state.current_page = "Trésorerie"

# --- القائمة الجانبية (لرفع صلاحية الأدمن) ---
st.sidebar.markdown("### ⚙️ Configuration")
langue = st.sidebar.selectbox("Langue", ["Français", "العربية"])
password = st.sidebar.text_input("القن السري (للإدارة فقط)", type="password")
if password == "1234":
    is_admin = True
    st.sidebar.success("Accès Administrateur")

# ==================== عرض المحتوى ====================

# --- 1. لوحة التحكم (Tableau de bord) ---
if st.session_state.current_page == "Tableau de bord":
        st.subheader("📊 Tableau de bord")
        years_list = sorted(df["Année / السنة"].dropna().unique().astype(str).tolist())
        selected_year = st.selectbox("اختر السنة / Sélectionnez l'année", years_list)
        if is_admin:
            sel_imm_dash = st.selectbox("Filtrer par Immeuble", ["Tous"] + immeubles_list)
            df_dash = df.copy()
            df_dash = df_dash[df_dash["Année / السنة"].astype(str) == selected_year]
            if sel_imm_dash != "Tous":
                df_dash = df_dash[df_dash["Immeuble / الإقامة"] == sel_imm_dash]
            
            columns_to_show_admin = ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف"]
            st.dataframe(df_dash[columns_to_show_admin], use_container_width=True, hide_index=True, height=750)
        else:
            # كود المستخدم العادي
            df_user = df[df["Nom et prénom / الاسم الكامل"].str.contains(st.session_state.user_name, case=False, na=False)]
            df_user = df_user[df_user["Année / السنة"].astype(str) == selected_year]
            
            columns_to_show = ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف"]
            if not df_user.empty:
                st.dataframe(df_user[columns_to_show], use_container_width=True, hide_index=True)
            else:
                st.warning("لا توجد بيانات مسجلة باسمك لهذه السنة.")

# --- 2. الاشتراكات (Cotisations) ---
# تأكد أن هذه الـ elif تبدأ من نفس مستوى الـ if الأولى (بدون إزاحة)
elif st.session_state.current_page == "Cotisations":
    st.subheader("💵 Situation des paiements de l'année" if langue == "Français" else "💵 وضعية الاشتراكات السنوية")        
    
    if is_admin:
        # --- تحسين توزيع الفلاتر: سطرين، كل سطر يحتوي على فلترين ---
        row1 = st.columns(2)
        row2 = st.columns(2)
        
        with row1[0]:
            selected_year = st.selectbox("Année / السنة", years_list)
        with row1[1]:
            months_list = ["الكل"] + months_cols
            selected_month = st.selectbox("Mois / الشهر", months_list)
            
        with row2[0]:
            selected_imm = st.selectbox("Immeuble / العمارة", immeubles_list)
            
        with row2[1]:
            
            apparts_in_imm = ["الكل"] + sorted(df[df["Immeuble / الإقامة"] == selected_imm]["Appartement / الشقة"].unique().tolist())
            selected_appart = st.selectbox("Appartement / الشقة", apparts_in_imm)
            
        st.markdown("---") # خط فاصل للتنظيم
        
        # --- الفلترة بناءً على العمارة والشقة ---
        df["Année / السنة"] = df["Année / السنة"].astype(str)
        mask = (df["Année / السنة"] == str(selected_year)) & (df["Immeuble / الإقامة"] == selected_imm)
        
        if selected_appart != "الكل":
            mask = mask & (df["Appartement / الشقة"] == selected_appart)
            
        df_filtered = df[mask].copy()
        
        # --- تصفية أعمدة الأشهر (إذا اختار المدير شهراً واحداً) ---
        cols_to_display = ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف", "Année / السنة"]
        if selected_month != "الكل":
            cols_to_display += [selected_month]
        else:
            cols_to_display += months_cols
            
        df_display = df_filtered[cols_to_display].copy()

        # تحويل القيم لرموز للعرض
        for month in (months_cols if selected_month == "الكل" else [selected_month]):
            if month in df_display.columns:
                df_display[month] = df_display[month].apply(lambda x: "✅" if str(x).strip().lower() == 'payé' else "❌")
        
        st.info("Mode Édition activé (Syndic)")
        
        edited_display_df = st.data_editor(
            df_display, 
            column_config={
                **{col: st.column_config.TextColumn(col, disabled=True) for col in ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف", "Année / السنة"]},
                **{month: st.column_config.SelectboxColumn(month, options=["✅", "❌"]) for month in (months_cols if selected_month == "الكل" else [selected_month])}
            },
            use_container_width=True, 
            hide_index=True 
        )
        
        if st.button("Sauvegarder les changements / حفظ التغييرات", type="primary"):
            # إرجاع القيم للإكسيل
            for month in (months_cols if selected_month == "الكل" else [selected_month]):
                edited_display_df[month] = edited_display_df[month].apply(lambda x: 'payé' if x == '✅' else 'Non Payé')
            
            # تحديث الداتا فريم وتخزينه
            df.update(edited_display_df)
            df.to_excel(excel_file, index=False)
            st.success("Données enregistrées avec succès !")
            st.rerun()

    else:
        # --- كود الساكن (User) ---
        st.write("### 📋 وضعية اشتراكاتك الخاصة:")
        # تصفية البيانات حسب اسم المستخدم المسجل حالياً في الـ session
        df_user_cotis = df[df["Nom et prénom / الاسم الكامل"].str.contains(st.session_state.user_name, case=False, na=False)].copy()
        
        # تحويل القيم لرموز بصرية للقراءة فقط
        for month in months_cols:
            df_user_cotis[month] = df_user_cotis[month].apply(lambda x: "✅" if str(x).strip().lower() == 'payé' else "❌")
        
        # عرض البيانات
        st.dataframe(df_user_cotis, use_container_width=True, hide_index=True)

# 🏦 TRÉSORERIE PAGE
elif st.session_state.current_page == "Trésorerie":
    import pandas as pd
    import streamlit as st
    import plotly.graph_objects as go
    from datetime import datetime
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    st.subheader("🏦 Trésorerie - الوضعية المالية")

    if is_admin:
        # =========================
        # 📅 FILTERS
        # =========================
        c1, c2 = st.columns(2)
        with c1:
            tres_year = st.selectbox("Année", years_list, index=years_list.index("2026") if "2026" in years_list else 0, key="tres_year")
        with c2:
            tres_month_num = st.selectbox("Mois", [str(i) for i in range(1, 13)], index=0, key="tres_month")
        
        st.caption(f"📅 Période: {tres_month_num}/{tres_year}")

        # =========================
        # 💰 CONSTANTS & CALCULATIONS
        # =========================
        PRIX_PAR_PAYE = 300
        solde_initial = 0.0

        # حسابات شاملة
        all_paid = (df[months_cols].astype(str).apply(lambda col: col.str.strip().str.lower() == "payé").sum().sum())
        total_recette_all = all_paid * PRIX_PAR_PAYE
        total_depense_all = df_expenses["DEPENSE"].sum()
        solde_global = solde_initial + total_recette_all - total_depense_all

        # حسابات الشهر الحالي
        month_name = months_cols[int(tres_month_num) - 1]
        df_year = df[df["Année / السنة"].astype(str) == str(tres_year)]
        total_recette_month = (df_year[month_name].astype(str).str.strip().str.lower().eq("payé").sum() * PRIX_PAR_PAYE)
        
        df_exp_month = df_expenses[(df_expenses["ANNEE"].astype(str) == str(tres_year)) & (df_expenses["MOIS"].astype(str) == str(tres_month_num))]
        total_depense_month = df_exp_month["DEPENSE"].sum()
        solde_month = total_recette_month - total_depense_month

        # 🔔 ALERTS
        st.markdown("### 🔔 Alertes")
        if solde_month < 0: st.error("⚠️ Déficit ce mois!")
        elif solde_month < 1000: st.warning("⚠️ Solde faible")
        else: st.success("✔️ Situation stable")

        # 📊 KPIs
        c1, c2, c3, c4 = st.columns(4)
        def kpi(title, value, color):
            st.markdown(f"""<div style="background:#111; padding:15px; border-radius:12px; text-align:center; border:1px solid #333;">
            <div style="color:#aaa;font-size:14px;">{title}</div>
            <div style="color:{color};font-size:20px;font-weight:bold;">{value:,.2f} MAD</div></div>""", unsafe_allow_html=True)
        
        with c1: kpi("💰 Recettes mois", total_recette_month, "#2ecc71")
        with c2: kpi("💸 Dépenses mois", total_depense_month, "#e74c3c")
        with c3: kpi("📊 Solde mois", solde_month, "#3498db")
        with c4: kpi("🏦 Solde global", solde_global, "#8e44ad")

        st.divider()

        # ➕ ADD EXPENSE
        st.markdown("### ➕ Ajouter une dépense")
        c1, c2, c3 = st.columns(3)
        with c1: 
            mode = st.selectbox("Mode paiement", ["ESPECE", "VIREMENT", "CHEQUE", "FRAIS BANQUE"])
            cat = st.selectbox("Catégorie", ["Entretien", "Salaire", "Electricité", "PRODUIT", "Autres"])
        with c2: 
            date = st.date_input("Date")
            libelle = st.text_input("Libellé")
        with c3: 
            montant = st.number_input("Montant", min_value=0.0, step=50.0)
            if st.button("✔️ Ajouter", use_container_width=True):
                if libelle and montant > 0:
                    new_row = {"DATE": date.strftime("%d/%m/%Y"), "ANNEE": str(tres_year), "MOIS": str(tres_month_num), "MODE DE PAIEMENT": mode, "CATEGORIE": cat.upper(), "DESIGNATION": libelle, "DEPENSE": montant}
                    df_expenses = pd.concat([df_expenses, pd.DataFrame([new_row])], ignore_index=True)
                    df_expenses.to_excel(expenses_file, index=False)
                    st.success("✔️ Ajouté!"); st.rerun()

        st.markdown("### 📋 Opérations")
        
        st.caption(f"📅 Période: {tres_month_num}/{tres_year}")
        st.caption(f"📅 Période: {tres_month_num}/{tres_year}")
        df_display = df_exp_month.copy()
        df_display["DEPENSE"] = pd.to_numeric(df_display["DEPENSE"], errors="coerce").fillna(0)
        df_display["RECETTE"] = 0.0
        df_display["DATE"] = pd.to_datetime(df_display["DATE"], errors="coerce", dayfirst=True)
        df_display = df_display.sort_values("DATE", ascending=False)
        df_display["DATE"] = df_display["DATE"].dt.strftime("%d/%m/%Y")
        
        resume = pd.DataFrame([{"DATE": "", "MODE DE PAIEMENT": "", "CATEGORIE": "RÉSUMÉ", "DESIGNATION": "🟢 TOTAL RECETTES", "DEPENSE": 0, "RECETTE": total_recette_month}])
        df_final = pd.concat([resume, df_display], ignore_index=True)
        st.dataframe(df_final, use_container_width=True, hide_index=True)


                # 📊 GRAPH ÉVOLUTION ANNUELLE (PLOTLY)
        import plotly.graph_objects as go
        st.markdown(f"### 📈 Évolution des recettes et dépenses pour l'année {tres_year}")

        months_names = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        recettes_list = []
        depenses_list = []

        for m in range(1, 13):
            m_col = months_cols[m-1]
            recette = (df_year[m_col].astype(str).str.strip().str.lower().eq("payé").sum() * 300)
            recettes_list.append(recette)
            
            exp_m = df_expenses[(df_expenses["ANNEE"].astype(str) == str(tres_year)) & (df_expenses["MOIS"].astype(str) == str(m))]
            depenses_list.append(exp_m["DEPENSE"].sum())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months_names, y=recettes_list, mode='lines+markers', name='Recettes', line=dict(color='#f39c12', width=5)))
        fig.add_trace(go.Scatter(x=months_names, y=depenses_list, mode='lines+markers', name='Dépenses', line=dict(color='#e74c3c', width=5)))
        
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Montant (MAD)",
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 💾 Export")
    
    # 1. تصدير Excel (بدون CSV كما طلبت)
    excel_file = f"tresorerie_{tres_year}_{tres_month_num}.xlsx"
    df_final.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f:
        st.download_button("⬇️ Excel", data=f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # 2. تقرير PDF (بشكل جدول)
    st.markdown("### 📄 Rapport PDF")
    if st.button("Créer PDF"):
        file_name = f"rapport_{tres_year}_{tres_month_num}.pdf"
        doc = SimpleDocTemplate(file_name, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>Rapport de Trésorerie</b>", styles["Title"]))
        elements.append(Spacer(1, 12))
        
        data = [
            ["Désignation", "Montant (MAD)"],
            ["Total Recettes", f"{total_recette_month:,.2f}"],
            ["Total Dépenses", f"{total_depense_month:,.2f}"],
            ["Solde Final", f"{solde_month:,.2f}"]
        ]

        table = Table(data, colWidths=[250, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        doc.build(elements)
        st.success("PDF généré !")
        st.rerun()

    # عرض زر التحميل PDF إذا كان الملف موجوداً
    import os
    file_name = f"rapport_{tres_year}_{tres_month_num}.pdf"
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            st.download_button("⬇️ Télécharger PDF", f, file_name=file_name, mime="application/pdf")

# إغلاق شرط الـ Admin (هذه الـ else يجب أن تكون في مستوى الـ if is_admin)
else:
    st.warning("⚠️ هذه الصفحة مخصصة للمدير فقط.")
