import streamlit as st
import sqlite3

# --- 1. تجهيز قاعدة البيانات المحلية ---
def init_db():
    conn = sqlite3.connect("smart_store.db", check_same_thread=False)
    cursor = conn.cursor()
    # جدول المنتجات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        quantity INTEGER,
        fixed_capital REAL,
        selling_price REAL
    )
    """)
    # جدول المحافظ الماليّة للشركاء
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

# دالة حساب رأس المال
def calculate_capital(price_yuan, weight, pack_cost, bag_cost, dollar_rate, shipping_rate):
    product_cost_lyd = (price_yuan * 0.14) * dollar_rate
    shipping_cost_lyd = (weight * shipping_rate) * dollar_rate
    return round(product_cost_lyd + shipping_cost_lyd + pack_cost + bag_cost, 2)

# --- 2. نظام تسجيل الدخول بالرموز السحرية ---
st.set_page_config(page_title="Ranim Store Secure", page_icon="🔒", layout="wide")

# الرموز الخاصة بالدخول (يمكنك تعديلها هنا بحرية)
USER_TOKENS = {
    "B2026": "Bashir",  # الرمز السري الخاص ببشير
    "A2026": "Ahmed"    # الرمز السري الخاص بأحمد
}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# إذا لم يسجل الدخول، تظهر شاشة القفل أولاً
if st.session_state["logged_in_user"] is None:
    st.subheader("🔒 نظام إدارة متجر رنيم الآمن")
    token_input = st.text_input("أدخل الرمز السري الخاص بك للدخول للمنظومة:", type="password")
    
    if st.button("تسجيل الدخول"):
        if token_input in USER_TOKENS:
            st.session_state["logged_in_user"] = USER_TOKENS[token_input]
            st.success(f"مرحباً بك يا {st.session_state['logged_in_user']}، تم التحقق بنجاح!")
            st.rerun()
        else:
            st.error("الرمز السري غير صحيح! لا يمكن الدخول.")
else:
    # تم الدخول بنجاح، هنا يبدأ الموقع الفعلي
    current_user = st.session_state["logged_in_user"]
    
    # زر الخروج في أعلى القائمة الجانبية
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["logged_in_user"] = None
        st.rerun()

    st.title("📦 لوحة تحكم متجر رنيم")
    st.markdown(f"👤 المستخدم الحالي: **{current_user}** | المنظومة مؤمنة بالكامل.")

    # القائمة الجانبية للتنقل
    menu = ["لوحة التحكم والمحافظ", "إضافة وتحديث البضاعة", "تسجيل عملية بيع", "الاستعلام عن منتج"]
    choice = st.sidebar.selectbox(" قائمة التحكم", menu)

    # --- القسم الأول: لوحة التحكم والمحافظ ---
    if choice == "لوحة التحكم والمحافظ":
        st.header("👥 الحسابات المالية للشركاء")
        
        cursor.execute("SELECT partner_name, balance FROM wallets")
        wallets = {row[0]: row[1] for row in cursor.fetchall()}
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="محفظة أرباح بشير", value=f"{wallets.get('Bashir', 0.0)} د.ل")
        with col2:
            st.metric(label="محفظة أرباح أحمد", value=f"{wallets.get('Ahmed', 0.0)} د.ل")
            
        st.divider()
        st.subheader(f"💸 سحب أموال من محفظتك ({current_user})")
        st.warning(f"ملاحظة: أنت الآن تسحب مباشرة من حسابك كـ {current_user} فقط.")
        
        withdraw_amount = st.number_input("المبلغ المراد سحبه (دينار)", min_value=0.0, step=1.0)
        
        if st.button("تأكيد عملية السحب"):
            current_bal = wallets.get(current_user, 0.0)
            if withdraw_amount > current_bal:
                st.error("رصيد أرباحك غير كافٍ! المتاح أقل من المطلوب.")
            elif withdraw_amount <= 0:
                st.warning("الرجاء إدخال مبلغ أكبر من الصفر.")
            else:
                new_bal = round(current_bal - withdraw_amount, 2)
                cursor.execute("UPDATE wallets SET balance = ? WHERE partner_name = ?", (new_bal, current_user))
                conn.commit()
                st.success(f"تم سحب {withdraw_amount} د.ل بنجاح من محفظتك يا {current_user}!")
                st.rerun()

    # --- القسم الثاني: إضافة وتحديث البضاعة ---
    elif choice == "إضافة وتحديث البضاعة":
        st.header("🛒 إدارة المخزون والبضائع القادمة")
        p_name = st.text_input("اسم المنتج").strip()
        
        if p_name:
            cursor.execute("SELECT id, quantity, fixed_capital, selling_price FROM products WHERE name = ?", (p_name,))
            existing = cursor.fetchone()
            
            if existing:
                st.warning(f"هذا المنتج موجود مسبقاً! رقم التعريف: {existing[0]} | الكمية الحالية: {existing[1]}")
                
            qty = st.number_input("الكمية الجديدة", min_value=1, step=1)
            price_yuan = st.number_input("سعر الشراء من الصين (باليوان)", min_value=0.0, step=0.5)
            weight = st.number_input("وزن القطعة الواحدة (كيلو)", min_value=0.0, step=0.05)
            pack_cost = st.number_input("تكلفة التغليف للقطعة (بالدينار)", min_value=0.0, step=0.5)
            bag_cost = st.number_input("تكلفة الكيس المطبوع للقطعة (بالدينار)", min_value=0.0, step=0.5)
            dollar_rate = st.number_input("سعر دولار السوق الموازي الحالي", min_value=0.0, value=7.1, step=0.05)
            shipping_rate = st.number_input("تكلفة الشحن لكل كيلو ($)", min_value=0.0, value=12.5, step=0.5)
            
            if price_yuan > 0:
                calculated_cap = calculate_capital(price_yuan, weight, pack_cost, bag_cost, dollar_rate, shipping_rate)
                st.info(f"💡 تكلفة رأس المال للقطعة: {calculated_cap} د.ل")
                st.success(f"📈 مقترح سعر البيع العادل: {round(calculated_cap*1.3)} - {round(calculated_cap*1.7)} د.ل")
                
            selling_price = st.number_input("سعر البيع المعتمد للجمهور (بالدينار)", min_value=0.0, step=1.0)
            
            if st.button("حفظ المنتج في المنظومة"):
                if existing:
                    total_qty = existing[1] + qty
                    cursor.execute("UPDATE products SET quantity=?, fixed_capital=?, selling_price=? WHERE id=?", (total_qty, calculated_cap, selling_price, existing[0]))
                else:
                    cursor.execute("INSERT INTO products (name, quantity, fixed_capital, selling_price) VALUES (?, ?, ?, ?)", (p_name, qty, calculated_cap, selling_price))
                conn.commit()
                st.success("تم تحديث المخزون وحفظ البيانات بنجاح!")

    # --- القسم الثالث: تسجيل عملية بيع ---
    elif choice == "تسجيل عملية بيع":
        st.header("💰 تسجيل فاتورة بيع جديدة")
        p_id = st.number_input("أدخل الرقم التعريفي للمنتج (ID)", min_value=1, step=1)
        qty_to_sell = st.number_input("الكمية المباعة", min_value=1, step=1)
        
        if st.button("إتمام عملية البيع"):
            cursor.execute("SELECT name, quantity, fixed_capital, selling_price FROM products WHERE id = ?", (p_id,))
            product = cursor.fetchone()
            
            if not product:
                st.error("عذراً، هذا الرقم التعريفي غير موجود في المخزن.")
            elif product[1] < qty_to_sell:
                st.error(f"الكمية غير كافية! المتوفر هو {product[1]} قطع فقط.")
            else:
                name, current_qty, capital, price = product
                total_before_discount = price * qty_to_sell
                discount = round(total_before_discount * 0.05, 2) if qty_to_sell >= 2 else 0.0
                
                final_total = total_before_discount - discount
                total_capital_cost = capital * qty_to_sell
                net_profit = round(final_total - total_capital_cost, 2)
                
                if final_total < total_capital_cost:
                    st.error("فشلت العملية: قيمة الخصم تلتهم رأس المال!")
                else:
                    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (current_qty - qty_to_sell, p_id))
                    share = round(net_profit / 2, 2)
                    if share > 0:
                        cursor.execute("UPDATE wallets SET balance = balance + ? WHERE partner_name = 'Bashir'", (share,))
                        cursor.execute("UPDATE wallets SET balance = balance + ? WHERE partner_name = 'Ahmed'", (share,))
                    conn.commit()
                    
                    st.success(f"✓ تمت عملية البيع! صافي الربح: {net_profit} د.ل. تم إضافة {share} د.ل لكل محفظة.")
                    if (current_qty - qty_to_sell) <= 3:
                        st.warning(f"🚨 المتبقي في المخزن {current_qty - qty_to_sell} قطع فقط.")

    # --- القسم الرابع: الاستعلام عن منتج ---
    elif choice == "الاستعلام عن منتج":
        st.header("🔍 الاستعلام عن تفاصيل منتج")
        search_id = st.number_input("أدخل رقم المنتج للبحث عنه", min_value=1, step=1)
        
        if st.button("بحث"):
            cursor.execute("SELECT name, quantity, fixed_capital, selling_price FROM products WHERE id = ?", (search_id,))
            prod = cursor.fetchone()
            if prod:
                st.write(f"**اسم المنتج:** {prod[0]}")
                st.write(f"**الكمية المتوفرة:** {prod[1]} قطع")
                st.write(f"**تكلفة رأس المال للقطعة:** {prod[2]} د.ل")
                st.write(f"**سعر البيع:** {prod[3]} د.ل")
            else:
                st.error("لم يتم العثور على المنتج.")