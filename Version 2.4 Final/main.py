from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
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
        if account:
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
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

            # Show the login form with message (if any)
        return render_template('index.html', msg=msg)
    return render_template('index.html')

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
        cur.execute("INSERT INTO employees(ID) VALUE(%s)", (userID))
        mysql.connection.commit()
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
        cur = mysql.connection.cursor()
        regDetails = request.form
        #resultValue=regDetails['ID']
        #ID = regDetails['ID']
        cur.execute("SELECT MAX(ID) FROM user")
        userID = cur.fetchone()
        first_name = regDetails['fname']
        middle_initial = regDetails['middle']
        last_name = regDetails['lname']
        email = regDetails['email']
        phone_number = regDetails['phone']
        job_title = regDetails['jobSelect']
        cur.execute("UPDATE employees set first_name = %s, middle_initial = %s, last_name = %s, email = %s, phone_number = %s, job_title = %s WHERE ID = %s", (first_name, middle_initial, last_name, email, phone_number, job_title, userID))
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
        if session['jobSelect'] == 'Painter':
            return render_template('homepage.html', username=session['username'])
        elif session['jobSelect'] == "System Admin/Owner" or session['jobSelect'] == "Sr.Painter/Manager":
            return render_template('homeAdmin.html', username=session['username'])
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
        cur = mysql.connection.cursor()
        userDetails = request.form
        ID = session['ID']
        customer_name = userDetails['custName']
        Customer_address = userDetails['address']
        Job_description = userDetails['jobDesc']
        jobCost = userDetails['pcost']
        compDate = userDetails['compDate']

        jobDate = datetime.datetime.strptime(compDate, '%Y-%m-%d')
        #now need to connect it to database and store it


        cur.execute("INSERT INTO jobreport(ID, customer_name, Customer_address,Job_description,jobCost, jobDate) VALUES(%s, %s, %s, %s, %s, %s)" , (ID, customer_name, Customer_address,Job_description,jobCost, jobDate))
        mysql.connection.commit()
        cur.close()
        return render_template('reportSucess.html')
    return render_template('jobreport.html')


@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        userDetails = request.form
        jobid = userDetails['jobid']
        services_description = userDetails['services']
        materials_cost = int(userDetails['mcost'])
        labor_cost = int(userDetails['lcost'])
        total_cost = materials_cost + labor_cost


        cur.execute("UPDATE jobinvoice set services_description = %s, materials_cost = %s, labor_cost = %s, total_cost = %s WHERE jobid = %s", (services_description, materials_cost, labor_cost, total_cost, jobid))
        mysql.connection.commit()
        cur.close()
        return render_template('invoiceSuccess.html')
    return render_template('invoice.html')

@app.route('/jobReportInvoice', methods=['GET', 'POST'])
def jobReportInvoice():
    if request.method == 'POST':
        jobid = request.form['jobid']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobinvoice(jobid) VALUE(%s)", [jobid])
        mysql.connection.commit()
        return render_template('invoice.html', jobid=jobid)


#this is the search one, i edited this
@app.route('/viewreport', methods=['GET', 'POST'])
def viewreport():
    if request.method == 'POST':
        controlLoop = [1]
        userDetails = request.form
        jobid = userDetails['jobid']

        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM jobreport WHERE jobid = %s", [jobid])
        if resultValue > 0:
            userDetails3 = cur.fetchall()
            return render_template('viewreport.html', userDetails=userDetails3, controlLoop=controlLoop)
        msg = "Job Report Does not Exist!"
        return render_template('viewreport.html', msg=msg)
    return render_template('viewreport.html')
#this is the search one
@app.route('/viewInvoice', methods=['GET', 'POST'])
def viewInvoice():
    if request.method == 'POST':
        controlLoop = [1]
        userDetails = request.form
        jobid = userDetails['jobid']

        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM jobinvoice WHERE jobid = %s", [jobid])
        if resultValue > 0:
            userDetails2 = cur.fetchall()
            return render_template('viewInvoice.html', userDetails=userDetails2, controlLoop=controlLoop)
        msg = "Invoice Does not Exist!"
        return render_template('viewInvoice.html', msg=msg)
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
    else:
        msg = "No existing job reports!"

        return render_template('noJobReports.html', msg=msg)

@app.route('/viewallinvoice')
def viewallinvoice():

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM jobinvoice")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('viewallInvoice.html', userDetails=userDetails)
    else:
        msg = "No existing invoices!"

        return render_template('noInvoices.html', msg=msg)

@app.route('/performanceReport', methods=['GET', 'POST'])
def performanceReport():
    if request.method == 'POST':
        userDetails = request.form
        cur = mysql.connection.cursor()

        sDate = userDetails['startDate']
        eDate = userDetails['endDate']
        startDate = datetime.datetime.strptime(sDate, '%Y-%m-%d')
        endDate = datetime.datetime.strptime(eDate, '%Y-%m-%d')

        resultValue = cur.execute("SELECT * FROM jobreport WHERE jobDate BETWEEN %s AND %s", (startDate, endDate))
        controlLoop = [1]
        if resultValue > 0:
            results = cur.fetchall()
            listResults = [list(i) for i in results]

            results2 = []
            sum = 0
            for row in results:
                sum += row[5]
                cur.execute("SELECT * FROM jobinvoice WHERE jobid = %s", [row[0]])
                tempResults = cur.fetchall()
                if tempResults:
                    results2.append(tempResults[0])

            listResults2 = [list(i) for i in results2]


            for i in range(len(listResults)):
                #for j in range(len(i)):
                    for k in range(len(listResults2)):
                       # for m in range(len(k)):
                            if listResults[i][0] == listResults2[k][1]:
                                listResults[i] = listResults[i] + listResults2[k]

            materialsSum = 0
            materialsCount = 0
            laborSum = 0
            laborCount = 0
            for row in listResults:
                if len(row) > 7:
                    if row[10] > 0:
                        materialsSum += row[10]
                        materialsCount += 1
                    if row[11] > 0:
                        laborSum += row[11]
                        laborCount += 1

            averageMaterials = materialsSum / materialsCount
            averageLabor = laborSum / laborCount
            resultsLength = len(listResults)

            return render_template('performanceReport.html', averageMaterials=averageMaterials, averageLabor=averageLabor, listResults=listResults, resultsLength=resultsLength, results=results, controlLoop=controlLoop, results2=results2, sum=sum, materialsSum=materialsSum, laborSum=laborSum, sDate=sDate, eDate=eDate)
        msg = "No Job Reports or Invoices to Generate Performance Reports from!"
        return render_template('performanceReport.html', msg=msg)
    return render_template('performanceReport.html')

@app.route('/viewEmployees')
def viewEmployees():

    cur = mysql.connection.cursor()
    ID = session['ID']
    resultValue = cur.execute("SELECT * FROM employees WHERE NOT ID = %s", [ID])
    if resultValue > 0:
        employeeDetails = cur.fetchall()
        return render_template('viewEmployees.html', employeeDetails=employeeDetails)
    else:
        msg = "No existing employees!"

        return render_template('viewEmployees.html', msg=msg)

@app.route('/editProfile', methods=['GET', 'POST'])
def editProfile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE ID = %s', (session['ID'],))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM employees WHERE ID = %s', (session['ID'],))
    account2 = cursor.fetchone()

    if request.method == 'POST':
        userDetails = request.form;

        if 'username' in userDetails:
            username = 1
            return render_template('editProfile.html',account=account, account2=account2, username=username)
        elif 'first_name' in userDetails:
            first_name = 1
            return render_template('editProfile.html', account=account, account2=account2, first_name=first_name)
        elif 'middle_initial' in userDetails:
            middle_initial = 1
            return render_template('editProfile.html', account=account, account2=account2, middle_initial=middle_initial)
        elif 'last_name' in userDetails:
            last_name = 1
            return render_template('editProfile.html', account=account, account2=account2, last_name=last_name)
        elif 'email' in userDetails:
            email = 1
            return render_template('editProfile.html', account=account, account2=account2, email=email)
        elif 'phone_number' in userDetails:
            phone = 1
            return render_template('editProfile.html', account=account, account2=account2, phone=phone)
        elif 'password' in userDetails:
            password = 1
            return render_template('editProfile.html', account=account, account2=account2, password=password)

        return render_template('profile.html', account=account, account2=account2)

    return render_template('editProfile.html', account=account, account2=account2)

@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute('SELECT * FROM user WHERE ID = %s', (session['ID'],))
    account = cur.fetchone()
    cur.execute('SELECT * FROM employees WHERE ID = %s', (session['ID'],))
    account2 = cur.fetchone()

    if request.method == 'POST':
        userDetails = request.form;
        if 'newUsername' in userDetails:
            username = userDetails['newUsername']
            ID = userDetails['newUserID']
            cur.execute('UPDATE user SET username = %s WHERE ID = %s', (username, ID))
            mysql.connection.commit()
            cur.close()

            userMsg = "Username Successfully Updated!"
            return render_template('updateProfileSuccess.html', userMsg=userMsg)
        elif 'newFirstName' in userDetails:
            first_name = userDetails['newFirstName']
            ID = userDetails['newfnUserID']
            cur.execute('UPDATE employees SET first_name = %s WHERE ID = %s', (first_name, ID))
            mysql.connection.commit()
            cur.close

            fn = "First Name Successfully Updated!"
            return render_template('updateProfileSuccess.html', fn=fn)
        elif 'newMiddleInitial' in userDetails:
            middle_initial = userDetails['newMiddleInitial']
            ID = userDetails['newmUserID']
            cur.execute('UPDATE employees SET middle_initial = %s WHERE ID = %s', (middle_initial, ID))
            mysql.connection.commit()
            cur.close

            mi = "Middle Initial Successfully Updated!"
            return render_template('updateProfileSuccess.html', mi=mi)
        elif 'newLastName' in userDetails:
            last_name = userDetails['newLastName']
            ID = userDetails['newlnUserID']
            cur.execute('UPDATE employees SET last_name = %s WHERE ID = %s', (last_name, ID))
            mysql.connection.commit()
            cur.close

            ln = "Last Name Successfully Updated!"
            return render_template('updateProfileSuccess.html', ln=ln)
        elif 'newEmail' in userDetails:
            email = userDetails['newEmail']
            ID = userDetails['newEmailID']
            cur.execute('UPDATE employees SET email = %s WHERE ID = %s', (email, ID))
            mysql.connection.commit()
            cur.close

            emailMsg = "Email Successfully Updated!"
            return render_template('updateProfileSuccess.html', emailMsg=emailMsg)
        elif 'newPhone' in userDetails:
            phone_number = userDetails['newPhone']
            ID = userDetails['newPhoneID']
            cur.execute('UPDATE employees SET phone_number = %s WHERE ID = %s', (phone_number, ID))
            mysql.connection.commit()
            cur.close

            phoneMsg = "Phone Number Successfully Updated!"
            return render_template('updateProfileSuccess.html', phoneMsg=phoneMsg)
        elif 'oldPassword' in userDetails:
            oldPassword = userDetails['oldPassword']
            ID = userDetails['oldPasswordID']
            cur.execute("SELECT * FROM user WHERE password = %s AND ID = %s", (oldPassword, ID))
            results = cur.fetchall()
            if results:
                cur.close()
                password = 2
                return render_template('editProfile.html', account=account, account2=account2, password=password)

            else:
                incorrectmsg = "Incorrect Password!"
                return render_template('editProfile.html', incorrectmsg=incorrectmsg)
        elif 'newPassword' in userDetails:
            newPassword = userDetails['newPassword']
            ID = userDetails['newPasswordID']
            cur.execute('UPDATE user SET password = %s WHERE ID = %s', (newPassword, ID))
            mysql.connection.commit()
            cur.close

            passwordMsg = "Password Successfully Updated!"
            return render_template('updateProfileSuccess.html', passwordMsg=passwordMsg)

if __name__ == '__main__':
    app.run(debug=True)