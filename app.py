from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "expense_tracker_secret"

DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid Credentials")

    # Render login form on GET request
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses WHERE user=?", (session["user"],)).fetchall()
    total = conn.execute("SELECT SUM(amount) FROM expenses WHERE user=?", (session["user"],)).fetchone()[0]
    conn.close()

    if total is None:
        total = 0

    return render_template("dashboard.html", expenses=expenses, total=total)

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        
        conn = get_db_connection()
        conn.execute("INSERT INTO expenses (user, category, amount, date) VALUES (?, ?, ?, ?)", 
                     (session["user"], category, amount, date))
        conn.commit()
        conn.close()
        
        return redirect(url_for("dashboard"))

    return render_template("add_expense.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

def get_expenses_by_date(selected_date):
    # Connect to your SQLite database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # Execute the SQL query to filter expenses by date
    query = "SELECT * FROM expenses WHERE expense_date = ?"
    cursor.execute(query, (selected_date,))
    expenses = cursor.fetchall()  # Get the list of filtered expenses

    conn.close()
    return expenses

@app.route('/filter-expense', methods=['POST'])
def filter_expense():
    selected_date = request.form['expense-date']
    print(f"Selected Date: {selected_date}")  # This will print the selected date
    expenses = get_expenses_by_date(selected_date)
    return render_template('dashboard.html', expenses=expenses)


if __name__ == "__main__":
    app.run(debug=True)
