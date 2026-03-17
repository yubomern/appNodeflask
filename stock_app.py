from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "uploads"

db = SQLAlchemy(app)


# -------------------------
# MODEL
# -------------------------

class Stock(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    pipeline = db.Column(db.String(50))

    file = db.Column(db.String(200))


# -------------------------
# INIT
# -------------------------

@app.before_request
def create_tables():
    db.create_all()


# -------------------------
# HTML PAGE
# -------------------------

@app.route("/")
def home():
    return render_template("stock.html")


# -------------------------
# FILE UPLOAD
# -------------------------

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filename = file.filename

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(path)

    return jsonify({"file": filename})


# -------------------------
# CRUD API
# -------------------------

@app.route("/stocks", methods=["GET"])
def get_stocks():

    stocks = Stock.query.all()

    result = []

    for s in stocks:

        result.append({
            "id": s.id,
            "name": s.name,
            "quantity": s.quantity,
            "pipeline": s.pipeline,
            "file": s.file
        })

    return jsonify(result)


@app.route("/stocks", methods=["POST"])
def add_stock():

    name = request.form["name"]

    quantity = request.form["quantity"]

    pipeline = request.form["pipeline"]

    file = request.files["file"]

    filename = file.filename

    file.save(os.path.join("uploads", filename))

    stock = Stock(
        name=name,
        quantity=quantity,
        pipeline=pipeline,
        file=filename
    )

    db.session.add(stock)

    db.session.commit()

    return jsonify({"status": "created"})


@app.route("/stocks/<int:id>", methods=["DELETE"])
def delete_stock(id):

    stock = Stock.query.get(id)

    if stock:
        db.session.delete(stock)
        db.session.commit()

    return jsonify({"status": "deleted"})


# -------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory("uploads", filename)


if __name__ == "__main__":

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    app.run(debug=True)