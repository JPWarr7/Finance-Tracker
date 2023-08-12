from app import app
from flask import render_template, redirect, send_from_directory, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import SignUpForm, SignInForm, ChangePasswordForm, FilterForm, AddTransactionForm, AddPaymentMethodForm
from app import db
from app.models import *
import sys
from datetime import datetime
from enum import Enum
from flask_mail import Mail, Message
import smtplib

# mail send
mail = Mail(app)

# Replace these values with your email credentials
EMAIL_USER = 'jonathanwarren2022@gmail.com'
EMAIL_PASSWORD = 'yzihkihuimvikfkw'

def send_mail(addr, msg):
    recipient = addr
    message = msg
    subject = 'Test Flask email'
    msg = Message(subject, recipients=[recipient], body = message)
    mail.send(msg)

# @app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/send_email', methods=['POST'])
# def send_email():
#     name = request.form['name']
#     email = request.form['email']
#     message = request.form['message']

# @app.route('/login', methods = ['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            print(f'Login failed for user: {user.first_name} {user.last_name}', file=sys.stderr)
            print(f'Provided email: {form.email.data}', file=sys.stderr)
            print(f'Provided password: {form.password.data}', file=sys.stderr)
            print(f'User object: {user}', file=sys.stderr)
            return redirect(url_for('signin'))

        login_user(user)
        print('Login successful', file=sys.stderr)
        return render_template('index.html')
    
    return render_template('signin.html', form=form)

# @app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        # Read data from form fields
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
      
        # Create new user object and add to database
        user = User( first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('signin'))
    
    # Render signup form template
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if not check_password_hash(user.password, form.current_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            new_password_hash = generate_password_hash(form.new_password.data)
            user.password = new_password_hash
            db.session.commit()
            flash('Your password has been updated. Please sign in again.', 'success')
            
            # Log user out after changing the password
            logout_user()
            return redirect(url_for('signin'))
        
    return render_template('changepassword.html', form=form)

@app.route('/addtransaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = AddTransactionForm()
    if form.validate_on_submit():
        # Data collection from form
        # title = form.title.data
        # date = form.date.data
        # amount = form.amount.data
        # # Note: card functionality needs implementation
        # card = form.card.data
        # type = form.type.data
        # category = form.category.data
        # comments = form.comments.data
        title = request.form['title']
        date = request.form['date']
        amount = request.form['amount']
        card = request.form['card']
        type = request.form['type']
        category = request.form['category']
        comments = request.form['comments']
            
        # Add transaction to database
        transaction = Transaction(user_id = current_user.id, 
                                  title = title, 
                                  date = date, 
                                  amount = amount, 
                                  card = card,
                                  type = type, 
                                  category = category, 
                                  comments = comments)
        
        db.session.add(transaction)
        db.session.commit()
        
    ACCT_EMAIL = current_user.email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        body = f"Subject: Transaction Added\n\n A transaction has been added to your account: \nTitle: {title}\nDate: {date}\n Amount: {amount} \nCard: {card}\nType: {type}\nCategory: {category} \nComments: {comments} \n has been added to your account."
        server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

        server.quit()
    
    except Exception as e:
        return f"Error: {e}" 

    return redirect(url_for('index'))

@app.route('/addpaymentmethod', methods=['GET', 'POST'])
@login_required
def add_payment_method():
    
    name = request.form['name']
    number = request.form['number']
    expiration = request.form['expiration']
    code = request.form['code']
    
            # Add transaction to database
    payment_method = PaymentMethod(user_id = current_user.id, 
                                number = number, 
                                name = name, 
                                expiration = expiration,
                                code = code)
    db.session.add(payment_method)
    db.session.commit()

    ACCT_EMAIL = current_user.email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        body = f"Subject: Payment Method Added\n\n A payment method including the following: \nName: {name}\nNumber: {number}\n Expiration: {expiration} \n has been added to your account."
        server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

        server.quit()
    
    except Exception as e:
        return f"Error: {e}" 
    
    return redirect(url_for('index'))  
    
    
    # form = AddPaymentMethodForm()
    # if form.validate_on_submit():
    #     # Data collection from form
    #     name = form.name.data
    #     number = form.number.data
    #     expiration = form.expiration.data
    #     # Note: card functionality needs implementation
    #     code = form.code.data
        
    #     # Add transaction to database
    #     payment_method = PaymentMethod(user_id = current_user.id, 
    #                               number = number, 
    #                               name = name, 
    #                               expiration = expiration)
        
    #     db.session.add(payment_method)
    #     db.session.commit()
        
        # return redirect(url_for('index'))
    