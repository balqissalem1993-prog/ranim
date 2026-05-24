import streamlit as st

st.set_page_config(page_title="نظام إدارة المتجر", layout="wide")

# إعداد البيانات الأولية
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "secret_token" not in st.session_state:
    st.session_state["secret_token"] = "b2026"  # الرمز الافتراضي
if "products" not in st.session_state:
    st.session_state["products"] = {"منتج 1": 10.0, "منتج 2": 25.0}

# شاشة الدخول
if st.session_state["logged_in_user"] is None:
    st.subheader("🔐 نظام إدارة متجر رينم الآمن")
    token_input = st.text_input("أدخل الرمز السري:", type="password")
    if st.button("تسجيل الدخول"):
        if token_input == st.session_state["secret_token"]:
            st.session_state["logged_in_user"] = "المدير"
            st.rerun()
        else:
            st.error("الرمز غير صحيح!")
else:
    st.sidebar.title("لوحة التحكم")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["logged_in_user"] = None
        st.rerun()
    
    # 1. تغيير الرمز
    with st.sidebar.expander("تغيير رمز الدخول"):
        new_token = st.text_input("الرمز الجديد")
        if st.button("حفظ الرمز"):
            st.session_state["secret_token"] = new_token
            st.success("تم تغيير الرمز بنجاح!")

    st.title("مرحباً بك في لوحة الإدارة")

    # 2. إضافة منتج
    with st.expander("إضافة منتج جديد"):
        name = st.text_input("اسم المنتج")
        price = st.number_input("السعر بالدولار ($)", min_value=0.0)
        if st.button("إضافة"):
            st.session_state["products"][name] = price
            st.success("تمت الإضافة!")

    # 3. عرض وحذف المنتجات
    st.subheader("قائمة المنتجات الحالية")
    for prod, price in list(st.session_state["products"].items()):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{prod}**")
        col2.write(f"{price} $")
        if col3.button("حذف", key=prod):
            del st.session_state["products"][prod]
            st.rerun()