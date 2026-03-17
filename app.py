from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------
# DATABASE MODEL
# -------------------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def index():
    return render_template("index.html")

# -------------------------
# REST API
# -------------------------

@app.route("/api/products", methods=["GET"])
def get_products():

    products = Product.query.all()

    result = []

    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "price": p.price
        })

    return jsonify(result)


@app.route("/api/products", methods=["POST"])
def add_product():

    data = request.json

    product = Product(
        name=data["name"],
        quantity=data["quantity"],
        price=data["price"]
    )

    db.session.add(product)
    db.session.commit()

    socketio.emit("notification", {"msg": "New product added!"})

    return jsonify({"status": "success"})


@app.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):

    data = request.json
    product = Product.query.get(id)

    product.name = data["name"]
    product.quantity = data["quantity"]
    product.price = data["price"]

    db.session.commit()

    return jsonify({"status": "updated"})


@app.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    return jsonify({"status": "deleted"})


# -------------------------
# SOCKET CHAT
# -------------------------

@socketio.on("message")
def handle_message(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    socketio.run(app, debug=True)