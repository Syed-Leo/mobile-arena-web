from flask import Flask, render_template, request, redirect, session, flash , url_for , jsonify
from db import cur, con

app = Flask(__name__)
app.secret_key = "dev-secret"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["userid"]
        password = request.form["password"]

        cur.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        admin = cur.fetchone()

        if admin:
            session["admin"] = username
            session["admin_name"] = username
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


# ---------------- ADMIN LOGOUT ----------------
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    admin_name = session.get("admin")

    return render_template(
        "admin_dashboard.html",
        admin_name=admin_name
    )


# ---------------- ADD PRODUCT ----------------
@app.route("/admin/add", methods=["GET", "POST"])
def add_product():
    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":
        brand_id = request.form["brand_id"]
        product_name = request.form["product_name"]
        price = request.form["price"]
        description = request.form["description"]

        ram = request.form["ram"]
        storage = request.form["storage"]
        battery = request.form["battery"]
        os = request.form["os"]
        network = request.form["network"]
        front = request.form["front_camera"]
        rear = request.form["rear_camera"]

        cur.execute("""
            INSERT INTO product 
            (product_name, price, stock, description, brand_id,
             ram, storage, battery, os, network, front_camera, rear_camera)
            VALUES (%s,%s,10,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            product_name, price, description, brand_id,
            ram, storage, battery, os, network, front, rear
        ))

        con.commit()

        flash("Phone added successfully 📱", "success")

        return redirect(url_for("add_product"))

    return render_template("admin_add.html")

# ---------------- UPDATE PRODUCT PRICE ----------------
@app.route("/admin/update", methods=["GET","POST"])
def update_price():

    if "admin" not in session:
        return redirect("/admin")

    msg = None

    if request.method == "POST":

        product_id = request.form["product_id"]
        price = request.form["price"]

        cur.execute(
        "UPDATE product SET price=%s WHERE product_id=%s",
        (price, product_id)
        )

        con.commit()

        msg = "Price updated successfully"


    cur.execute("SELECT brand_id, brand_name FROM brand")
    brands = cur.fetchall()

    return render_template(
        "admin_update.html",
        brands=brands,
        msg=msg
    )


@app.route("/get_products/<int:brand_id>")
def get_products(brand_id):

    cur.execute(
        "SELECT product_id, product_name FROM product WHERE brand_id=%s",
        (brand_id,)
    )

    products = cur.fetchall()

    result = []

    for p in products:
        result.append({
            "product_id": p[0],
            "product_name": p[1]
        })

    return jsonify(result)

# ---------------- DELETE PRODUCT ----------------
@app.route("/admin/delete", methods=["GET","POST"])
def delete_product():

    if "admin" not in session:
        return redirect("/admin")

    msg = None

    if request.method == "POST":

        product_id = request.form["product_id"]

        cur.execute(
        "DELETE FROM product WHERE product_id=%s",
        (product_id,)
        )

        con.commit()

        msg = "Phone deleted successfully"


    cur.execute("SELECT brand_id, brand_name FROM brand")
    brands = cur.fetchall()

    return render_template(
        "admin_delete.html",
        brands=brands,
        msg=msg
    )

# ---------------- VIEW DATABASE ----------------
@app.route("/admin/database", methods=["GET","POST"])
def view_database():

    if "admin" not in session:
        return redirect("/admin")

    phones = None

    cur.execute("SELECT brand_id, brand_name FROM brand")
    brands = cur.fetchall()

    if request.method == "POST":

        brand_id = request.form["brand_id"]

        cur.execute("""
        SELECT product_name, ram, storage, battery,
               network, front_camera, rear_camera, price
        FROM product
        WHERE brand_id=%s
        """,(brand_id,))

        phones = cur.fetchall()

    return render_template(
        "admin_database.html",
        brands=brands,
        phones=phones
    )


# ---------------- MANAGE ORDERS ----------------
@app.route("/admin/orders")
def admin_orders():
    if "admin" not in session:
        return redirect("/admin")
    
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT o.order_id, c.full_name, o.order_date, o.total_amount, o.status
        FROM orders o
        JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    """)

    orders = cur.fetchall()

    return render_template("admin_orders.html", orders=orders)


# ---------------- UPDATE ORDER STATUS ----------------
@app.route("/admin/update_order/<int:order_id>", methods=["POST"])
def update_order(order_id):

    if "admin" not in session:
        return redirect("/admin")

    new_status = request.form["status"]

    cur.execute(
        "UPDATE orders SET status=%s WHERE order_id=%s",
        (new_status, order_id)
    )

    con.commit()
    return redirect("/admin/orders")


# ---------------- CUSTOMER LOGIN ----------------
@app.route("/customer", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form["userid"]
        password = request.form["password"]

        cur.execute(
            "SELECT * FROM customer WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        if user:
            session["customer"] = email
            session["customer_id"] = user[0]   # IMPORTANT
            return redirect("/customer/dashboard")
        else:
            return render_template("customer_login.html", error="Invalid credentials")

    return render_template("customer_login.html")

# ---------------- CUSTOMER SIGNUP ----------------
@app.route("/customer/customer_signup", methods=["GET","POST"])
def customer_signup():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        address = request.form["address"]

        cur = con.cursor()

        cur.execute("""
        INSERT INTO customer (full_name,email,phone,password,address)
        VALUES (%s,%s,%s,%s,%s)
        """,(full_name,email,phone,password,address))

        con.commit()

        flash("Account created successfully","success")

        return redirect(url_for("customer_login"))

    return render_template("customer_signup.html")

# ---------------- CUSTOMER DASHBOARD ----------------
@app.route("/customer/dashboard")
def customer_dashboard():
    if "customer" not in session:
        return redirect("/customer")

    return render_template("customer_dashboard.html")


# ---------------- CUSTOMER LOGOUT ----------------
@app.route("/customer/logout")
def customer_logout():
    session.pop("customer", None)
    return redirect("/")


# ---------------- SEARCH PRODUCT ----------------
@app.route("/customer/search")
def customer_search():
    if "customer_id" not in session:
        return redirect("/customer")

    product_name = request.args.get("product_name")

    cur = con.cursor()

    if product_name:
        cur.execute("""
            SELECT p.product_id, p.product_name,
                   p.ram, p.storage, p.os, p.network,
                   p.front_camera, p.rear_camera, p.price
            FROM product p
            WHERE p.product_name LIKE %s
        """, ("%" + product_name + "%",))

        results = cur.fetchall()
        return render_template("customer_search.html", results=results)

    return render_template("customer_search.html")


# ---------------- FILTER PRODUCTS ----------------
@app.route("/customer/filter", methods=["GET", "POST"])
def customer_filter():

    if "customer" not in session:
        return redirect("/customer")

    brand = request.values.get("brand")
    min_price = request.values.get("min_price")
    max_price = request.values.get("max_price")
    ram = request.values.get("ram")
    storage = request.values.get("storage")
    network = request.values.get("network")
    battery = request.values.get("battery")
    front = request.values.get("front_camera")
    rear = request.values.get("rear_camera")

    query = """
        SELECT p.product_id, p.product_name, b.brand_name,
        p.ram, p.storage, p.battery,
        p.front_camera, p.rear_camera, p.price
        FROM product p
        JOIN brand b ON p.brand_id = b.brand_id
        WHERE 1=1
    """

    values = []

    if brand:
        query += " AND b.brand_name=%s"
        values.append(brand)

    if min_price:
        query += " AND p.price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND p.price <= %s"
        values.append(max_price)

    if ram:
        query += " AND p.ram=%s"
        values.append(ram)

    if storage:
        query += " AND p.storage=%s"
        values.append(storage)

    if network:
        query += " AND p.network=%s"
        values.append(network)

    if battery:
        query += " AND p.battery=%s"
        values.append(battery)

    if front:
        query += " AND p.front_camera=%s"
        values.append(front)

    if rear:
        query += " AND p.rear_camera=%s"
        values.append(rear)

    cur.execute(query, tuple(values))
    results = cur.fetchall()

    return render_template("customer_filter.html", results=results)

# ---------------- ADMIN ADD CUSTOMER ----------------

@app.route("/admin/add_customer", methods=["GET","POST"])
def admin_add_customer():

    if "admin" not in session:
        return redirect("/admin")

    msg = None
    msg_type = None

    if request.method == "POST":

        name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        address = request.form["address"]

        cur.execute(
            "SELECT phone, email FROM customer WHERE phone=%s OR email=%s",
            (phone, email)
        )

        existing = cur.fetchone()

        if existing:

            msg_type = "error"

            if existing[0] == phone:
                msg = "Phone number already exists"
            elif existing[1] == email:
                msg = "Email already exists"

            return render_template(
                "admin_add_customer.html",
                msg=msg,
                msg_type=msg_type,
                full_name=name,
                email=email,
                phone=phone,
                password=password,
                address=address
            )

        else:

            cur.execute("""
            INSERT INTO customer
            (full_name,email,phone,password,address)
            VALUES (%s,%s,%s,%s,%s)
            """,(name,email,phone,password,address))

            con.commit()

            msg = "Customer added successfully"
            msg_type = "success"

            return render_template(
                "admin_add_customer.html",
                msg=msg,
                msg_type=msg_type
            )

    return render_template("admin_add_customer.html")

# ---------------- ADMIN VIEW CUSTOMERS ----------------

@app.route("/admin/view_customers")
def view_customers():
    if "admin" not in session:
        return redirect("/admin")

    cur.execute("SELECT customer_id, full_name, email, phone, address FROM customer")
    customers = cur.fetchall()

    return render_template("admin_view_customers.html", customers=customers)

# ---------------- ADMIN DELETE CUSTOMER ----------------

@app.route("/admin/delete_customer", methods=["GET","POST"])
def delete_customer():

    if "admin" not in session:
        return redirect("/admin")

    msg = None

    if request.method == "POST":
        customer_id = request.form["customer_id"]

        cur.execute("DELETE FROM customer WHERE customer_id=%s", (customer_id,))
        con.commit()

        msg = "Customer deleted successfully"

    # ALWAYS fetch updated list
    cur.execute("SELECT customer_id, full_name FROM customer")
    customers = cur.fetchall()

    return render_template(
        "admin_delete_customer.html",
        customers=customers,
        msg=msg
    )

# ---------------- ADMIN ADD ADMIN ----------------
@app.route("/admin/add_admin", methods=["GET","POST"])
def add_admin():

    if request.method == "POST":

        username = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cur = con.cursor()

        cur.execute("""
        INSERT INTO admin (username,email,password)
        VALUES (%s,%s,%s)
        """,(username,email,password))

        con.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template("add_admin.html")

# ---------------- CUSTOMER ORDERS ----------------

@app.route("/customer/orders")
def customer_orders():

    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]

    cur = con.cursor()

    cur.execute("""
    SELECT 
        o.order_id,
        o.order_date,
        o.status,
        p.product_name,
        p.ram,
        p.storage,
        oi.quantity,
        p.price
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN product p ON oi.product_id = p.product_id
    WHERE o.customer_id = %s
    ORDER BY o.order_id DESC
    """, (customer_id,))

    rows = cur.fetchall()

    orders = {}

    for row in rows:

        order_id = row[0]

        if order_id not in orders:
            orders[order_id] = {
                "order_id": row[0],
                "date": row[1],
                "status": row[2],
                "products": []
            }

        orders[order_id]["products"].append({
            "product_name": row[3],
            "ram": row[4],
            "storage": row[5],
            "quantity": row[6],
            "price": row[7]
        })

    return render_template(
        "customer_orders.html",
        orders=orders.values()
    )

# ---------------- ORDER DETAILS ----------------

@app.route("/customer/order/<int:order_id>")
def order_details(order_id):
    if "customer_id" not in session:
        return redirect("/customer")

    cur.execute("""
        SELECT 
        p.product_name,
        p.ram,
        p.storage,
        oi.quantity,
        p.price
        FROM order_items oi
        JOIN product p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
    """, (order_id,))

    items = cur.fetchall()

    return render_template("order_details.html", items=items)

# ---------------- PLACE ORDER  ----------------
@app.route("/customer/place_order", methods=["POST"])
def place_order():
    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]
    product_id = request.form["product_id"]

    # Get product price
    cur.execute("SELECT price FROM product WHERE product_id=%s", (product_id,))
    product = cur.fetchone()

    if not product:
        return "Product not found"

    price = product[0]

    # Create order
    cur.execute("""
        INSERT INTO orders (customer_id, total_amount, status)
        VALUES (%s, %s, 'PENDING')
    """, (customer_id, price))

    con.commit()

    # Get latest order_id
    order_id = cur.lastrowid

    # Insert into order_items
    cur.execute("""
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
    """, (order_id, product_id, 1, price))

    con.commit()

    return redirect("/customer/orders")

# ---------------- CANCEL ORDER  ----------------

@app.route("/customer/cancel_order", methods=["POST"])
def cancel_order():

    order_id = request.form.get("order_id")

    cur = con.cursor()

    cur.execute("""
        UPDATE orders
        SET status = 'CANCELLED'
        WHERE order_id = %s
    """, (order_id,))

    con.commit()

    return redirect(url_for("customer_orders"))

# ---------------- DELETE ORDER  ----------------

@app.route("/customer/delete_order", methods=["POST"])
def delete_order():

    order_id = request.form.get("order_id")

    cur = con.cursor()

    cur.execute("""
    UPDATE orders
    SET is_deleted = 1
    WHERE order_id=%s
    """,(order_id,))

    con.commit()

    return redirect(url_for("customer_orders"))

# ---------------- ADD TO CART  ----------------

@app.route("/customer/add_to_cart", methods=["POST"])
def add_to_cart():
    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]
    product_id = request.form.get("product_id")

    cur.execute("""
        SELECT quantity
        FROM cart
        WHERE customer_id=%s AND product_id=%s
    """, (customer_id, product_id))

    item = cur.fetchone()

    if item:
        cur.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE customer_id=%s AND product_id=%s
        """, (customer_id, product_id))
    else:
        cur.execute("""
            INSERT INTO cart (customer_id, product_id, quantity)
            VALUES (%s,%s,1)
        """, (customer_id, product_id))

    con.commit()

    flash("Product added to cart 🛒", "success")

    return redirect(request.referrer)

# ---------------- ORDER HISTORY  ----------------

@app.route("/customer/order_history")
def order_history():

    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]

    cur = con.cursor()

    cur.execute("""
    SELECT 
        o.order_id,
        o.order_date,
        o.status,
        p.product_name,
        p.ram,
        p.storage,
        oi.quantity,
        p.price,
        o.is_deleted
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN product p ON oi.product_id = p.product_id
    WHERE o.customer_id = %s
    ORDER BY o.order_id DESC
    """,(customer_id,))

    rows = cur.fetchall()

    orders = {}

    for row in rows:

        order_id = row[0]

        if order_id not in orders:
            orders[order_id] = {
                "order_id": row[0],
                "date": row[1],
                "status": row[2],
                "deleted": row[8],
                "products":[]
            }

        orders[order_id]["products"].append({
            "name": row[3],
            "ram": row[4],
            "storage": row[5],
            "quantity": row[6],
            "price": row[7]
        })

    return render_template("order_history.html", orders=orders.values())

# ---------------- VIEW CART  ----------------

@app.route("/customer/cart")
def view_cart():
    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]

    cur = con.cursor(dictionary=True)

    cur.execute("""
    SELECT 
    c.cart_id,
    p.product_id,
    p.product_name,
    p.ram,
    p.storage,
    p.price,
    c.quantity,
    (p.price * c.quantity) AS subtotal
    FROM cart c
    JOIN product p ON c.product_id = p.product_id
    WHERE c.customer_id = %s
    """, (customer_id,))

    cart_items = cur.fetchall()

    total = sum(item["subtotal"] for item in cart_items)

    return render_template("cart.html", cart=cart_items, total=total)

# ---------------- CHECKOUT  ----------------

@app.route("/customer/checkout", methods=["POST"])
def checkout():
    if "customer_id" not in session:
        return redirect("/customer")

    customer_id = session["customer_id"]
    cur = con.cursor(dictionary=True)

    # Get cart items
    cur.execute("""
        SELECT product_id, quantity
        FROM cart
        WHERE customer_id=%s
    """, (customer_id,))

    items = cur.fetchall()

    if not items:
        return redirect("/customer/cart")

    total_amount = 0

    # Calculate total
    for item in items:
        cur.execute("SELECT price FROM product WHERE product_id=%s",
                    (item["product_id"],))
        price = cur.fetchone()["price"]
        total_amount += price * item["quantity"]

    # Create order
    cur.execute("""
        INSERT INTO orders (customer_id, total_amount, status)
        VALUES (%s, %s, 'PENDING')
    """, (customer_id, total_amount))

    con.commit()
    order_id = cur.lastrowid

    # Insert order items
    for item in items:
        cur.execute("SELECT price FROM product WHERE product_id=%s",
                    (item["product_id"],))
        price = cur.fetchone()["price"]

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item["product_id"], item["quantity"], price))

    con.commit()

    # Clear cart after checkout
    cur.execute("DELETE FROM cart WHERE customer_id=%s", (customer_id,))
    con.commit()

    return redirect("/customer/orders")

# ---------------- CART COUNTER ----------------

@app.context_processor
def inject_cart_count():
    if "customer_id" in session:
        customer_id = session["customer_id"]

        cur = con.cursor(dictionary=True)
        cur.execute("""
            SELECT SUM(quantity) AS total_items
            FROM cart
            WHERE customer_id = %s
        """, (customer_id,))

        result = cur.fetchone()
        count = result["total_items"] if result["total_items"] else 0

        return dict(cart_count=count)

    return dict(cart_count=0)

# ---------------- CART UPDATE ----------------

@app.route("/customer/update_cart", methods=["POST"])
def update_cart():

    customer_id = session["customer_id"]
    product_id = request.form.get("product_id")
    action = request.form.get("action")

    if action == "increase":

        cur.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE customer_id=%s AND product_id=%s
        """, (customer_id, product_id))

    elif action == "decrease":

        cur.execute("""
        UPDATE cart
        SET quantity = quantity - 1
        WHERE customer_id=%s AND product_id=%s
        """, (customer_id, product_id))

        cur.execute("""
        DELETE FROM cart
        WHERE customer_id=%s
        AND product_id=%s
        AND quantity <= 0
        """, (customer_id, product_id))

    con.commit()

    return redirect(url_for("view_cart"))

# ---------------- REMOVE FROM CART ----------------
@app.route("/customer/remove_from_cart", methods=["POST"])
def remove_from_cart():

    customer_id = session["customer_id"]
    product_id = request.form.get("product_id")

    cur.execute("""
    DELETE FROM cart
    WHERE customer_id=%s AND product_id=%s
    """, (customer_id, product_id))

    con.commit()

    flash("Item removed from cart 🗑", "info")

    return redirect(url_for("view_cart"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)