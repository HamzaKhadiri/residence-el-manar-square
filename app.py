import streamlit as st
import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from supabase import create_client
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os


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

# دالة جلب بيانات الاشتراكات وتصحيحها أوتوماتيكياً
def load_data():
    try:
        response = supabase.table("residents").select("*").execute()

        if response.data:
            df = pd.DataFrame(response.data)

            df = df.rename(columns={
                "immeuble": "Immeuble / الإقامة",
                "appartement": "Appartement / الشقة",
                "nom_complet": "Nom et prénom / الاسم الكامل",
                "telephone": "Téléphone / الهاتف",
                "annee": "Année / السنة",
                "janvier": "Janvier",
                "fevrier": "Février",
                "mars": "Mars",
                "avril": "Avril",
                "mai": "Mai",
                "juin": "Juin",
                "juillet": "Juillet",
                "aout": "Août",
                "septembre": "Septembre",
                "octobre": "Octobre",
                "novembre": "Novembre",
                "decembre": "Décembre"
            })

            return df

        return pd.DataFrame(columns=[
            "Immeuble / الإقامة",
            "Appartement / الشقة",
            "Nom et prénom / الاسم الكامل",
            "Téléphone / الهاتف",
            "Année / السنة",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre"
        ])

    except Exception as e:
        st.error(f"Erreur chargement residents : {e}")
        return pd.DataFrame()

# دالة ذكية ومصححة لجلب المصاريف وإضافة أعمدة السنة والشهر تلقائياً إذا كانت ناقصة
def load_expenses():
    try:
        response = supabase.table("expenses").select("*").execute()

        if response.data:
            df_exp = pd.DataFrame(response.data)
            return df_exp

        return pd.DataFrame(columns=[
            "date",
            "annee",
            "mois",
            "mode_de_paiment",
            "categorie",
            "designation",
            "depense"
        ])

    except Exception as e:
        st.error(f"Erreur chargement dépenses : {e}")
        return pd.DataFrame()
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
df = load_data()
df_expenses = load_expenses()

# 2. تهيئة الحالة الأساسية
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# 3. منطق تسجيل الدخول
if st.session_state.user_name is None:
    st.markdown("<h1 style='text-align: center;'>🔐 Résidence El Manar Square</h1>", unsafe_allow_html=True)
    input_name = st.text_input("أدخل اسمك الكامل / Entrez votre nom complet:")
    
    if st.button("دخول / Connexion"):
        input_name_clean = input_name.strip().lower()
        
        if input_name_clean == "admin":
            st.session_state.user_name = "Admin"
            st.rerun()
        elif input_name_clean:
            try:
                # البحث في Supabase (بحث جزئي)
                search_query = f"%{input_name_clean}%"
                response = supabase.table("residents").select("nom_complet").ilike("nom_complet", search_query).execute()
                
                if response.data:
                    # نأخذ أول نتيجة مطابقة
                    st.session_state.user_name = response.data[0]['nom_complet']
                    st.rerun()
                else:
                    st.error("الاسم غير موجود أو خطأ في الكتابة!")
            except Exception as e:
                st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        else:
            st.warning("الرجاء إدخال اسم.")
            
    st.stop() # إيقاف الكود هنا إذا لم يسجل المستخدم دخوله

# 4. بعد تسجيل الدخول، نحدد صلاحية الأدمن
is_admin = (st.session_state.user_name == "Admin")

# 5. البانر وزر الخروج
st.markdown(f'''
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">
        🏢 Résidence El Manar Square - Espace: {st.session_state.user_name}
    </div>
''', unsafe_allow_html=True)

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
    
    # 1. جلب السنوات المتاحة (تأكد أن العمود سميتو "Année / السنة")
    years_list = sorted(df["Année / السنة"].dropna().unique().astype(str).tolist())
    selected_year = st.selectbox("اختر السنة / Sélectionnez l'année", years_list)
    
    # 2. منطق الأدمن
    if is_admin:
        sel_imm_dash = st.selectbox("Filtrer par Immeuble", ["Tous"] + immeubles_list)
        df_dash = df.copy()
        df_dash = df_dash[df_dash["Année / السنة"].astype(str) == selected_year]
        
        if sel_imm_dash != "Tous":
            df_dash = df_dash[df_dash["Immeuble / الإقامة"] == sel_imm_dash]
        
        columns_to_show_admin = ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف"]
        st.dataframe(df_dash[columns_to_show_admin], use_container_width=True, hide_index=True, height=750)
    
    # 3. منطق المستخدم العادي
    else:
        # البحث عن اسم المستخدم في Supabase-based DataFrame
        df_user = df[df["Nom et prénom / الاسم الكامل"].str.contains(st.session_state.user_name, case=False, na=False)]
        df_user = df_user[df_user["Année / السنة"].astype(str) == selected_year]
        
        columns_to_show = ["Immeuble / الإقامة", "Appartement / الشقة", "Nom et prénom / الاسم الكامل", "Téléphone / الهاتف"]
        
        if not df_user.empty:
            st.dataframe(df_user[columns_to_show], use_container_width=True, hide_index=True)
        else:
            st.warning("لا توجد بيانات مسجلة باسمك لهذه السنة.")
elif st.session_state.current_page == "Cotisations":
    st.subheader("💵 Situation des paiements de l'année" if langue == "Français" else "💵 وضعية الاشتراكات السنوية")        
    
    # دالة تحويل القيم (✅ و ❌) للعرض فقط
    def format_payment(val):
        val_str = str(val).strip().upper()
        if val_str in ['PAYE', 'PAYÉ']: return '✅'
        if val_str == 'NON_PAYE': return '❌'
        return val

    # --- الجزء الخاص بالأدمن ---
if is_admin:

    row1, row2 = st.columns(2), st.columns(2)

    with row1[0]:
        selected_year = st.selectbox(
            "Année / السنة",
            sorted(df["Année / السنة"].unique())
        )

    with row1[1]:
        months_list = ["الكل"] + months_cols
        selected_month = st.selectbox(
            "Mois / الشهر",
            months_list
        )

    with row2[0]:
        selected_imm = st.selectbox(
            "Immeuble / الإقامة",
            sorted(df["Immeuble / الإقامة"].unique())
        )

    with row2[1]:
        filtered_apparts = df[
            df["Immeuble / الإقامة"] == selected_imm
        ]["Appartement / الشقة"].unique().tolist()

        apparts_in_imm = ["الكل"] + sorted(filtered_apparts)

        selected_appart = st.selectbox(
            "Appartement / الشقة",
            apparts_in_imm
        )

    st.markdown("---")

    mask = (
        (df["Année / السنة"].astype(str) == str(selected_year))
        &
        (df["Immeuble / الإقامة"] == selected_imm)
    )

    if selected_appart != "الكل":
        mask &= (
            df["Appartement / الشقة"] == selected_appart
        )

    df_filtered = df[mask].copy()

    if df_filtered.empty:
        st.warning("لا توجد بيانات تطابق الاختيارات.")

    else:

        cols_to_display = [
            "id",
            "Immeuble / الإقامة",
            "Appartement / الشقة",
            "Nom et prénom / الاسم الكامل",
            "Téléphone / الهاتف",
            "Année / السنة"
        ] + (
            months_cols
            if selected_month == "الكل"
            else [selected_month]
        )

        df_display = df_filtered[cols_to_display].copy()

        for month in months_cols:
            if month in df_display.columns:
                df_display[month] = (
                    df_display[month]
                    .replace("PAYÉ", "PAYE")
                    .fillna("NON_PAYE")
                )

        edited_df = st.data_editor(
            df_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                month: st.column_config.SelectboxColumn(
                    month,
                    options=["PAYE", "NON_PAYE"]
                )
                for month in months_cols
                if month in df_display.columns
            },
            disabled=[
                "id",
                "Immeuble / الإقامة",
                "Appartement / الشقة",
                "Nom et prénom / الاسم الكامل",
                "Téléphone / الهاتف",
                "Année / السنة"
            ]
        )

        if st.button(
            "💾 Enregistrer les modifications",
            use_container_width=True
        ):

            month_map = {
                "Janvier": "janvier",
                "Février": "fevrier",
                "Mars": "mars",
                "Avril": "avril",
                "Mai": "mai",
                "Juin": "juin",
                "Juillet": "juillet",
                "Août": "aout",
                "Septembre": "septembre",
                "Octobre": "octobre",
                "Novembre": "novembre",
                "Décembre": "decembre"
            }

            try:

                for _, row in edited_df.iterrows():

                    resident_id = row["id"]

                    updates = {}

                    for month_fr, month_db in month_map.items():

                        if month_fr in edited_df.columns:

                            value = str(row[month_fr]).strip()

                            if value == "PAYE":
                                updates[month_db] = "PAYE"
                            else:
                                updates[month_db] = "NON_PAYE"

                    if updates:

                        supabase.table("residents") \
                            .update(updates) \
                            .eq("id", resident_id) \
                            .execute()

                st.success("✅ Modifications enregistrées avec succès")
                st.rerun()

            except Exception as e:
                st.error(f"Erreur : {e}")

    # --- الجزء الخاص بالساكن ---
        else:
        st.write("### 📋 وضعية اشتراكاتك الخاصة:")
        user_name = st.session_state.get("user_name", "")
        # استخدام الاسم الصحيح للعمود "Nom et prénom / الاسم الكامل"
        df_user_cotis = df[df["Nom et prénom / الاسم الكامل"].str.contains(user_name, case=False, na=False)].copy()
        
        if df_user_cotis.empty:
            st.info("لم يتم العثور على بيانات خاصة بك.")
        else:
            for month in months_cols:
                if month in df_user_cotis.columns:
                    df_user_cotis[month] = df_user_cotis[month].apply(format_payment)
            
            st.dataframe(df_user_cotis, use_container_width=True, hide_index=True)
# 🏦 TRÉSORERIE PAGE
elif st.session_state.current_page == "Trésorerie":
    st.subheader("🏦 Trésorerie - الوضعية المالية")

    if is_admin:
        # =========================
        # 📅 FILTERS
        # =========================
        c1, c2 = st.columns(2)
        with c1:
            tres_year = st.selectbox("Année", years_list, 
                                    index=years_list.index("2026") if "2026" in years_list else 0, 
                                    key="tres_year")
        with c2:
            tres_month_num = st.selectbox("Mois", [str(i) for i in range(1, 13)], 
                                         index=datetime.now().month - 1, 
                                         key="tres_month")
        
        st.caption(f"📅 Période: {tres_month_num}/{tres_year}")

        # =========================
        # 💰 CALCULATIONS
        # =========================
        PRIX_PAR_PAYE = 300
        solde_initial = 0.0

        all_paid = (df[months_cols].astype(str).apply(lambda col: col.str.strip().str.lower() == "paye").sum().sum())
        total_recette_all = all_paid * PRIX_PAR_PAYE
        total_depense_all = df_expenses["depense"].sum()
        solde_global = solde_initial + total_recette_all - total_depense_all

        month_name = months_cols[int(tres_month_num) - 1]
        df_year = df[df["Année / السنة"].astype(str) == str(tres_year)]
        total_recette_month = (df_year[month_name].astype(str).str.strip().str.lower().eq("paye").sum() * PRIX_PAR_PAYE)
        
        df_exp_month = df_expenses[(df_expenses["annee"].astype(str) == str(tres_year)) & (df_expenses["mois"].astype(str) == str(tres_month_num))]
        total_depense_month = df_exp_month["depense"].sum()
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
        
        with c1: kpi("💰 recettes mois", total_recette_month, "#2ecc71")
        with c2: kpi("💸 Dépenses mois", total_depense_month, "#e74c3c")
        with c3: kpi("📊 Solde mois", solde_month, "#3498db")
        with c4: kpi("🏦 Solde global", solde_global, "#8e44ad")

        st.divider()

        # ➕ ADD EXPENSE (SUPABASE INSERT)
        st.markdown("### ➕ Ajouter une dépense")
        c1, c2, c3 = st.columns(3)
        with c1: 
            mode = st.selectbox("Mode paiement", ["ESPECE", "VIREMENT", "CHEQUE", "FRAIS BANQUE"])
            cat = st.selectbox("Catégorie", ["Entretien", "Salaire", "Electricité", "PRODUIT", "Autres"])
        with c2: 
            date = st.date_input("date")
            libelle = st.text_input("Libellé")
        with c3: 
            montant = st.number_input("Montant", min_value=0.0, step=50.0)
            if st.button("✔️ Ajouter", use_container_width=True):
                if libelle and montant > 0:
                    new_exp = {
                        "date": date.strftime("%Y-%m-%d"),
                        "annee": str(tres_year),
                        "mois": str(tres_month_num),
                        "mode_de_paiement": mode,
                        "categorie": cat.upper(),
                        "designation": libelle,
                        "depense": float(montant)
                    }
                    
                    # محاولة الإضافة مع التقاط الخطأ بالتفصيل
                    try:
                        response = supabase.table("expenses").insert(new_exp).execute()
                        st.success("✔️ Ajouté à Supabase!")
                        st.rerun()
                    except Exception as e:
                        # هذا السطر هو اللي غادي يوريك المشكل الحقيقي
                        st.error(f"Erreur Supabase: {e}")
                else:
                    st.warning("الرجاء ملء جميع الخانات بشكل صحيح.")
        st.markdown("### 📋 Opérations")
        df_display = df_exp_month.copy()
        if not df_display.empty:
            df_display["depense"] = pd.to_numeric(df_display["depense"], errors="coerce").fillna(0)
            df_display["recette"] = 0.0
            df_display["date"] = pd.to_datetime(df_display["date"], errors="coerce")
            df_display = df_display.sort_values("date", ascending=False)
            df_display["date"] = df_display["date"].dt.strftime("%Y-%m-%d")
            resume = pd.DataFrame([{"date": "", "mode_de_paiement": "", "categorie": "RÉSUMÉ", "designation": "🟢 TOTAL recetteS", "depense": 0, "recette": total_recette_month}])
            df_final = pd.concat([resume, df_display], ignore_index=True)
            st.dataframe(df_final, use_container_width=True, hide_index=True)

        # 📊 GRAPH
        st.markdown(f"### 📈 Évolution des recettes et dépenses pour l'année {tres_year}")
        recettes_list, depenses_list = [], []
        for m in range(1, 13):
            m_col = months_cols[m-1]
            recette = (df_year[m_col].astype(str).str.strip().str.lower().eq("paye").sum() * 300)
            recettes_list.append(recette)
            # استخدمي الأسماء العربية التي تظهر في أعمدة جدولك
            exp_m = df_expenses[(df_expenses["annee"].astype(str) == str(tres_year)) & (df_expenses["mois"].astype(str) == str(m))]
            depenses_list.append(exp_m["depense"].sum())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months_cols, y=recettes_list, mode='lines+markers', name='recettes', line=dict(color='#f39c12', width=5)))
        fig.add_trace(go.Scatter(x=months_cols, y=depenses_list, mode='lines+markers', name='Dépenses', line=dict(color='#e74c3c', width=5)))
        fig.update_layout(xaxis_title="Mois", yaxis_title="Montant (MAD)", plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # 💾 PDF
        st.markdown("### 📄 Rapport PDF")
        if st.button("Créer PDF"):
            file_name = f"rapport_{tres_year}_{tres_month_num}.pdf"
            doc = SimpleDocTemplate(file_name, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [Paragraph("<b>Rapport de Trésorerie</b>", styles["Title"]), Spacer(1, 12)]
            data = [["Désignation", "Montant (MAD)"], ["Total recettes", f"{total_recette_month:,.2f}"], ["Total Dépenses", f"{total_depense_month:,.2f}"], ["Solde Final", f"{solde_month:,.2f}"]]
            table = Table(data, colWidths=[250, 150])
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.lightgrey), ('GRID', (0, 0), (-1, -1), 1, colors.black), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')]))
            elements.append(table)
            doc.build(elements)
            st.success("Pgénéré !")
            st.rerun()

        if os.path.exists(f"rapport_{tres_year}_{tres_month_num}.pdf"):
            with open(f"rapport_{tres_year}_{tres_month_num}.pdf", "rb") as f:
                st.download_button("⬇️ Télécharger PDF", f, file_name=f"rapport_{tres_year}_{tres_month_num}.pdf", mime="application/pdf")

    else:
        st.warning("⚠️ هذه الصفحة مخصصة للمدير فقط.")
