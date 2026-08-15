from flask import Flask, render_template, request, redirect, session
import sqlite3   # <<< important! DB connection panna
app = Flask(__name__)
app.secret_key = "supermarket"
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price REAL,
quantity INTEGER,
minimum_stock INTEGER
)
""")

conn.commit()
conn.close()

# Sample product list


cart = []
sales = []

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("login.html")


# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    # Admin Login
    if username == "admin" and password == "123":
        session['role'] = "admin"
        return redirect('/admin_dashboard')

    # User Login
    elif username == "user" and password == "123":
        session['role'] = "user"
        return redirect('/user_dashboard')

    else:
        return "Invalid Login"


# ---------------- USER DASHBOARD ----------------
@app.route('/user_dashboard')
def user_dashboard():
    return render_template("user_dashboard.html")



# ---------------- VIEW PRODUCTS ----------------
@app.route('/view_products')
def view_products():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("view_products.html", products=products)
# ---------------- ADD TO CART ----------------

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    if product:
        item = {
            "id": product["id"],
            "name": product["name"],
            "price": product["price"]
        }

        cart.append(item)

    conn.close()

    return redirect('/my_cart')
# ---------------- REMOVE FROM CART ----------------
@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):

    global cart

    cart = [item for item in cart if item["id"] != id]

    return redirect('/my_cart')


# ---------------- MY CART ----------------
@app.route('/my_cart')
def cart_page():
    total = sum(item["price"] for item in cart)
    return render_template("my_cart.html", cart=cart, total=total)
# ---------------- PURCHASE ----------------
@app.route('/purchase')
def purchase():

    for item in cart:
        sales.append(item)

    cart.clear()

    return "Purchase Successful"


# ---------------- PURCHASE HISTORY ----------------
@app.route('/purchase_history')
def purchase_history():
    return render_template("purchase_history.html", sales=sales)
# ---------------- CHECKOUT ----------------
@app.route('/checkout', methods=['POST'])
def checkout():

    for item in cart:
        sales.append(item)

    cart.clear()

    return redirect('/purchase_history')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ---------------- ADD PRODUCT ----------------
@app.route('/add_product', methods=['GET','POST'])
def add_product():

    if request.method == 'POST':

        conn = get_db()
        cursor = conn.cursor()

        product_name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        minimum_stock = request.form['minimum_stock']

        cursor.execute(
            "INSERT INTO products(name, category, price, quantity, minimum_stock) VALUES (?,?,?,?,?)",
            (product_name, category, price, quantity, minimum_stock)
        )
        conn.commit()  # 👈 commit illa na database save aagala
        conn.close()

        return redirect('/view_products')

    return render_template("add_product.html")

# ---------------- ADMIN VIEW PRODUCT ----------------
@app.route('/admin_view_products')
def admin_view_products():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()
    return render_template("admin_view_products.html", products=products)

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_product(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Form submit → update
        name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        minimum_stock = request.form['minimum_stock']

        # Update the product with the correct id
        cursor.execute("""
            UPDATE products
            SET name=?, category=?, price=?, quantity=?, minimum_stock=?
            WHERE id=?
        """, (name, category, price, quantity, minimum_stock, id))

        conn.commit()
        conn.close()
        return redirect('/admin_view_products')

    # GET → fetch product from DB to show in form
    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()
    conn.close()
    return render_template("edit_product.html", product=product)
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin_view_products')
# ---------------- MANAGE STOCK ----------------
@app.route('/manage_stock')
def manage_stock():
    # Direct DB connection inside route
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template('manage_stock.html', products=products)
@app.route('/update_stock/<int:id>', methods=['POST'])
def update_stock(id):

    new_stock = request.form['stock']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_stock, id))

    conn.commit()
    conn.close()

    return redirect('/manage_stock')




@app.route('/sales_report')
def sales_report():
    return render_template("sales_report.html", sales=sales)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)