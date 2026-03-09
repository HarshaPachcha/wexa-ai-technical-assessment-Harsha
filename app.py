from flask import Flask, render_template, request, redirect
from flask_bcrypt import Bcrypt
from models import db, User, Organization, Product

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stockflow.db"
app.config["SECRET_KEY"] = "secret"

db.init_app(app)
bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return redirect("/login")


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


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password,password):

            return redirect(f"/dashboard/{user.organization_id}")

    return render_template("login.html")


@app.route("/dashboard/<org_id>")
def dashboard(org_id):

    products = Product.query.filter_by(organization_id=org_id).all()

    total_products = len(products)

    total_inventory = sum(p.quantity for p in products)

    low_stock = [p for p in products if p.quantity <= p.low_stock_threshold]

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_inventory=total_inventory,
        low_stock=low_stock,
        org_id=org_id,
        products=products
    )


@app.route("/add_product/<org_id>", methods=["POST"])
def add_product(org_id):

    name = request.form["name"]
    sku = request.form["sku"]
    quantity = request.form["quantity"]

    product = Product(
        organization_id=org_id,
        name=name,
        sku=sku,
        quantity=quantity
    )

    db.session.add(product)
    db.session.commit()

    return redirect(f"/dashboard/{org_id}")


@app.route("/delete/<id>/<org_id>")
def delete_product(id,org_id):

    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    return redirect(f"/dashboard/{org_id}")


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)