import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "stockflow.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ---------------- MODELS ---------------- #

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(200))
    organization_id = db.Column(db.Integer)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    organization_id = db.Column(db.Integer)

    name = db.Column(db.String(120))
    sku = db.Column(db.String(50))

    quantity = db.Column(db.Integer)

    low_stock_threshold = db.Column(db.Integer, default=5)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer)

    product_name = db.Column(db.String(120))

    quantity_sold = db.Column(db.Integer)


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect("/login")


# Signup
@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        org_name = request.form["organization"]

        org = Organization(name=org_name)

        db.session.add(org)
        db.session.commit()

        hashed = bcrypt.generate_password_hash(password)

        user = User(
            email=email,
            password=hashed,
            organization_id=org.id
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


# Login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password,password):

            return redirect(f"/dashboard/{user.organization_id}")

        else:
            return "Invalid Login"

    return render_template("login.html")


# Dashboard
@app.route("/dashboard/<org_id>")
def dashboard(org_id):

    products = Product.query.filter_by(organization_id=org_id).all()

    sales = Sale.query.all()

    total_products = len(products)

    total_inventory = sum(p.quantity for p in products)

    low_stock = [p for p in products if p.quantity <= p.low_stock_threshold]

    return render_template(
        "dashboard.html",
        products=products,
        sales=sales,
        total_products=total_products,
        total_inventory=total_inventory,
        low_stock=low_stock,
        org_id=org_id
    )


# Add Product
@app.route("/add_product/<org_id>", methods=["POST"])
def add_product(org_id):

    name = request.form["name"]
    sku = request.form["sku"]
    quantity = int(request.form["quantity"])

    product = Product(
        organization_id=org_id,
        name=name,
        sku=sku,
        quantity=quantity
    )

    db.session.add(product)
    db.session.commit()

    return redirect(f"/dashboard/{org_id}")


# Sell Product
@app.route("/sell/<int:id>/<org_id>", methods=["POST"])
def sell_product(id, org_id):

    product = Product.query.get(id)

    sold_qty = int(request.form.get("sold_qty",0))

    if product:

        product.quantity -= sold_qty

        sale = Sale(
            product_id=id,
            product_name=product.name,
            quantity_sold=sold_qty
        )

        db.session.add(sale)

        # AUTO DELETE PRODUCT
        if product.quantity <= 0:
            db.session.delete(product)

        db.session.commit()

    return redirect(f"/dashboard/{org_id}")


# Edit Page
@app.route("/edit/<int:id>/<org_id>")
def edit_product(id, org_id):

    product = Product.query.get_or_404(id)

    return render_template("edit_product.html", product=product, org_id=org_id)


# Update Product
@app.route("/update/<int:id>/<org_id>", methods=["POST"])
def update_product(id, org_id):

    product = Product.query.get_or_404(id)

    product.name = request.form["name"]
    product.sku = request.form["sku"]
    product.quantity = int(request.form["quantity"])

    db.session.commit()

    return redirect(f"/dashboard/{org_id}")


# Delete Product
@app.route("/delete/<int:id>/<org_id>")
def delete_product(id, org_id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    return redirect(f"/dashboard/{org_id}")


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)