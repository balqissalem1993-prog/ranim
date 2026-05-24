import streamlit as st
import sqlite3
from datetime import datetime

# =====================================
# إعداد الصفحة
# =====================================

st.set_page_config(
    page_title="Ranim Store Pro",
    page_icon="🛍",
    layout="wide"
)

# =====================================
# تصميم الواجهة
# =====================================

st.markdown("""
<style>
.main {
    background-color: #f8f9fc;
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

h1, h2, h3 {
    color: #111827;
}

div.stButton > button {
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# قاعدة البيانات
# =====================================


def init_db():
    conn = sqlite3.connect(
        "smart_store.db",
        check_same_thread=False
    )

    cursor = conn.cursor()

    # المنتجات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        quantity INTEGER,
        fixed_capital REAL,
        selling_price REAL
    )
    """)

    # محافظ الأرباح
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        partner_name TEXT,
        account_type TEXT,
        balance REAL,
        PRIMARY KEY (partner_name, account_type)
    )
    """)

    # خزائن رأس المال
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capital_accounts (
        account_type TEXT PRIMARY KEY,
        balance REAL
    )
    """)

    # سجل العمليات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        quantity INTEGER,
        total REAL,
        capital REAL,
        profit REAL,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # السجل المالي
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

    # المحافظ الافتراضية
    defaults = [
        ('Bashir', 'cash', 0),
        ('Bashir', 'bank', 0),
        ('Ahmed', 'cash', 0),
        ('Ahmed', 'bank', 0)
    ]

    for row in defaults:
        cursor.execute("""
        INSERT OR IGNORE INTO wallets
        VALUES (?, ?, ?)
        """, row)

    # الخزائن الافتراضية
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

# =====================================
# حساب رأس المال
# =====================================


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

# =====================================
# تسجيل الدخول
# =====================================

if "user_tokens" not in st.session_state:
    st.session_state["user_tokens"] = {
        "B2026": "Bashir",
        "A2026": "Ahmed"
    }

USER_TOKENS = st.session_state["user_tokens"]

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# =====================================
# واجهة الدخول
# =====================================

if st.session_state["logged_in_user"] is None:


    st.markdown("""
    <div style='text-align:center;padding:40px;'>
        <h1>🛍 منظومة متجر رنيم</h1>
        <h3>نظام إدارة احترافي للمخزون والمحاسبة</h3>
    </div>
    """, unsafe_allow_html=True)

    st.info("🔒 الرجاء إدخال الرمز السري للمتابعة")

    token_input = st.text_input(
        "الرمز السري",
        type="password"
    )

    if st.button("تسجيل الدخول"):

        if token_input in USER_TOKENS:

            st.session_state[
                "logged_in_user"
            ] = USER_TOKENS[token_input]

            st.success("تم تسجيل الدخول بنجاح")

            st.rerun()

        else:
            st.error("الرمز السري غير صحيح")

# =====================================
# الواجهة الرئيسية
# =====================================

else:

    current_user = st.session_state[
        "logged_in_user"
    ]

    # القائمة الجانبية
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

        st.title("🛍 مرحباً بك في منظومة متجر رنيم")

        st.caption(
            "إدارة المخزون والأرباح والخزائن المالية"
        )

        # الخزائن
        cursor.execute(
            "SELECT * FROM capital_accounts"
        )

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

        # إحصائيات
        cursor.execute(
            "SELECT COUNT(*) FROM products"
        )
        products_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM transactions"
        )
        sales_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT IFNULL(SUM(profit),0) FROM transactions"
        )
        total_profit = cursor.fetchone()[0]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "📦 المنتجات",
                products_count
            )

        with c2:
            st.metric(
                "🧾 المبيعات",
                sales_count
            )

        with c3:
            st.metric(
                "📈 إجمالي الأرباح",
                f"{round(total_profit,2)} د.ل"
            )

    # =====================================
    # الخزائن والمحافظ
    # =====================================

    elif choice == "الخزائن والمحافظ":

        st.header("💰 إدارة الخزائن والمحافظ")

        # عرض المحافظ
        cursor.execute(
            "SELECT * FROM wallets"
        )

        wallets = cursor.fetchall()

        for wallet in wallets:

            st.info(
                f"{wallet[0]} | {wallet[1]} | {wallet[2]} د.ل"
            )

        st.divider()

        # تعديل المحافظ
        st.subheader("⚙️ تعديل المحافظ")

        partner = st.selectbox(
            "الشريك",
            ["Bashir", "Ahmed"]
        )

        wallet_type = st.selectbox(
            "نوع المحفظة",
            ["cash", "bank"]
        )

        new_balance = st.number_input(
            "الرصيد الجديد",
            min_value=0.0,
            step=1.0
        )

        if st.button("حفظ تعديل المحفظة"):


            cursor.execute("""
            UPDATE wallets
            SET balance = ?
            WHERE partner_name = ?
            AND account_type = ?
            """, (
                new_balance,
                partner,
                wallet_type
            ))

            conn.commit()

            st.success("تم تعديل المحفظة")

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
            key="capital_edit"
        )

        if st.button("حفظ تعديل الخزنة"):

            cursor.execute("""
            UPDATE capital_accounts
            SET balance = ?
            WHERE account_type = ?
            """, (
                capital_balance,
                capital_type
            ))

            cursor.execute("""
            INSERT INTO financial_logs
            (action_type, account_type, amount, note)
            VALUES (?, ?, ?, ?)
            """, (
                "تعديل خزنة",
                capital_type,
                capital_balance,
                "تعديل يدوي"
            ))

            conn.commit()

            st.success("تم تعديل الخزنة")

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
            SELECT * FROM products
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

            payment_source = st.radio(
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
                    f"رأس المال للقطعة: {calculated_cap} د.ل"
                )

            selling_price = st.number_input(
                "سعر البيع",
                min_value=0.0,
                step=1.0
            )

            if st.button("حفظ المنتج"):

                total_cost = calculated_cap * qty

                cursor.execute("""
                SELECT balance
                FROM capital_accounts
                WHERE account_type = ?
                """, (payment_source,))

                current_capital = cursor.fetchone()[0]

                if total_cost > current_capital:

                    st.error(
                        "الرصيد غير كافي في الخزنة"
                    )

                else:


                    new_capital = (
                        current_capital - total_cost
                    )

                    cursor.execute("""
                    UPDATE capital_accounts
                    SET balance = ?
                    WHERE account_type = ?
                    """, (
                        new_capital,
                        payment_source
                    ))

                    if existing:

                        cursor.execute("""
                        UPDATE products
                        SET quantity = quantity + ?,
                            fixed_capital = ?,
                            selling_price = ?
                        WHERE name = ?
                        """, (
                            qty,
                            calculated_cap,
                            selling_price,
                            p_name
                        ))

                    else:

                        cursor.execute("""
                        INSERT INTO products
                        (name, quantity, fixed_capital, selling_price)
                        VALUES (?, ?, ?, ?)
                        """, (
                            p_name,
                            qty,
                            calculated_cap,
                            selling_price
                        ))

                    cursor.execute("""
                    INSERT INTO financial_logs
                    (action_type, account_type, amount, note)
                    VALUES (?, ?, ?, ?)
                    """, (
                        "شراء بضاعة",
                        payment_source,
                        -total_cost,
                        p_name
                    ))

                    conn.commit()

                    st.success(
                        "تمت إضافة البضاعة بنجاح"
                    )

        st.divider()

        # حذف منتج
        st.subheader("🗑 حذف منتج")

        delete_id = st.number_input(
            "رقم المنتج",
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
            SELECT name,
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

                    st.error("الكمية غير كافية")

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

                    # إضافة رأس المال للخزنة
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

                    # توزيع الأرباح
                    share = round(
                        net_profit / 2,
                        2
                    )

                    cursor.execute("""
                    UPDATE wallets
                    SET balance = balance + ?
                    WHERE partner_name = 'Bashir'
                    AND account_type = ?
                    """, (
                        share,
                        payment_method
                    ))

                    cursor.execute("""
                    UPDATE wallets
                    SET balance = balance + ?
                    WHERE partner_name = 'Ahmed'
                    AND account_type = ?
                    """, (
                        share,
                        payment_method
                    ))

                    # تسجيل العملية
                    cursor.execute("""
                    INSERT INTO transactions
                    (
                        product_name,
                        quantity,
                        total,
                        capital,
                        profit,
                        payment_method
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        qty_to_sell,
                        total_sale,
                        total_capital,
                        net_profit,
                        payment_method
                    ))

                    cursor.execute("""
                    INSERT INTO financial_logs
                    (action_type, account_type, amount, note)
                    VALUES (?, ?, ?, ?)
                    """, (
                        "بيع",
                        payment_method,
                        total_sale,
                        name
                    ))

                    conn.commit()

                    st.success(
                        f"تم البيع | الربح {net_profit} د.ل"
                    )

    # =====================================
    # البحث
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

                st.success("تم العثور على المنتج")

                st.write(f"📦 الاسم: {prod[1]}")
                st.write(f"📦 الكمية: {prod[2]}")
                st.write(f"💰 رأس المال: {prod[3]}")
                st.write(f"💵 سعر البيع: {prod[4]}")

            else:
                st.error("المنتج غير موجود")


    # =====================================
    # سجل العمليات
    # =====================================

    elif choice == "سجل العمليات":

        st.header("📑 سجل المبيعات")

        cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        if rows:

            for row in rows:

                st.container()

                st.write(f"🛒 المنتج: {row[1]}")
                st.write(f"📦 الكمية: {row[2]}")
                st.write(f"💰 المبيعات: {row[3]} د.ل")
                st.write(f"🏦 رأس المال: {row[4]} د.ل")
                st.write(f"📈 الربح: {row[5]} د.ل")
                st.write(f"💳 الدفع: {row[6]}")
                st.write(f"🕒 التاريخ: {row[7]}")

                st.divider()

        else:
            st.info("لا توجد عمليات")

    # =====================================
    # السجل المالي
    # =====================================

    elif choice == "السجل المالي":

        st.header("📚 السجل المالي الكامل")

        cursor.execute("""
        SELECT *
        FROM financial_logs
        ORDER BY id DESC
        """)

        logs = cursor.fetchall()

        if logs:

            for log in logs:

                st.write(
                    f"{log[5]} | "
                    f"{log[1]} | "
                    f"{log[2]} | "
                    f"{log[3]} د.ل | "
                    f"{log[4]}"
                )

                st.divider()

        else:
            st.info("السجل المالي فارغ")
