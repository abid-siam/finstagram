from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField,\
    TextAreaField, SelectMultipleField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
import pymysql.cursors
from connection import *


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        cursor = conn.cursor()
        query = 'SELECT * FROM Person WHERE username = %s'
        cursor.execute(query, (username.data))
        data = cursor.fetchone()
        cursor.close()
        if (data):
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')


class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=20)])
    username = StringField('Username', validators=[Length(min=2, max=20)])
    bio = TextAreaField('Bio', validators=[Length(max=1024)])
    avatar = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != session['username']:
            cursor = conn.cursor()
            query = 'SELECT * FROM Person WHERE username = %s'
            cursor.execute(query, (username.data))
            data = cursor.fetchone()
            if (data):
                raise ValidationError('That username is taken. Please choose a different one.')


class ChangePassForm(FlaskForm):
    currentPass = StringField('Current Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirmNewPass = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('newPassword')])
    submit = SubmitField('Confirm')


class FollowRequestForm(FlaskForm):

    userFollow = StringField('Search for User', validators=[DataRequired()])
    submit = SubmitField('Send Request')

    def validate_userFollow(self, userFollow):
        if userFollow.data == session['username']:
            raise ValidationError('That is your username. Please choose a different one.')
        cursor = conn.cursor()
        query = 'SELECT * FROM Person WHERE username = %s'
        cursor.execute(query, (userFollow.data))
        data = cursor.fetchone()
        if (not data):
            raise ValidationError('The username entered does not exist. Please choose a different one.')
        # check if the follow request has been sent before
        query = 'SELECT acceptedFollow FROM Follow WHERE followeeUsername= %s AND followerUsername=%s'
        cursor.execute(query, (userFollow.data, session['username']))
        data = cursor.fetchone()
        cursor.close()
        print(data)
        if data:  # if accepted, alert you already follow the username, else say your follow request is pending
            if data['acceptedFollow'] == 0:
                raise ValidationError(f'You have already sent a request to {userFollow.data}. The request is pending.')
            else:
                raise ValidationError(f'You already follow {userFollow.data}!')


class ManageRequestForm(FlaskForm):
    select = SelectMultipleField('Select Follow Request', validators=[DataRequired()])
    submit = SubmitField('Accept')


class CreateGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Confirm')


class ManageGroupForm(FlaskForm):
    group = SelectField('Select A Group', coerce=int)
    # newUserForm = FormField(AddUserForm)
    # currentMemberForm = FormField(CurrentMemberForm)
    newUser = StringField('Add Friend Into Group', validators=[DataRequired()])
    # members = SelectMultipleField('Current Members', validators=[Optional()])

    submit = SubmitField('Add to Group')
    # deleteGroup = SubmitField('Delete Group')

    def validate_newUser(self, newUser):
            # cannot add ourselves into group
        if self.newUser.data == session['username']:
            raise ValidationError('That is your username. Please choose a different one.')
        cursor = conn.cursor()
        # check to see if the username entered is in current users followers
        query = 'SELECT * FROM Follow WHERE followerUsername =%s AND followeeUsername =%s AND acceptedFollow =1'
        cursor.execute(query, (session['username'], self.newUser.data))
        data = cursor.fetchone()
        if not data:
            raise ValidationError(f'{self.newUser.data} is not in your Followers.')
        # check to see if the username entered already belongs in the group specified
        query = 'SELECT * FROM Belong WHERE groupName = %s AND groupOwner = %s AND username = %s'
        cursor.execute(query, (self.group.data, session['username'], self.newUser.data))
        data = cursor.fetchone()
        if (data):
            raise ValidationError(f'{self.newUser.data} is already in the {self.group.choices[int(self.group.data)][1]} group!')


class CreatePostForm(FlaskForm):
    image = FileField('Select an Image', validators=[FileAllowed(['jpg', 'png'])])
    caption = TextAreaField('Caption', validators=[Length(max=1024)])
    allFollowers = RadioField('Share With', choices=[('T', 'All Followers'), ('F', 'My Groups (Select Below)')], validators=[DataRequired()])
    groups = SelectMultipleField('Select Groups', coerce=int)  # Will appear if all Followers == False
    submit = SubmitField('Post')

    def validate_groups(self, groups):
        if self.allFollowers.data == 'F' and not groups.data:  # we did not choose a group
            raise ValidationError("You must select at least one group")


