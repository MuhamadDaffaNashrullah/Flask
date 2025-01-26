from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)

# Konfigurasi
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Inisialisasi database dan modul tambahan
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin' atau 'user'

class Pesanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    email = db.Column(db.String(100))
    tanggal = db.Column(db.String(100))
    jumlah = db.Column(db.Integer)
    produk = db.Column(db.String(100))
    harga = db.Column(db.Float)
    total_harga = db.Column(db.Float)
    pesan = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('index.html')

@app.route('/contact')
@login_required
def contact():
    return render_template("contact.html")

@app.route('/cart')
@login_required
def cart():
    return render_template("cart.html")

@app.route('/checkout')
@login_required
def checkout():
    return render_template("checkout.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                flash("Selamat datang, Admin!", "success")
            else:
                flash("Selamat datang, Pembeli!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login gagal. Periksa username dan password.", "danger")
    return render_template('Login.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Tambahkan admin jika belum ada
        if not User.query.filter_by(username="admin").first():
            hashed_password = bcrypt.generate_password_hash("admin123").decode("utf-8")
            admin_user = User(username="admin", password=hashed_password, role="admin")
            db.session.add(admin_user)

        # Tambahkan pembeli (user) jika belum ada
        if not User.query.filter_by(username="pembeli").first():
            hashed_password = bcrypt.generate_password_hash("pembeli123").decode("utf-8")
            buyer_user = User(username="pembeli", password=hashed_password, role="user")
            db.session.add(buyer_user)

        db.session.commit()

    app.run(debug=True)
