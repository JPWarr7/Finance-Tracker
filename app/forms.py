from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, DateField, RadioField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, StopValidation, NumberRange, EqualTo
from wtforms.widgets import CheckboxInput, ListWidget
from enum import Enum

# Login form (subclassed from FlaskForm)
class SignInForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password:', validators=[DataRequired()])
    new_password = PasswordField('New Password:', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password:', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password:')
    
class SignUpForm(FlaskForm):
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])    
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    passwordRetype = PasswordField('Confirm Password: ', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign up')
    
class AddTransactionForm(FlaskForm):
    title = StringField('Title: ',validators=[DataRequired()])
    date = DateField('Transaction Date: ', validators =[DataRequired()], format='%Y-%m-%d')
    amount = IntegerField('Transaction Amount', validators=[DataRequired(), NumberRange(min=.01, max=99999999, message="Please enter a valid transaction amount")])
    card = SelectField('Category: ', choices=[('Personal'),('Business'),('Food'),('Travel'),('Other')]) # implement card option functionality
    type = SelectField('Type: ', choices=[('Purchase'),('Deposit'),('Withdrawal'),('Refund')])
    category = SelectField('Category: ', choices=[('Personal'),('Business'),('Food'),('Travel'),('Other')])
    comments = StringField('Comments (Optional): ')
    submit = SubmitField('Add Transaction')
    
class AddPaymentMethodForm(FlaskForm):
    name = StringField('Cardholder Name: ',validators=[DataRequired()])
    number = IntegerField('Credit Card Number: ', validators=[DataRequired(), NumberRange(min=.01, max=9999_9999_9999_9999, message="Please enter a valid CC (sadly we do not accept American Express cards at this time.)")])
    expiration = DateField('Expiration: ', validators =[DataRequired()], format='%Y-%m')
    code = IntegerField('CVC (the three digits on the back of the card): ', validators=[DataRequired(), NumberRange(min=.01, max=9999)])
    submit = SubmitField('Add Card')

class FilterForm(FlaskForm):
    filt = SelectField('Filter By: ', choices=[('Date'),('Amount'),('Type')])
    filterInput = StringField('Type:', validators=[DataRequired()])
    submit = SubmitField('Filter')

