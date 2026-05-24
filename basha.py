import streamlit as st
import sqlite3

# ==============================
# تجهيز قاعدة البيانات
# ==============================

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

    # جدول المحافظ
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        partner_name TEXT PRIMARY KEY,
        balance REAL
    )
    """)

    # جدول العمليات
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

    # إدخال المحافظ إن لم تكن موجودة
    cursor.execute("""
    INSERT OR IGNORE INTO wallets (partner_name, balance)
    VALUES ('Bashir', 0.0)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO wallets (partner_name, balance)
    VALUES ('Ahmed', 0.0)
    """)

    conn.commit()
    return conn


conn = init_db()
cursor = conn.cursor()

# ==============================
# حساب رأس المال
# ==============================

def calculate_capital(
    price_yuan,
    weight,
    pack_cost,
    bag_cost,
    dollar_rate,
    shipping_rate
):
    product_cost_lyd = (price_yuan * 0.14) * dollar_rate
    shipping_cost_lyd = (weight * shipping_rate) * dollar_rate

    total = (
        product_cost_lyd
        + shipping_cost_lyd
        + pack_cost
        + bag_cost
    )

    return round(total, 2)

# ==============================
# إعدادات الصفحة
# ==============================

st.set_page_config(
    page_title="Ranim Store Secure",
    page_icon="🔒",
    layout="wide"
)

# ==============================
# الرموز السرية
# ==============================

if "user_tokens" not in st.session_state:
    st.session_state["user_tokens"] = {
        "B2026": "Bashir",
        "A2026": "Ahmed"
    }

USER_TOKENS = st.session_state["user_tokens"]

# ==============================
# حالة تسجيل الدخول
# ==============================

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# ==============================
# شاشة تسجيل الدخول
# ==============================

if st.session_state["logged_in_user"] is None:

    st.subheader("🔒 نظام إدارة متجر رنيم الآمن")

    token_input = st.text_input(
        "أدخل الرمز السري الخاص بك:",
        type="password"
    )

    if st.button("تسجيل الدخول"):

        if token_input in USER_TOKENS:

            st.session_state["logged_in_user"] = USER_TOKENS[token_input]

            st.success(
                f"مرحباً بك يا {st.session_state['logged_in_user']}"
            )

            st.rerun()

        else:
            st.error("الرمز السري غير صحيح")

# ==============================
# بعد تسجيل الدخول
# ==============================

else:

    current_user = st.session_state["logged_in_user"]

    # تسجيل خروج
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["logged_in_user"] = None
        st.rerun()

    st.title("📦 لوحة تحكم متجر رنيم")

    st.markdown(
        f"👤 المستخدم الحالي: **{current_user}**"
    )

    # القائمة
    menu = [
        "لوحة التحكم والمحافظ",
        "إضافة وتحديث البضاعة",
        "تسجيل عملية بيع",
        "الاستعلام عن منتج",
        "سجل العمليات"
    ]

    choice = st.sidebar.selectbox(
        "القائمة الرئيسية",
        menu
    )

    # ==========================================
    # لوحة التحكم والمحافظ
    # ==========================================

    if choice == "لوحة التحكم والمحافظ":

        st.header("👥 المحافظ المالية")

        cursor.execute(
            "SELECT partner_name, balance FROM wallets"
        )

        wallets = {
            row[0]: row[1]
            for row in cursor.fetchall()
        }

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "محفظة بشير",
                f"{wallets.get('Bashir', 0.0)} د.ل"
            )

        with col2:
            st.metric(
                "محفظة أحمد",
                f"{wallets.get('Ahmed', 0.0)} د.ل"
            )

        # ==========================
        # سحب الأموال
        # ==========================

        st.divider()

        st.subheader(
            f"💸 سحب من محفظتك ({current_user})"
        )

        withdraw_amount = st.number_input(
            "المبلغ المراد سحبه",
            min_value=0.0,
            step=1.0
        )

        if st.button("تأكيد السحب"):

            current_balance = wallets.get(
                current_user,
                0.0
            )

            if withdraw_amount > current_balance:

                st.error("الرصيد غير كافٍ")

            elif withdraw_amount <= 0:

                st.warning("أدخل مبلغ صحيح")

            else:

                new_balance = round(
                    current_balance - withdraw_amount,
                    2
                )

                cursor.execute("""
                UPDATE wallets
                SET balance = ?
                WHERE partner_name = ?
                """, (
                    new_balance,
                    current_user
                ))

                conn.commit()

                st.success("تم السحب بنجاح")

                st.rerun()

        # ==========================
        # تعديل المحافظ
        # ==========================

        st.divider()

        st.subheader("⚙️ تعديل المحافظ")

        partner_edit = st.selectbox(
            "اختر المحفظة",
            ["Bashir", "Ahmed"]
        )

        new_balance = st.number_input(
            "الرصيد الجديد",
            min_value=0.0,
            step=1.0,
            key="balance_edit"
        )

        if st.button("حفظ الرصيد الجديد"):

            cursor.execute("""
            UPDATE wallets
            SET balance = ?
            WHERE partner_name = ?
            """, (
                new_balance,
                partner_edit
            ))

            conn.commit()

            st.success(
                f"تم تحديث رصيد {partner_edit}"
            )

            st.rerun()

        # ==========================
        # تغيير الرمز السري
        # ==========================

        st.divider()

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

                    USER_TOKENS[new_token] = current_user

                    st.success(
                        "تم تغيير الرمز السري بنجاح"
                    )

                    found = True

                    break

            if not found:
                st.error("الرمز الحالي غير صحيح")

    # ==========================================
    # إضافة وتحديث البضاعة
    # ==========================================

    elif choice == "إضافة وتحديث البضاعة":

        st.header("🛒 إدارة البضاعة")

        p_name = st.text_input(
            "اسم المنتج"
        ).strip()

        if p_name:

            cursor.execute("""
            SELECT id, quantity, fixed_capital, selling_price
            FROM products
            WHERE name = ?
            """, (p_name,))

            existing = cursor.fetchone()

            if existing:

                st.warning(
                    f"المنتج موجود مسبقاً | ID: {existing[0]}"
                )

            qty = st.number_input(
                "الكمية",
                min_value=1,
                step=1
            )

            price_yuan = st.number_input(
                "سعر المنتج باليوان",
                min_value=0.0,
                step=0.5
            )

            weight = st.number_input(
                "وزن القطعة",
                min_value=0.0,
                step=0.05
            )

            pack_cost = st.number_input(
                "تكلفة التغليف",
                min_value=0.0,
                step=0.5
            )

            bag_cost = st.number_input(
                "تكلفة الكيس",
                min_value=0.0,
                step=0.5
            )

            dollar_rate = st.number_input(
                "سعر الدولار",
                min_value=0.0,
                value=7.1,
                step=0.05
            )

            shipping_rate = st.number_input(
                "الشحن لكل كيلو",
                min_value=0.0,
                value=12.5,
                step=0.5
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

                st.success(
                    f"سعر بيع مقترح: "
                    f"{round(calculated_cap*1.3)}"
                    f" - "
                    f"{round(calculated_cap*1.7)} د.ل"
                )

            selling_price = st.number_input(
                "سعر البيع",
                min_value=0.0,
                step=1.0
            )

            if st.button("حفظ المنتج"):

                if existing:

                    total_qty = existing[1] + qty

                    cursor.execute("""
                    UPDATE products
                    SET quantity=?,
                        fixed_capital=?,
                        selling_price=?
                    WHERE id=?
                    """, (
                        total_qty,
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

                conn.commit()

                st.success("تم حفظ المنتج")

        # ==========================
        # حذف منتج
        # ==========================

        st.divider()

        st.subheader("🗑️ حذف منتج")

        delete_id = st.number_input(
            "رقم المنتج للحذف",
            min_value=1,
            step=1,
            key="delete_product"
        )

        if st.button("حذف المنتج"):

            cursor.execute("""
            SELECT name
            FROM products
            WHERE id = ?
            """, (delete_id,))

            check = cursor.fetchone()

            if check:

                cursor.execute("""
                DELETE FROM products
                WHERE id = ?
                """, (delete_id,))

                conn.commit()

                st.success(
                    f"تم حذف المنتج: {check[0]}"
                )

            else:
                st.error("المنتج غير موجود")

    # ==========================================
    # تسجيل عملية بيع
    # ==========================================

    elif choice == "تسجيل عملية بيع":

        st.header("💰 تسجيل عملية بيع")

        p_id = st.number_input(
            "رقم المنتج",
            min_value=1,
            step=1
        )

        qty_to_sell = st.number_input(
            "الكمية المباعة",
            min_value=1,
            step=1
        )

        payment_method = st.radio(
            "طريقة الدفع",
            ["كاش", "مصرف"]
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

            elif product[1] < qty_to_sell:

                st.error(
                    f"المتوفر فقط {product[1]}"
                )

            else:

                name = product[0]
                current_qty = product[1]
                capital = product[2]
                price = product[3]

                total_before_discount = (
                    price * qty_to_sell
                )

                discount = (
                    round(
                        total_before_discount * 0.05,
                        2
                    )
                    if qty_to_sell >= 2
                    else 0.0
                )

                final_total = (
                    total_before_discount - discount
                )

                total_capital_cost = (
                    capital * qty_to_sell
                )

                net_profit = round(
                    final_total - total_capital_cost,
                    2
                )

                if final_total < total_capital_cost:

                    st.error(
                        "الخصم أكل رأس المال"
                    )

                else:

                    # تحديث الكمية
                    cursor.execute("""
                    UPDATE products
                    SET quantity = ?
                    WHERE id = ?
                    """, (
                        current_qty - qty_to_sell,
                        p_id
                    ))

                    # توزيع الأرباح
                    share = round(
                        net_profit / 2,
                        2
                    )

                    if share > 0:

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
                        final_total,
                        net_profit,
                        payment_method
                    ))

                    conn.commit()

                    st.success(
                        f"تم البيع بنجاح | "
                        f"الربح الصافي: {net_profit} د.ل"
                    )

                    st.info(
                        f"طريقة الدفع: {payment_method}"
                    )

                    if (
                        current_qty - qty_to_sell
                    ) <= 3:

                        st.warning(
                            f"المتبقي فقط "
                            f"{current_qty - qty_to_sell}"
                        )

    # ==========================================
    # الاستعلام عن منتج
    # ==========================================

    elif choice == "الاستعلام عن منتج":

        st.header("🔍 البحث عن منتج")

        search_id = st.number_input(
            "رقم المنتج",
            min_value=1,
            step=1
        )

        if st.button("بحث"):

            cursor.execute("""
            SELECT
                name,
                quantity,
                fixed_capital,
                selling_price
            FROM products
            WHERE id = ?
            """, (search_id,))

            prod = cursor.fetchone()

            if prod:

                st.write(f"اسم المنتج: {prod[0]}")
                st.write(f"الكمية: {prod[1]}")
                st.write(
                    f"رأس المال: {prod[2]} د.ل"
                )
                st.write(
                    f"سعر البيع: {prod[3]} د.ل"
                )

            else:
                st.error("المنتج غير موجود")

    # ==========================================
    # سجل العمليات
    # ==========================================

    elif choice == "سجل العمليات":

        st.header("📑 سجل العمليات")

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

        operations = cursor.fetchall()

        if operations:

            for op in operations:

                st.container()

                st.write(f"🛒 المنتج: {op[0]}")
                st.write(f"📦 الكمية: {op[1]}")
                st.write(f"💰 الإجمالي: {op[2]} د.ل")
                st.write(f"📈 الربح: {op[3]} د.ل")
                st.write(f"🏦 الدفع: {op[4]}")
                st.write(f"🕒 التاريخ: {op[5]}")

                st.divider()

        else:

            st.info("لا توجد عمليات حالياً")