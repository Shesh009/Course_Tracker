from flask import Flask, render_template, request, url_for, session, redirect, flash
import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

# Function to connect to MySQL
def connect_to_mysql():
    try:
        mysql_config = {
            'host': os.getenv("HOST"),
            'user': os.getenv("USER"),
            'password': os.getenv("PASSWORD_SQL"),
            'database': os.getenv("DATABASE")
        }
        connection = mysql.connector.connect(**mysql_config)
        return connection
    except mysql.connector.Error as err:
        app.logger.error(f"MySQL connection error: {err}")
        return None

# Create tables if they don't exist
def create_tables(connection):
    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CREDENTIALS (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                NAME VARCHAR(255) NOT NULL,
                EMAIL VARCHAR(255) UNIQUE NOT NULL,
                PASSWORD VARCHAR(255) NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS COURSES (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                EMAIL VARCHAR(255) NOT NULL,
                COURSE_NAME VARCHAR(255) NOT NULL,
                MODULE VARCHAR(255) NOT NULL,
                COMPLETED BOOLEAN DEFAULT 0,
                FOREIGN KEY (EMAIL) REFERENCES CREDENTIALS(EMAIL) ON DELETE CASCADE
            );
        """)
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        app.logger.error(f"MySQL table creation error: {err}")

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password == confirm_password:
                connection = connect_to_mysql()
                if connection:
                    create_tables(connection)
                    cursor = connection.cursor()
                    insert_query = "INSERT INTO CREDENTIALS (NAME, EMAIL, PASSWORD) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (name, email, password))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    flash("Registered Successfully", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Database connection failed", "error")
            else:
                flash("Password and confirm password do not match", "error")
        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            flash("Error in registration process. Please try again.", "error")

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM CREDENTIALS WHERE EMAIL=%s AND PASSWORD=%s", (email, password))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if not result:
                flash("Login failed. Invalid email or password.", "error")
            else:
                session['email'] = email
                app.logger.debug(f"User logged in: {email}")
                return redirect(url_for("dashboard"))

    return render_template('login.html', error='')

# Dashboard route
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if "email" in session:
        email = session["email"]
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT NAME FROM CREDENTIALS WHERE EMAIL=%s", (email,))
            name = cursor.fetchone()[0].upper()
            cursor.close()
            connection.close()
            return render_template('dashboard.html', name=name)
        else:
            flash("Database connection failed", "error")
    return redirect(url_for("login"))

# Show route
@app.route('/show', methods=["GET", "POST"])
def show():
    if "email" in session:
        email = session["email"]
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            query = """SELECT COURSE_NAME, COUNT(COURSE_NAME), 
                               CAST(SUM(COMPLETED) AS SIGNED), 
                               CAST((CAST(SUM(COMPLETED) AS SIGNED) / COUNT(COURSE_NAME)) * 100 AS SIGNED) 
                       FROM COURSES WHERE EMAIL=%s GROUP BY COURSE_NAME"""
            cursor.execute(query, (email,))
            result = cursor.fetchall()
            tab = []
            for row in result:
                tab.append([row[0], str(row[1]), str(row[2]), str(row[3]) + "%"])
            cursor.close()
            connection.close()
            return render_template('show.html', data=tab, email=email)
        else:
            flash("Database connection failed", "error")
    return redirect(url_for("login"))

# Add course route
@app.route('/add_course', methods=["GET", "POST"])
def add_course():
    if "email" in session:
        email = session["email"]
        if request.method == "POST":
            course = request.form['name']
            n = int(request.form['number'])
            modules = [request.form[f'module_{i}'] for i in range(1, n + 1)]
            connection = connect_to_mysql()
            if connection:
                cursor = connection.cursor()
                for module in modules:
                    cursor.execute("INSERT INTO COURSES (EMAIL, COURSE_NAME, MODULE, COMPLETED) VALUES (%s, %s, %s, 0)", 
                                   (email, course, module))
                connection.commit()
                cursor.close()
                connection.close()
                flash("Course added successfully", "success")
                return redirect(url_for("add_course"))
            else:
                flash("Database connection failed", "error")
    return render_template('add_course1.html')

# Edit course route
@app.route('/edit', methods=["GET", "POST"])
def edit():
    tab = []
    if "email" in session:
        email = session['email']
        course = session.get('course', '')
        if request.method == "POST":
            course = request.form['name']
            session['course'] = course
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT MODULE, COMPLETED FROM COURSES WHERE EMAIL=%s AND COURSE_NAME=%s", 
                           (email, course))
            result = cursor.fetchall()
            for row in result:
                tab.append([row[0], str(row[1])])
            cursor.close()
            connection.close()
            return render_template('edit.html', data=tab, email=email, course=course)
        else:
            flash("Database connection failed", "error")
    return redirect(url_for("login"))

# Update course status route
@app.route('/update_status/<module>', methods=["POST"])
def update_status(module):
    if "email" in session and "course" in session:
        email = session["email"]
        course = session["course"]
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM COURSES WHERE COURSE_NAME=%s AND EMAIL=%s AND MODULE=%s", 
                           (course, email, module))
            result = cursor.fetchall()

            if result:
                cursor.execute("UPDATE COURSES SET COMPLETED = CASE WHEN COMPLETED = 0 THEN 1 ELSE 0 END WHERE COURSE_NAME=%s AND EMAIL=%s AND MODULE=%s", 
                               (course, email, module))
                connection.commit()
            cursor.close()
            connection.close()
        return redirect(url_for("edit"))
    return redirect(url_for("login"))

# Delete course route
@app.route("/delete_course/<course>", methods=["GET", "POST"])
def delete_course(course):
    if "email" in session:
        email = session['email']
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM COURSES WHERE EMAIL=%s AND COURSE_NAME=%s", (email, course))
            result = cursor.fetchall()

            if result:
                cursor.execute("DELETE FROM COURSES WHERE EMAIL=%s AND COURSE_NAME=%s", (email, course))
                connection.commit()
                flash(f"Course '{course}' deleted", "success")
            cursor.close()
            connection.close()
        return redirect('/show')
    return redirect(url_for("login"))

# Logout route
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Delete account route
@app.route('/delete_account', methods=["GET", "POST"])
def delete_account():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM CREDENTIALS WHERE EMAIL=%s AND PASSWORD=%s", (email, password))
            if cursor.fetchone():
                cursor.execute("DELETE FROM CREDENTIALS WHERE EMAIL=%s AND PASSWORD=%s", (email, password))
                connection.commit()
                flash("Account deleted", "success")
            cursor.close()
            connection.close()
        else:
            flash("Database connection failed", "error")
    return render_template('delete_acc.html')

# Home route
@app.route('/', methods=["GET"])
def hello_world():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
