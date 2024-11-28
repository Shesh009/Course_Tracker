from flask import Flask, flash, render_template, request,url_for,session,redirect
import mysql.connector
from tabulate import tabulate
import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key=os.urandom(24)
load_dotenv()

def connect_to_mysql():
    mysql_config = {
        'host': os.getenv("HOST"),
        'user': os.getenv("USER"),
        'password': os.getenv("PASSWORD_SQL"),
        'database': os.getenv("DATABASE")
    }
    connection = mysql.connector.connect(**mysql_config)
    return connection

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

@app.route('/dashboard',methods=["GET","POST"])
def dashboard():
    if "email" in session:
        email=session["email"]
        query = f"SELECT NAME FROM CREDENTIALS WHERE (EMAIL='{email}')"
        connection = connect_to_mysql()
        cursor = connection.cursor()
        cursor.execute(query)
        name = cursor.fetchone()[0].upper()
        cursor.close()
        connection.close()
        return render_template('dashboard.html',name=name)
    else:
        return redirect("/login")


@app.route('/show', methods=["GET", "POST"])
def show():
    if "email" in session:
        email=session["email"]
        query=f'''SELECT COURSE_NAME,COUNT(COURSE_NAME),CAST(SUM(COMPLETED) AS SIGNED),
                CAST((CAST(SUM(COMPLETED) AS SIGNED)/COUNT(COURSE_NAME))*100 AS SIGNED)
            FROM COURSES 
            WHERE EMAIL="{email}"
            GROUP BY COURSE_NAME'''
        connection = connect_to_mysql()
        cursor = connection.cursor()
        cursor.execute(query)
        result=cursor.fetchall()
        tab=[]
        if result:
                for i in result:
                    tab.append([i[0],str(i[1]),str(i[2]),str(i[3])+"%"])
        connection.commit()
        cursor.close()
        connection.close()
    else:
        return redirect(url_for("login"))
    return render_template('show.html',data=tab,email=email)


@app.route('/edit',methods=["GET","POST"])
def edit():
    tab=[]
    if "email" in session:
        email=session['email']
        course = session.get('course', '')
        if request.method=="POST":
            course=request.form['name']
            session['course']=course
        select = f"SELECT MODULE,COMPLETED FROM COURSES WHERE (EMAIL='{email}' AND COURSE_NAME='{course}')"
        connection = connect_to_mysql()
        cursor = connection.cursor()
        cursor.execute(select)
        result = cursor.fetchall()
        if result:
            for i in result:
                tab.append([i[0],str(i[1])])
        cursor.close()
        connection.close()
        return render_template('edit.html',data=tab,email=email,course=course)
    else:
        return redirect(url_for("login"))


def course_progress(email, course):
    select_query = f"SELECT MODULE, COMPLETED FROM COURSES WHERE (EMAIL='{email}' AND COURSE_NAME='{course}')"
    connection = connect_to_mysql()
    cursor = connection.cursor()
    cursor.execute(select_query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@app.route('/add_course', methods=["GET", "POST"])
def add_course():
    if "email" in session:
        email = session["email"]
        if request.method == "POST":
            course = request.form['name']
            n = int(request.form['number'])
            inputs = [request.form[f'module_{i}'] for i in range(1, n + 1)]
            for i in range(n):
                query = f"INSERT INTO COURSES (EMAIL, COURSE_NAME,MODULE,COMPLETED) VALUES ('{email}','{course}','{inputs[i]}',0)"
                connection = connect_to_mysql()
                cursor=connection.cursor()
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
        return render_template('add_course1.html')
    else:
        return redirect(url_for("login"))



@app.route('/', methods=["GET", "POST"])
def hello_world():
    session.pop('email', None)
    if request.method == "POST":
        print("posted")
    return render_template('index.html')

@app.route('/about_us', methods=["GET", "POST"])
def about_us():
    return render_template('about.html')



@app.route('/delete_module/<module>', methods=["POST"])
def delete_module(module):
    if "email" in session and "course" in session:
        email = session["email"]
        course = session["course"]

        if request.method == "POST":
            connection = connect_to_mysql()
            cursor = connection.cursor()

            try:
                select_query = f"SELECT * FROM COURSES WHERE COURSE_NAME='{course}' AND EMAIL='{email}' AND  MODULE='{module}'"
                cursor.execute(select_query)
                result = cursor.fetchall()

                if result:
                    delete_query = f"DELETE FROM COURSES WHERE COURSE_NAME='{course}' AND EMAIL='{email}' AND MODULE='{module}'"
                    cursor.execute(delete_query)
                    connection.commit()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()

        return redirect(url_for("edit"))
    else:
        return redirect(url_for("login"))

@app.route('/update_status/<module>', methods=["POST"])
def update_status(module):
    if "email" in session and "course" in session:
        email = session["email"]
        course = session["course"]

        if request.method == "POST":
            connection = connect_to_mysql()
            cursor = connection.cursor()

            try:
                select_query = f"SELECT * FROM COURSES WHERE COURSE_NAME='{course}' AND EMAIL='{email}' AND  MODULE='{module}'"
                cursor.execute(select_query)
                result = cursor.fetchall()

                if result:
                    update_query = f"UPDATE COURSES SET COMPLETED = CASE WHEN COMPLETED = 0 THEN 1 ELSE 0 END WHERE COURSE_NAME='{course}' AND EMAIL='{email}' AND MODULE='{module}'"
                    cursor.execute(update_query)
                    connection.commit()
            except Exception as e:
                print(f"Error: {e}")
            select_query = f"SELECT * FROM COURSES WHERE COURSE_NAME='{course}' AND EMAIL='{email}'"
            cursor.execute(select_query)
            result = cursor.fetchall()
            cursor.close()
            connection.close()
        return redirect(url_for("edit"))
    else:
        return redirect(url_for("login"))

@app.route("/delete_course/<course>",methods=["GET","POST"])
def delete_course(course):
        if "email" in session:
            email=session['email']
            if request.method=="POST":
                connection = connect_to_mysql()
                cursor = connection.cursor()
                try:
                    select_query = f"SELECT * FROM COURSES WHERE EMAIL= '{email}' AND COURSE_NAME='{course}'"
                    cursor.execute(select_query)
                    result = cursor.fetchall()

                    if result:
                        delete_query = f"DELETE FROM COURSES WHERE EMAIL= '{email}' AND COURSE_NAME='{course}'"
                        cursor.execute(delete_query)
                        connection.commit()
                        return redirect('/show')
                except:
                    print("No such record")
                cursor.close()
                connection.close()
            return redirect('/show')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/delete_account',methods=["GET","POST"])
def delete_account():
        if request.method=="POST":
            email=request.form["email"]
            password=request.form["password"]
            connection = connect_to_mysql()
            cursor = connection.cursor()
            try:
                select=f"SELECT * FROM CREDENTIALS WHERE (EMAIL='{email}' and PASSWORD='{password}')"
                cursor.execute(select)
                if cursor.fetchone():
                    query = f"DELETE FROM CREDENTIALS WHERE (EMAIL='{email}' and PASSWORD='{password}')"
                    cursor.execute(query)
                    connection.commit()
                    print("Account deleted\n")
                else:
                    print("No matching account found\n")
            except Exception as e:
                print(f"Error: {e}")
            cursor.close()
            connection.close()
        return render_template('delete_acc.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=5000)
