from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)

    low_stock_threshold = db.Column(db.Integer, default=5)