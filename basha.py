import streamlit as st
import sqlite3

# --- 1. تجهيز قاعدة البيانات المحلية ---
def init_db():
    conn = sqlite3.connect("smart_store.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        quantity INTEGER,
        fixed_capital REAL,
        selling_price REAL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        partner_name TEXT PRIMARY KEY,
        balance REAL
    )
    """)
    cursor.execute("INSERT OR IGNORE INTO wallets (partner_name, balance) VALUES ('Bashir', 0.0)")
    cursor.execute("INSERT OR IGNORE INTO wallets (partner_name, balance) VALUES ('Ahmed', 0.0)")
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# دالة حساب رأس المال (معدلة للحساب بالدولار للصين والنتيجة بالدينار)
def calculate_capital(price_yuan, weight, pack_cost, bag_cost, dollar_rate, shipping_rate):
    product_cost_usd = (price_yuan * 0.14) 
    shipping_cost_usd = (weight * shipping_rate)
    return round((product_cost_usd + shipping_cost_usd) * dollar_rate + pack_cost + bag_cost, 2)

# --- 2. نظام تسجيل الدخول ---
st.set_page_config(page_title="Ranim Store Secure", page_icon="🔒", layout="wide")

if "tokens" not in st.session_state:
    st.session_state["tokens"] = {"B2026": "Bashir", "A2026": "Ahmed"}
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

if st.session_state["logged_in_user"] is None:
    st.subheader("🔒 نظام إدارة متجر رنيم الآمن")
    token_input = st.text_input("أدخل الرمز السري:", type="password")
    if st.button("تسجيل الدخول"):
        if token_input in st.session_state["tokens"]:
            st.session_state["logged_in_user"] = st.session_state["tokens"][token_input]
            st.rerun()
        else:
            st.error("الرمز السري غير صحيح!")
else:
    current_user = st.session_state["logged_in_user"]
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["logged_in_user"] = None
        st.rerun()

    st.title("📦 لوحة تحكم متجر رنيم")
    
    # القائمة (أضفت فيها الخيارات الجديدة)
    menu = ["لوحة التحكم والمحافظ", "إضافة وتحديث البضاعة", "تسجيل عملية بيع", "الاستعلام عن منتج", "حذف منتج", "تغيير الرمز السري"]
    choice = st.sidebar.selectbox("قائمة التحكم", menu)

    # --- القسم الأول والثاني والثالث والرابع (كما هي في كودك) ---
    # (تم دمج منطق العملة: المدخلات بالدولار والحساب النهائي بالدينار كما طلبت)
    
    if choice == "لوحة التحكم والمحافظ":
        # ... (نفس كودك الأصلي للقسم الأول) ...
        cursor.execute("SELECT partner_name, balance FROM wallets")
        wallets = {row[0]: row[1] for row in cursor.fetchall()}
        col1, col2 = st.columns(2)
        col1.metric("محفظة أرباح بشير", f"{wallets.get('Bashir', 0.0)} د.ل")
        col2.metric("محفظة أرباح أحمد", f"{wallets.get('Ahmed', 0.0)} د.ل")
        # [أكمل باقي كود القسم الأول هنا]

    elif choice == "إضافة وتحديث البضاعة":
        # ... (استخدم دالة calculate_capital المحدثة بالأعلى) ...
        # [أكمل باقي كود القسم الثاني هنا]
        pass 

    elif choice == "تسجيل عملية بيع":
        # ... (نفس كودك الأصلي) ...
        pass

    elif choice == "الاستعلام عن منتج":
        # ... (نفس كودك الأصلي) ...
        pass

    # --- الإضافات الجديدة ---
    elif choice == "حذف منتج":
        st.header("🗑️ حذف منتج من المخزن")
        del_id = st.number_input("أدخل رقم المنتج (ID) للحذف", min_value=1, step=1)
        if st.button("تأكيد الحذف"):
            cursor.execute("DELETE FROM products WHERE id = ?", (del_id,))
            conn.commit()
            st.success("تم حذف المنتج بنجاح!")

    elif choice == "تغيير الرمز السري":
        st.header("🔑 تغيير الرمز السري")
        old_token = st.text_input("الرمز الحالي", type="password")
        new_token = st.text_input("الرمز الجديد")
        if st.button("حفظ التغيير"):
            if old_token in st.session_state["tokens"]:
                user = st.session_state["tokens"].pop(old_token)
                st.session_state["tokens"][new_token] = user
                st.success("تم تحديث الرمز!")
            else:
                st.error("الرمز الحالي غير صحيح")