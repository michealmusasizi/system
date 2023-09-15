from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
from flask import request
import MySQLdb


app = Flask(__name__)
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_system'  # Remove spaces from database name

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form: # Add a colon at the end
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQL.cursor.Dictcursor)
        cursor.execute('SELECT * FROM USER WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            if user['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']  # Correct the usage of 'name' key
                session['email'] = user['email']  # Correct the usage of 'email' key
                message = 'Logged in successfully!'
                return redirect(url_for('users'))
            else:
                message = 'Only admin can login'
        else:
            message = 'Please enter correct email / password!'
            return render_template('login.html', message=message)  # Correct the variable name

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('userid',None)
    session.pop('email',None)
    session.pop('name',None)
    return redirect(url_for('login'))

@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQL.cursor.Dictcursor)
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchone()
        return render_template("user.html",users = users)
    return redirect(url_for('login'))
   
@app.route('/view', methods=['GET', 'POST'])  # Correct route path
def view():  # Add missing colon
    if 'loggedin' in session:
        viewuserid = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQL.cursor.Dictcursor)
        cursor.execute('SELECT * FROM USER WHERE userid = %s', (viewuserid,))
        user = cursor.fetchone()
        return render_template('view.html', user=user)  # Correct variable name
    return redirect(url_for('login'))

@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    message = ''
    changepassuserid = None  # Initialize changepassuserid
    if 'loggedin' in session:
        changepassuserid = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_password' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_password']  # Correct variable name
            userid = request.form['userid']
            if not password or not confirm_pass:
                message = 'Please fill out the form!'
            elif password != confirm_pass:
                message = 'Confirm password is not equal!'
            else:
                cursor = mysql.connection.cursor(MySQL.cursor.DictCursor)
                cursor.execute('UPDATE user SET password = %s WHERE userid = %s', (password, userid))  # Fix indentation
                mysql.connection.commit()
                message = 'Password updated!'
        elif request.method == 'POST':  # Move this line to match 'if' condition
            message = 'Please fill out the form!'
    return render_template("password_change.html", message=message, changepassuserid=changepassuserid)
    return redirect(url_for('login'))

@app.route("/delete", methods=['GET'])  # Use 'GET' method
def delete():
    if 'loggedin' in session:
        deleteuserid = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQL.cursor.DictCursor)  # Correct the cursor class name
        cursor.execute('DELETE FROM user WHERE userid = %s', (deleteuserid,))  # Use lowercase 'user' in the query
        mysql.connection.commit()
        return redirect(url_for('users'))  # Redirect to 'users' route
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country = request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        mysql.connection.commit()
        account = cursor.fetchone()
        if account:
            message = 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s)', (userName, email, role, country, password))
            mysql.connection.commit()
            message = 'New user created!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    msg = ''
    if 'loggedin' in session:
        edituserid = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = %s', (edituserid,))
        edituser = cursor.fetchone()

        if request.method == 'POST' and 'name' in request.form and 'role' in request.form and 'country' in request.form:
            userName = request.form['name']
            role = request.form['role']
            country = request.form['country']
            userid = request.form['userid']

            if not re.match(r'^[A-Za-Z0-9]+$', userName):
                msg = 'Name must contain only characters and numbers!'
            else:
                cursor.execute('UPDATE user SET name = %s, role = %s, country = %s WHERE userid = %s', (userName, role, country, edituserid))
                mysql.connection.commit()
                msg = 'User updated!'
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
            
        cursor.close()  # Close the cursor after using it

    return render_template('edit.html', msg=msg, edituserid=edituserid)

if __name__ == '__main__':
   app.run(debug=True)