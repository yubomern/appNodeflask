from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

import os
import secrets

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------

app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

CORS(app)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

API_TOKEN = "mysecrettoken"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

# -------------------------
# SECURITY
# -------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def verify_token():
    token = request.headers.get("Authorization")
    if token != API_TOKEN:
        return False
    return True


# -------------------------
# MODEL
# -------------------------

class Stock(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

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
# SOCKET CONNECTION
# -------------------------

@socketio.on("connect")
def connect():
    print("Client connected")


# -------------------------
# FILE UPLOAD
# -------------------------

@app.route("/upload", methods=["POST"])
def upload():

    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files["file"]

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(path)

        return jsonify({"file": filename})

    return jsonify({"error": "Invalid file"}), 400


# -------------------------
# GET STOCKS
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


# -------------------------
# ADD STOCK
# -------------------------

@app.route("/stocks", methods=["POST"])
@limiter.limit("20 per minute")
def add_stock():

    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    name = request.form["name"]
    quantity = request.form["quantity"]
    pipeline = request.form["pipeline"]

    file = request.files["file"]

    filename = None

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    stock = Stock(
        name=name,
        quantity=quantity,
        pipeline=pipeline,
        file=filename
    )

    db.session.add(stock)
    db.session.commit()

    socketio.emit("notification", {
        "message": f"New stock added: {name}"
    })

    return jsonify({"status": "created"})


# -------------------------
# DELETE STOCK
# -------------------------

@app.route("/stocks/<int:id>", methods=["DELETE"])
def delete_stock(id):

    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    stock = Stock.query.get(id)

    if stock:
        db.session.delete(stock)
        db.session.commit()

        socketio.emit("notification", {
            "message": f"Stock deleted: {stock.name}"
        })

    return jsonify({"status": "deleted"})


# -------------------------
# FILE SERVE
# -------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    socketio.run(app, debug=True)