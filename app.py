from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "skillchain_secret"

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7410",
    database="skillchain"
)
cursor = db.cursor(dictionary=True)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and user["password_hash"] and check_password_hash(user["password_hash"], password):
            session["user"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password"
    return render_template("userlogin.html")

@app.route("/adminlogin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == "admin@example.com" and password == "admin123":
            session["admin"] = email
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid admin credentials"
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            contact_number = request.form.get("phone", None)
            dob = request.form.get("dob", None)
            wallet_address = request.form.get("wallet_address", None)

            user_type = "student"
            membership_status = "inactive"
            salary = 0.00
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            hashed_pw = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO users 
                (name, email, password_hash, contact_number, wallet_address, user_type, membership_status, salary, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, email, hashed_pw, contact_number, wallet_address, user_type, membership_status, salary, created_at))
            db.commit()
            return redirect(url_for("userlogin"))
        except mysql.connector.IntegrityError:
            return "User already exists or email is taken."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", name=session["user"])
    return redirect(url_for("userlogin"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
