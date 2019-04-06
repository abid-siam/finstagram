from flask import Flask, render_template, request, session, url_for, flash, redirect
import hashlib
from forms import RegistrationForm, LoginForm
import pymysql.cursors

'''
Abid Siam
CS-UY 410X
Professor Frankl
Updated: April 5, 2019
github.com/abid-siam/finstagram-project
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '71a924bd8cc5c7250a4fd7314f3d2faa'
# session is a dictionary
# sha256 encrypts strings to 64 bits

# connect to the database
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='Finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#==========================================================================
# Encrypt the password field to a 64 but hexadecimal


def encrypt(strToHash):
    encoded = hashlib.sha256(str.encode(strToHash))
    return encoded.hexdigest()

# Return True if hashed password field matched with database


def verify(strToVerify, compareTo):
    encoded = (hashlib.sha256(str.encode(strToVerify))).hexdigest()
    print("Compare1: ", encoded, end='\n')
    print("Compare2: ", compareTo, end='\n')
    return (encoded == compareTo)

#===========================================================================


@app.route("/")
@app.route("/home")
def home():
    print("In here\n")
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))  # need to make the dashboard

    return render_template('home.html', title='Home')

# only accessible if logged in


@app.route('/dashboard')
def dashboard():
    username = session['username']
    cursor = conn.cursor()
    return render_template('dashboard.html', title='Dashboard', username=username)


@app.route("/about")
def about():
    # Will contain project information
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # the function valifate_on_submit() is a member function of FlaskForm
        # check that the user information doesn't already exist
        firstName = form.first_name.data
        lastName = form.last_name.data
        username = form.username.data
        password_hashed = encrypt(form.password.data)
        # create and execute query
        cursor = conn.cursor()
        query = 'SELECT * FROM Person WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        if (data):  # there is already a username with the one given in the registration form
            flash('The Username Is Already Taken! Try Another One', 'danger')
            cursor.close()
        else:  # the username is unique and does not exist in the database
            ins = 'INSERT INTO Person(fname,lname,username,password) VALUES(%s,%s,%s,%s)'
            cursor.execute(ins, (firstName, lastName, username, password_hashed))
            # save changes to database
            conn.commit()
            cursor.close()
            # notify the user of successful creation of account
            flash(f'Account created for {form.username.data}! You can now login', 'success')  # the second argument taken by the flash function indicates the type of result our message is

            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # no errors when inputting data and no empty fields
        # fetch data from the form
        username = form.username.data
        password_to_check = form.password.data
        print("The username is: ", username, end='\n')
        print("The password is: ", password_to_check, end='\n')

        cursor = conn.cursor()
        # execute query
        query = cursor.execute("SELECT * FROM Person WHERE username = %s", username)

        if(query > 0):  # the username exists in the database
            # get stored hashed password
            data = cursor.fetchone()
            password_correct = data['password']
            # Compare the passwords
            if verify(password_to_check, password_correct):
                print("They match!!\n")
                # Valid User
                session['logged_in'] = True
                session['username'] = username

                flash("You Have Successfuly Logged in", "success")
                return redirect(url_for("dashboard"))
            else:  # passwords do not match
                flash('Login Unsuccessful. Please check username and password', 'danger')
                # we don't want to flash the password being incorrect, but just highliight it and display it as an error underneath the password field

            # close connection
            cursor.close()
        else:  # no results with the specified username in the database
            flash('Login Unsuccessful. No Account Exists With That Username', 'danger')
            cursor.close()

    return render_template('login.html', title='Login', form=form)


#==================================================================================
if __name__ == "__main__":
    app.run(debug=True)
