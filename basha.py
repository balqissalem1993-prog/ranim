# =========================================
# منظومة متجر رنيم — النسخة المستقرة
# تعمل على قاعدة البيانات القديمة بدون مشاكل
# =========================================

import streamlit as st
import sqlite3

# =========================================
# إعداد الصفحة
# =========================================

st.set_page_config(
    page_title="Ranim Store",
    page_icon="🛍️",
    layout="wide"
)

# =========================================
# تحسين الشكل
# =========================================

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
}

.stMetric {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
}

div.stButton > button {
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}

h1, h2, h3 {
    color: #111827;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# قاعدة البيانات
# =========================================

def init_db():

    conn = sqlite3.connect(
        "smart_store.db",
        check_same_thread=False
    )

    cursor = conn.cursor()

    # =====================================
    # جدول المنتجات
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        quantity INTEGER,
        fixed_capital REAL,
        selling_price REAL
    )
    """)

    # =====================================
    # المحافظ (النظام القديم)
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        partner_name TEXT PRIMARY KEY,
        balance REAL
    )
    """)

    # =====================================
    # خزائن رأس المال
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capital_accounts (
        account_type TEXT PRIMARY KEY,
        balance REAL
    )
    """)

    # =====================================
    # العمليات
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER,
        total REAL,
        profit REAL,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =====================================
    # السجل المالي
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT,
        account_type TEXT,
        amount REAL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =====================================
    # المحافظ الافتراضية
    # =====================================

    cursor.execute("""
    INSERT OR IGNORE INTO wallets
    (partner_name, balance)
    VALUES ('Bashir', 0)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO wallets
    (partner_name, balance)
    VALUES ('Ahmed', 0)
    """)

    # =====================================
    # خزائن افتراضية
    # =====================================

    cursor.execute("""
    INSERT OR IGNORE INTO capital_accounts
    VALUES ('cash', 0)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO capital_accounts
    VALUES ('bank', 0)
    """)

    conn.commit()

    return conn


conn = init_db()
cursor = conn.cursor()

# =========================================
# حساب رأس المال
# =========================================

def calculate_capital(
    price_yuan,
    weight,
    pack_cost,
    bag_cost,
    dollar_rate,
    shipping_rate
):

    product_cost_lyd = (
        price_yuan * 0.14
    ) * dollar_rate

    shipping_cost_lyd = (
        weight * shipping_rate
    ) * dollar_rate

    total = (
        product_cost_lyd
        + shipping_cost_lyd
        + pack_cost
        + bag_cost
    )

    return round(total, 2)

# =========================================
# تسجيل الدخول
# =========================================

if "user_tokens" not in st.session_state:

    st.session_state["user_tokens"] = {
        "B2026": "Bashir",
        "A2026": "Ahmed"
    }

USER_TOKENS = st.session_state["user_tokens"]

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# =========================================
# واجهة الدخول
# =========================================

if st.session_state["logged_in_user"] is None:

    st.markdown("""
    <div style='text-align:center;padding:40px'>
        <h1>🛍️ منظومة متجر رنيم</h1>
        <h3>نظام إدارة المخزون والمحاسبة</h3>
    </div>
    """, unsafe_allow_html=True)

    token_input = st.text_input(
        "🔒 الرمز السري",
        type="password"
    )

    if st.button("تسجيل الدخول"):

        if token_input in USER_TOKENS:

            st.session_state[
                "logged_in_user"
            ] = USER_TOKENS[token_input]

            st.success("تم تسجيل الدخول")

            st.rerun()

        else:
            st.error("الرمز غير صحيح")

# =========================================
# داخل النظام
# =========================================

else:

    current_user = st.session_state[
        "logged_in_user"
    ]

    # =====================================
    # القائمة الجانبية
    # =====================================

    st.sidebar.title("⚙️ لوحة التحكم")

    st.sidebar.success(
        f"مرحباً {current_user}"
    )

    if st.sidebar.button("🚪 تسجيل الخروج"):

        st.session_state[
            "logged_in_user"
        ] = None

        st.rerun()

    menu = [
        "الرئيسية",
        "الخزائن والمحافظ",
        "إضافة وتحديث البضاعة",
        "تسجيل عملية بيع",
        "الاستعلام عن منتج",
        "سجل العمليات",
        "السجل المالي"
    ]

    choice = st.sidebar.selectbox(
        "القائمة",
        menu
    )

    # =====================================
    # الرئيسية
    # =====================================

    if choice == "الرئيسية":

        st.title("🛍️ مرحباً بك في متجر رنيم")

        st.caption(
            "نظام احترافي لإدارة البضائع والأرباح"
        )

        # المحافظ
        cursor.execute("""
        SELECT partner_name, balance
        FROM wallets
        """)

        wallets = {
            row[0]: row[1]
            for row in cursor.fetchall()
        }

        # الخزائن
        cursor.execute("""
        SELECT account_type, balance
        FROM capital_accounts
        """)

        capitals = {
            row[0]: row[1]
            for row in cursor.fetchall()
        }

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "💵 خزنة الكاش",
                f"{capitals.get('cash',0)} د.ل"
            )

        with col2:
            st.metric(
                "🏦 خزنة المصرف",
                f"{capitals.get('bank',0)} د.ل"
            )

        st.divider()

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "👤 أرباح بشير",
                f"{wallets.get('Bashir',0)} د.ل"
            )

        with c2:
            st.metric(
                "👤 أرباح أحمد",
                f"{wallets.get('Ahmed',0)} د.ل"
            )

    # =====================================
    # الخزائن والمحافظ
    # =====================================

    elif choice == "الخزائن والمحافظ":

        st.header("💰 إدارة الأموال")

        # تعديل المحافظ

        st.subheader("👥 تعديل المحافظ")

        partner = st.selectbox(
            "الشريك",
            ["Bashir", "Ahmed"]
        )

        new_balance = st.number_input(
            "الرصيد الجديد",
            min_value=0.0,
            step=1.0
        )

        if st.button("حفظ المحفظة"):

            cursor.execute("""
            UPDATE wallets
            SET balance = ?
            WHERE partner_name = ?
            """, (
                new_balance,
                partner
            ))

            conn.commit()

            st.success("تم تحديث المحفظة")

        st.divider()

        # تعديل الخزائن

        st.subheader("🏦 تعديل الخزائن")

        capital_type = st.selectbox(
            "نوع الخزنة",
            ["cash", "bank"]
        )

        capital_balance = st.number_input(
            "الرصيد",
            min_value=0.0,
            step=1.0,
            key="capital"
        )

        if st.button("حفظ الخزنة"):

            cursor.execute("""
            UPDATE capital_accounts
            SET balance = ?
            WHERE account_type = ?
            """, (
                capital_balance,
                capital_type
            ))

            conn.commit()

            st.success("تم تعديل الخزنة")

        st.divider()

        # تغيير الرمز

        st.subheader("🔑 تغيير الرمز السري")

        old_token = st.text_input(
            "الرمز الحالي",
            type="password"
        )

        new_token = st.text_input(
            "الرمز الجديد",
            type="password"
        )

        if st.button("تغيير الرمز"):

            found = False

            for token, user in list(USER_TOKENS.items()):

                if (
                    user == current_user
                    and token == old_token
                ):

                    del USER_TOKENS[token]

                    USER_TOKENS[
                        new_token
                    ] = current_user

                    st.success(
                        "تم تغيير الرمز"
                    )

                    found = True

                    break

            if not found:
                st.error("الرمز الحالي خطأ")

    # =====================================
    # إضافة بضاعة
    # =====================================

    elif choice == "إضافة وتحديث البضاعة":

        st.header("📦 إدارة المخزون")

        p_name = st.text_input(
            "اسم المنتج"
        ).strip()

        if p_name:

            cursor.execute("""
            SELECT id, quantity
            FROM products
            WHERE name = ?
            """, (p_name,))

            existing = cursor.fetchone()

            if existing:

                st.warning(
                    f"المنتج موجود | ID: {existing[0]}"
                )

            qty = st.number_input(
                "الكمية",
                min_value=1,
                step=1
            )

            price_yuan = st.number_input(
                "السعر باليوان",
                min_value=0.0,
                step=0.5
            )

            weight = st.number_input(
                "الوزن",
                min_value=0.0,
                step=0.05
            )

            pack_cost = st.number_input(
                "التغليف",
                min_value=0.0,
                step=0.5
            )

            bag_cost = st.number_input(
                "الكيس",
                min_value=0.0,
                step=0.5
            )

            dollar_rate = st.number_input(
                "الدولار",
                value=7.1,
                step=0.05
            )

            shipping_rate = st.number_input(
                "الشحن",
                value=12.5,
                step=0.5
            )

            purchase_source = st.radio(
                "مصدر الشراء",
                ["cash", "bank"]
            )

            calculated_cap = 0

            if price_yuan > 0:

                calculated_cap = calculate_capital(
                    price_yuan,
                    weight,
                    pack_cost,
                    bag_cost,
                    dollar_rate,
                    shipping_rate
                )

                st.info(
                    f"رأس المال: {calculated_cap} د.ل"
                )

            selling_price = st.number_input(
                "سعر البيع",
                min_value=0.0,
                step=1.0
            )

            if st.button("حفظ المنتج"):

                total_cost = (
                    calculated_cap * qty
                )

                # خصم من الخزنة

                cursor.execute("""
                SELECT balance
                FROM capital_accounts
                WHERE account_type = ?
                """, (purchase_source,))

                current_balance = cursor.fetchone()[0]

                if total_cost > current_balance:

                    st.error(
                        "الرصيد غير كافي"
                    )

                else:

                    new_balance = (
                        current_balance - total_cost
                    )

                    cursor.execute("""
                    UPDATE capital_accounts
                    SET balance = ?
                    WHERE account_type = ?
                    """, (
                        new_balance,
                        purchase_source
                    ))

                    if existing:

                        cursor.execute("""
                        UPDATE products
                        SET quantity = quantity + ?,
                            fixed_capital = ?,
                            selling_price = ?
                        WHERE id = ?
                        """, (
                            qty,
                            calculated_cap,
                            selling_price,
                            existing[0]
                        ))

                    else:

                        cursor.execute("""
                        INSERT INTO products
                        (
                            name,
                            quantity,
                            fixed_capital,
                            selling_price
                        )
                        VALUES (?, ?, ?, ?)
                        """, (
                            p_name,
                            qty,
                            calculated_cap,
                            selling_price
                        ))

                    # سجل مالي

                    cursor.execute("""
                    INSERT INTO financial_logs
                    (
                        action_type,
                        account_type,
                        amount,
                        note
                    )
                    VALUES (?, ?, ?, ?)
                    """, (
                        "شراء بضاعة",
                        purchase_source,
                        -total_cost,
                        p_name
                    ))

                    conn.commit()

                    st.success(
                        "تم حفظ المنتج"
                    )

        st.divider()

        # حذف منتج

        st.subheader("🗑️ حذف منتج")

        delete_id = st.number_input(
            "رقم المنتج للحذف",
            min_value=1,
            step=1
        )

        if st.button("حذف المنتج"):

            cursor.execute("""
            SELECT name
            FROM products
            WHERE id = ?
            """, (delete_id,))

            found = cursor.fetchone()

            if found:

                cursor.execute("""
                DELETE FROM products
                WHERE id = ?
                """, (delete_id,))

                conn.commit()

                st.success(
                    f"تم حذف {found[0]}"
                )

            else:
                st.error("المنتج غير موجود")

    # =====================================
    # البيع
    # =====================================

    elif choice == "تسجيل عملية بيع":

        st.header("💵 تسجيل عملية بيع")

        p_id = st.number_input(
            "رقم المنتج",
            min_value=1,
            step=1
        )

        qty_to_sell = st.number_input(
            "الكمية",
            min_value=1,
            step=1
        )

        payment_method = st.radio(
            "طريقة الدفع",
            ["cash", "bank"]
        )

        if st.button("إتمام البيع"):

            cursor.execute("""
            SELECT
                name,
                quantity,
                fixed_capital,
                selling_price
            FROM products
            WHERE id = ?
            """, (p_id,))

            product = cursor.fetchone()

            if not product:

                st.error("المنتج غير موجود")

            else:

                name = product[0]
                current_qty = product[1]
                capital = product[2]
                price = product[3]

                if current_qty < qty_to_sell:

                    st.error(
                        "الكمية غير كافية"
                    )

                else:

                    total_sale = (
                        price * qty_to_sell
                    )

                    total_capital = (
                        capital * qty_to_sell
                    )

                    net_profit = round(
                        total_sale - total_capital,
                        2
                    )

                    # تحديث الكمية

                    cursor.execute("""
                    UPDATE products
                    SET quantity = ?
                    WHERE id = ?
                    """, (
                        current_qty - qty_to_sell,
                        p_id
                    ))

                    # إرجاع رأس المال للخزنة

                    cursor.execute("""
                    SELECT balance
                    FROM capital_accounts
                    WHERE account_type = ?
                    """, (payment_method,))

                    current_balance = cursor.fetchone()[0]

                    new_balance = (
                        current_balance + total_capital
                    )

                    cursor.execute("""
                    UPDATE capital_accounts
                    SET balance = ?
                    WHERE account_type = ?
                    """, (
                        new_balance,
                        payment_method
                    ))

                    # توزيع الربح

                    share = round(
                        net_profit / 2,
                        2
                    )

                    cursor.execute("""
                    UPDATE wallets
                    SET balance = balance + ?
                    WHERE partner_name = 'Bashir'
                    """, (share,))

                    cursor.execute("""
                    UPDATE wallets
                    SET balance = balance + ?
                    WHERE partner_name = 'Ahmed'
                    """, (share,))

                    # تسجيل العملية

                    cursor.execute("""
                    INSERT INTO transactions
                    (
                        product_name,
                        quantity,
                        total,
                        profit,
                        payment_method
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """, (
                        name,
                        qty_to_sell,
                        total_sale,
                        net_profit,
                        payment_method
                    ))

                    # السجل المالي

                    cursor.execute("""
                    INSERT INTO financial_logs
                    (
                        action_type,
                        account_type,
                        amount,
                        note
                    )
                    VALUES (?, ?, ?, ?)
                    """, (
                        "بيع",
                        payment_method,
                        total_sale,
                        name
                    ))

                    conn.commit()

                    st.success(
                        f"تم البيع | الربح {net_profit}"
                    )

    # =====================================
    # الاستعلام
    # =====================================

    elif choice == "الاستعلام عن منتج":

        st.header("🔍 البحث عن منتج")

        search_id = st.number_input(
            "رقم المنتج",
            min_value=1,
            step=1
        )

        if st.button("بحث"):

            cursor.execute("""
            SELECT *
            FROM products
            WHERE id = ?
            """, (search_id,))

            prod = cursor.fetchone()

            if prod:

                st.write(
                    f"📦 الاسم: {prod[1]}"
                )

                st.write(
                    f"📦 الكمية: {prod[2]}"
                )

                st.write(
                    f"💰 رأس المال: {prod[3]}"
                )

                st.write(
                    f"💵 سعر البيع: {prod[4]}"
                )

            else:
                st.error("غير موجود")

    # =====================================
    # سجل العمليات
    # =====================================

    elif choice == "سجل العمليات":

        st.header("📑 سجل المبيعات")

        cursor.execute("""
        SELECT
            product_name,
            quantity,
            total,
            profit,
            payment_method,
            created_at
        FROM transactions
        ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        if rows:

            for row in rows:

                st.info(
                    f'''
                    🛒 المنتج: {row[0]}
                    
                    📦 الكمية: {row[1]}
                    
                    💰 الإجمالي: {row[2]} د.ل
                    
                    📈 الربح: {row[3]} د.ل
                    
                    💳 الدفع: {row[4]}
                    
                    🕒 {row[5]}
                    '''
                )

        else:
            st.info("لا توجد عمليات")

    # =====================================
    # السجل المالي
    # =====================================

    elif choice == "السجل المالي":

        st.header("📚 السجل المالي")

        cursor.execute("""
        SELECT
            action_type,
            account_type,
            amount,
            note,
            created_at
        FROM financial_logs
        ORDER BY id DESC
        """)

        logs = cursor.fetchall()

        if logs:

            for log in logs:

                st.write(
                    f'''
                    🧾 العملية: {log[0]}
                    | 💳 الحساب: {log[1]}
                    | 💰 القيمة: {log[2]}
                    | 📝 {log[3]}
                    | 🕒 {log[4]}
                    '''
                )

                st.divider()

        else:
            st.info("لا توجد سجلات")