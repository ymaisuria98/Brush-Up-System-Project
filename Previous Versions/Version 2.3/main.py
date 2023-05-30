from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# this code below is for the style sheet
app = Flask(__name__, static_folder='static')
#app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

# Intialize MySQL
mysql = MySQL(app)





@app.route('/', methods=['GET', 'POST'])

def index():
    return render_template('index.html')

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/index', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

 # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        #Job_title = request.form['Job_title']
    # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))



        account = cursor.fetchone()
        id = account['ID']

        cursor.execute('SELECT * FROM employees WHERE ID = %s', [id])

        account2 = cursor.fetchone()


   # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['ID'] = account['ID']
            session['username'] = account['username']
            session['jobSelect'] = account2['job_title']
            # Redirect to home page
            if session['jobSelect'] == 'Painter':
                return redirect(url_for('home'))
            elif session['jobSelect'] == "System Admin/Owner" or session['jobSelect'] == "Sr.Painter/Manager":
                return render_template('homeAdmin.html')
            return  redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

            # Show the login form with message (if any)
        return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('ID', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('index'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST':

        # fetch form data
        regDetails = request.form
        username = regDetails['user']
        password = regDetails['pword']
        security_question_one = regDetails['answer1']
        security_question_two = regDetails['answer2']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(username, password, security_question_one, security_question_two) VALUES(%s, %s, %s, %s)" , (username, password, security_question_one, security_question_two))
        mysql.connection.commit()
        cur.execute("SELECT MAX(ID) FROM user")
        userID = cur.fetchone()
        ID = ''
        for item in userID:
            ID = ID + str(item)
        cur.close()
        return render_template('employeeRegister.html', ID=ID)
    return render_template('register.html')

#adding this
@app.route('/employeeRegister', methods =['GET', 'POST'])
def employeeRegister():

    if request.method == 'POST':
        # fetch form data
        regDetails = request.form
        #resultValue=regDetails['ID']
        ID = regDetails['ID']
        first_name = regDetails['fname']
        middle_initial = regDetails['middle']
        last_name = regDetails['lname']
        email = regDetails['email']
        phone_number = regDetails['phone']
        job_title = regDetails['jobSelect']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employees(ID, first_name, middle_initial, last_name,email, phone_number, job_title) VALUES(%s, %s, %s,%s, %s, %s,%s)" , (ID, first_name, middle_initial, last_name, email, phone_number, job_title))
        mysql.connection.commit()
        cur.close()

        return render_template('registerResult.html')

    return render_template('employeeRegister.html')

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users

@app.route('/homepage')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('homepage.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:

        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE ID = %s', (session['ID'],))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM employees WHERE ID = %s', (session['ID'],))
        account2 = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account, account2=account2 )
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#new code below
@app.route('/jobreport', methods =['GET', 'POST'])
def jobreport():
    if request.method == 'POST':
        #fetch form data
        userDetails = request.form
        customer_name = userDetails['custName']
        Customer_address = userDetails['address']
        Job_description = userDetails['jobDesc']
        jobCost = userDetails['pcost']
        #now need to connect it to database and store it

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobreport(customer_name, Customer_address,Job_description,jobCost) VALUES(%s, %s, %s, %s)" , ( customer_name, Customer_address,Job_description,jobCost))
        mysql.connection.commit()
        cur.close()
        return render_template('reportSucess.html')
    return render_template('jobreport.html')


@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        userDetails = request.form
        jobid = userDetails['jobid']
        services_description = userDetails['services']
        materials_cost = userDetails['mcost']
        labor_cost = userDetails['lcost']
        total_cost = userDetails['tcost']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobInvoice(jobid, services_description, materials_cost, labor_cost, total_cost) VALUES(%s, %s, %s, %s, %s)", (jobid, services_description, materials_cost, labor_cost, total_cost))
        mysql.connection.commit()
        cur.close()
        return render_template('invoiceSuccess.html')
    return render_template('invoice.html')

#this is the search one, i edited this
@app.route('/viewreport', methods=['GET', 'POST'])
def viewreport():
    if request.method == 'POST':
        userDetails = request.form
        jobid = userDetails['jobid']

        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM jobreport WHERE jobid = %s", [jobid])
        if resultValue > 0:
            userDetails3 = cur.fetchall()
            return render_template('viewreport.html', userDetails=userDetails3)
    return render_template('viewreport.html')
#this is the search one
@app.route('/viewInvoice', methods=['GET', 'POST'])
def viewInvoice():
    if request.method == 'POST':
        userDetails = request.form
        jobid = userDetails['jobid']

        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM jobInvoice WHERE jobid = %s", [jobid])
        if resultValue > 0:
            userDetails2 = cur.fetchall()
            return render_template('viewInvoice.html', userDetails=userDetails2)
    return render_template('viewInvoice.html')

@app.route('/reportSucess')
def reportSucess():

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM jobreport")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('reportSucess.html', userDetails=userDetails)
#added the code below, needed an admin homepage for function

@app.route('/homeAdmin')
def homeAdmin():
    # Check if user is loggedin
    if 'loggedin' in session:
            # User is loggedin show them the home page
        return render_template('homeAdmin.html', username=session['username'])
        # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#also added this to view all job reports

@app.route('/viewalljobreport')
def viewalljobreport():

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM jobreport")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('viewalljobreport.html', userDetails=userDetails)


@app.route('/viewallinvoice')
def viewallinvoice():

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM jobInvoice")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('viewallInvoice.html', userDetails=userDetails)



if __name__ == '__main__':
    app.run(debug=True)