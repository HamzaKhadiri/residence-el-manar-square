import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Résidence El Manar Square", page_icon="🏢", layout="wide")

# 2. تنسيق الـ CSS (تم دمجه وتنظيفه)
st.markdown("""
<style>
.main { background-color: #f5f7fb; }
.edary-box-card { background: #ffffff; border-radius: 20px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,.08); border-left: 5px solid #d91c23; }
.stButton>button { border-radius: 40px; font-weight: bold; height: 60px; }
[data-testid="stSidebar"] { background-color: #b5121b; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] div { color: white !important; }
[data-testid="stSidebar"] input { color: black !important; }
</style>
""", unsafe_allow_html=True)

# 3. الاتصال بـ Google Sheets
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])

# إعداد الصلاحيات
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# الاتصال بـ Google Sheets
# بما أننا استخدمنا """ في Secrets، المفتاح الآن بتنسيق صحيح ولن يحتاج لـ .replace()
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

client = get_gspread_client()
sheet_syndic = client.open("syndic_data").sheet1
sheet_expenses = client.open("expenses_data").sheet1

# 4. الدوال الأساسية
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

# مثال لبداية التطبيق
st.title("🏢 لوحة تحكم Résidence El Manar Square")
# يمكنك إضافة باقي الكود الخاص بواجهة المستخدم هنا
