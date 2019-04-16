from flask import Flask, render_template, request, session, url_for, flash, redirect
import hashlib
from forms import RegistrationForm, LoginForm, ChangePassForm
import pymysql.cursors
'''
Abid Siam
CS-UY 410X
Professor Frankl
Updated: April 15, 2019
New features: update password and username, upload avatar, update bio

****NEED TO CREATE A USER CLASS WHICH CONTAINS EVERYTHING THAT CAN BELONG TO A USER*****

github.com/abid-siam/finstagram-project
'''


app = Flask(__name__)
app.config['SECRET_KEY'] = '71a924bd8cc5c7250a4fd7314f3d2faa'
# session is a dictionary

# connect to the database
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='Finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#==========================================================================
# Encrypt the password field to a 64 bit hexadecimal


def encrypt(strToHash):
    encoded = hashlib.sha256(str.encode(strToHash))
    return encoded.hexdigest()

# Return True if hashed password field matched with database


def verify(strToVerify, compareTo):
    encoded = (hashlib.sha256(str.encode(strToVerify))).hexdigest()
    return (encoded == compareTo)


#===========================================================================
class User():

    def __init__(self, fName, lName, username, password, bio, avatar, isPrivate):
        self.firstName = fName
        self.lastName = lName
        self.username = username
        self.password = password
        self.bio = bio
        self.avatar = avatar
        self.isPrivate = isPrivate
        self.posts = []


@app.route("/")
@app.route("/home")
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))  # need to make the dashboard

    return render_template('home.html', title='Home')

# only accessible if logged in


@app.route('/dashboard')
def dashboard():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    current_user = User(data["fname"], data["lname"], username,
                        data["password"], data["bio"], data["avatar"], data["isPrivate"])

    return render_template('dashboard.html', title='Dashboard', current_user=current_user)


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
            # default the avatar to 'default.jpg', set the profile to public
            ins = 'INSERT INTO Person(fname,lname,username,password,avatar,isPrivate) VALUES(%s,%s,%s,%s,"default.jpg",1)'
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

        cursor = conn.cursor()
        # execute query
        query = cursor.execute("SELECT * FROM Person WHERE username = %s", username)

        if(query > 0):  # the username exists in the database
            # get stored hashed password
            data = cursor.fetchone()
            password_correct = data['password']
            # Compare the passwords
            if verify(password_to_check, password_correct):
                # Valid User
                session['logged_in'] = True
                session['username'] = username
                cursor.close()
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


@app.route("/changePassword", methods=['GET', 'POST'])
def changePassword():
    form = changePassForm()
    # should be logged in already
    # user enters current password
    if 'logged_in' in session:
        if form.validate_on_submit():
            # get information from form
            currentPass = form.currentPass.data
            newPass = form.newPassword.data
            # create cursor
            cursor = conn.cursor()
            # verify current password
            username = session['username']
            query = 'SELECT * FROM Person WHERE username = %s'
            cursor.execute(query, (username))
            # query must return something since the user is already logged in
            data = cursor.fetchone()
            password_correct = data['password']
            if verify(currentPass, password_correct):
                # passwords match, update current password
                newPassHashed = encrypt(newPass)
                query = 'UPDATE Person SET password=%s WHERE username=%s'
                cursor.execute(query, (newPassHashed, username))
                conn.commit()
                cursor.close()
                session.clear()  # must login again
                flash('Your Password Has Been Updated', 'success')
                return redirect(url_for('login'))
            else:
                cursor.close()
                flash('Incorrect Password, Could Not Change Password', 'danger')
                return redirect(url_for('login'))
        return render_template('changePassword', title='Change Password', form=form)
# @app.route("/changeUsername", methods=["GET, POST"])
# def changeUsername():
#     if 'logged_in' in session:
#         form =


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out", "success")
    return redirect(url_for('home'))



#==================================================================================
if __name__ == "__main__":
    app.run(debug=True)
