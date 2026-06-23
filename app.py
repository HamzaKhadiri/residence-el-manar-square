import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

# قراءة البيانات مباشرة من الـ Secrets كقاموس (Dictionary)
# إعداد الصلاحيات
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# قراءة الإعدادات
creds_dict = dict(st.secrets["gcp_service_account"])

# خطوة هامة: تنظيف المفتاح
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

# الاتصال بـ Google Sheets
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# فتح الجداول
sheet_syndic = client.open("syndic_data").sheet1
sheet_expenses = client.open("expenses_data").sheet1

# فتح الجداول
sheet_syndic = client.open("syndic_data").sheet1
sheet_expenses = client.open("expenses_data").sheet1

# 3. الدوال الأساسية (للتعامل مع Google Sheets)
def load_data():
    return pd.DataFrame(sheet_syndic.get_all_records())

def save_data(df):
    sheet_syndic.clear()
    sheet_syndic.update([df.columns.tolist()] + df.fillna("").values.tolist())

def load_expenses():
    return pd.DataFrame(sheet_expenses.get_all_records())

def save_expenses(df_expenses):
    sheet_expenses.clear()
    sheet_expenses.update([df_expenses.columns.tolist()] + df_expenses.fillna("").values.tolist())

