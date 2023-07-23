# app.py
import os
import re
import uuid
import bcrypt
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session,url_for, flash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MySQL configurations
db_config = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USERNAME'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# app.py (continuation)
@app.route("/")
def login_page():
    return render_template("login.html")

# app.py (updated)
@app.route("/signup")
def signup_page():
    return render_template("signup.html")



@app.route("/signup", methods=["POST"])
def signup():
    id = uuid.uuid4().hex[:16]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    email_pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"

    if not re.match(email_pattern, email):
        return {"success": False, "message": "Please enter a valid email address."}
    
    if not len(password.split())<8:
        print(password)
        return {"success": False, "message": "Length of password shall be between 8 to 20 characters"}

    # Perform validation (you can add more validation checks)
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    cursor.execute("INSERT INTO users (id, email, password) VALUES (%s,%s, %s)", (id, email, hashed_password))
    conn.commit()

    return {"success": True, "message": "Sign-up successful!"}

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"].encode('utf-8')

        # Perform authentication with MySQL (you should properly hash passwords in a real application)
        cursor.execute(f"SELECT password FROM users WHERE email = '{email}';")
        user = cursor.fetchone()
        if user:
            stored_password = user[0].encode('utf-8')
            if bcrypt.checkpw(password, stored_password):
                session["user_id"] = user[0]  
                return {"success": True}
            else:
                return {"success": False}
        else:
            return {"success": False}
    else:
        return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in
    if "user_id" in session:
        # Fetch user data from MySQL if needed
        # user_id = session["user_id"]
        # cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        # user = cursor.fetchone()
        # return render_template("dashboard.html", user=user)
        return f"Hello, {session['user_id']}! <a href='/logout'>Logout</a>"
    else:
        return redirect("/")
    

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id')
    print("Session : ", session)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

