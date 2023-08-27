from app import app
from flask import render_template, redirect, send_from_directory, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import *
import sys
from flask_mail import Mail, Message
import smtplib
import plotly.express as px
from plotly.offline import plot
from plotly.offline import *
import plotly.graph_objs as go
import pandas as pd

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
def landing():
    return render_template('landing.html')

@app.route('/home')
@login_required
def index():
    if current_user.newuser == True:
        flash('Complete the "New Users" Section!', 'success')
        
    payment_methods, payment_methods_preview = view_payment_methods()
    transactions, transactions_preview = view_transactions()
    transaction_info = []
    payment_method_info = []
    line_graph, pie_chart = create_graphs()
    return render_template('index.html', payment_methods = payment_methods, payment_methods_preview = payment_methods_preview, transactions=transactions, transactions_preview = transactions_preview, transaction_info =transaction_info, payment_method_info = payment_method_info, line_graph = line_graph, pie_chart = pie_chart)

@app.route('/login', methods = ['GET', 'POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    user = db.session.query(User).filter_by(email=email).first()
    
    if user is None or not user.check_password(password):
        print(f'Login failed for user: {user.first_name} {user.last_name}', file=sys.stderr)
        print(f'Provided email: {email}', file=sys.stderr)
        print(f'Provided password: {password}', file=sys.stderr)
        print(f'User object: {user}', file=sys.stderr)
        flash('An error occurred when trying to sign-in', 'success')
        return redirect(url_for('landing'))

    login_user(user)
    flash('Login Successful!', 'success')
    print('Login successful', file=sys.stderr)
    return redirect(url_for('index'))
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Read data from form fields
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    password_verification = request.form['password_verification']
        
    user = db.session.query(User).filter_by(email=email).first()
    
    if user is None:
        
        if password == password_verification:
            # Create new user object and add to database
            user = User( first_name=first_name, last_name=last_name, email=email, newuser = True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            print('Sign-up successful', file=sys.stderr)
            
            # email notification of sign-up
            ACCT_EMAIL = email
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(EMAIL_USER, EMAIL_PASSWORD)

                body = f"Subject: Account Created\n\nWelcome to the Finance Tracker, {first_name} {last_name}! Your account information is listed below: \nName: {first_name} {last_name}\nEmail: {email}"
                server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

                server.quit()
            
            except Exception as e:
                return f"Error: {e}" 
            
            flash('Account Created!', 'success')
            return redirect(url_for('landing'))
        
        else:
            flash('An error occurred when trying to sign-up', 'success')
            return redirect(url_for('landing'))

    else:
        # account already created with email.
        print(f'Error: Signup failed for user: {first_name} {last_name}', file=sys.stderr)
        print(f'Provided email: {email} is already being used for an account.', file=sys.stderr)
        flash('An error occurred when trying to sign-up', 'success')
        return redirect(url_for('landing'))
    
@app.route('/newuser', methods=['GET', 'POST'])
@login_required
def new_user():
    if current_user.newuser == True:
        amount = request.form['amount']
        transaction = Transaction(user_id = current_user.id, 
                                title = "Initial Amount", 
                                date = "1/1/2000", 
                                amount = amount, 
                                type = 'deposit', 
                                category = "deposit", 
                                comments = "initial starting balance")
        
        db.session.add(transaction)
        
        csv = request.form['csv']
        statement = pd.read_csv(csv)
        print(csv)
        print(statement)
        
            # extracting vals
        date = statement[['Date']].to_dict('list')
        date_list = list(date['Date'])
        
        amount = statement[['Amount']].to_dict('list')
        amount_list = list(amount['Amount'])
        
        description = statement[['Description']].to_dict('list')
        description_list = list(description['Description'])
        
        length = len(date_list)
        i = 0
        while i < length:
            
            desc_string = description_list[i].split()
            
            if amount_list[i] < 0:
                type = "purchase"
                title = "Purchase"
                
            else:
                type = "deposit"
                title = "Deposit"
                
            category = f'{desc_string[0]} {desc_string[1]}'
            
            if desc_string[0] == "RECURRING":
                
                if desc_string[5] == "ABC*THE":
                    title = f'{desc_string[5]} {desc_string[6]}'
                else:
                    title = desc_string[5]
                category = "SUBSCRIPTION"
                
            elif desc_string[0] == "PURCHASE":
                if desc_string[4] == "SHELL" or desc_string[4] == "CUMBERLAND" or desc_string[4] == "SUNOCO" or desc_string[4] == "EXXON" or desc_string[4] == "PROSPECT":
                    category = "GAS"
                elif desc_string[4] == "McDonalds" or desc_string[4] == "DUNKIN" or desc_string[4] == "CHENG" or desc_string[4] == "TONYS" or desc_string[4] == "BUFFALO" or desc_string[4] == "MINAMI" or desc_string[4] == "AUNTIE" or desc_string[4] == "PANERA" or desc_string[4] == "STORE*WAYBACK" or desc_string[4] == "DOMINO'S" or desc_string[4] == "DOMENIC'S":
                    category = "FOOD"
                else:
                    category = "PURCHASE"
                        
                title = f'{desc_string[4]} {desc_string[5]}'
                
            elif desc_string[0] == "PLANET":
                title = f'{desc_string[0]} {desc_string[1]} {desc_string[2]} {desc_string[3]}'
                category = "SUBSCRIPTION"
                
            elif desc_string[0] == "ONLINE":
                title = 'DEPOSIT'
            
            elif desc_string[0] == "NON-WELLS":
                title = "misc."
                category = "misc."
            
            else:
                title = "misc."
                category = "misc."
                
            transaction = Transaction(user_id = current_user.id, 
                                    title = title,
                                    date = date_list[i], 
                                    amount = amount_list[i],
                                    type = type, 
                                    category = category,
                                    comments = description_list[i])
            db.session.add(transaction)
            i+=1

        current_user.newuser = False
        db.session.commit() 

    else:
        print('not new user.')
    
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('landing'))

@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():     
    new_password = request.form['new_password']
    password_retype = request.form['password_retype']
        
    if new_password != password_retype:
        flash('Passwords do not match.', 'danger')
    else:
        new_password_hash = generate_password_hash(new_password)
        current_user.password = new_password_hash
        db.session.commit()
        flash('Your password has been updated. Please sign in again.', 'success')
        
        # Log user out after changing the password
        logout_user()
        return redirect(url_for('landing'))
    
    return redirect(url_for('index'))

@app.route('/addtransaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
 
    if current_user.newuser == True:
        amount = request.form['amount']
        transaction = Transaction(user_id = current_user.id, 
                                title = "Initial Amount", 
                                date = "1/1/2000", 
                                amount = amount, 
                                type = 'deposit', 
                                category = "deposit", 
                                comments = "initial starting balance")
        db.session.add(transaction)
        current_user.newuser == False
 
    else:
        title = request.form['title']
        date = request.form['date']
        amount = request.form['amount']
        payment_id = request.form['card']
        if payment_id == '':
            payment_id = None
        type = request.form['type']
        category = request.form['category']
        comments = request.form['comments']
            
        # Add transaction to database
        transaction = Transaction(user_id = current_user.id,
                                    payment_id = payment_id, 
                                    title = title, 
                                    date = date, 
                                    amount = amount, 
                                    type = type, 
                                    category = category, 
                                    comments = comments)
        
        db.session.add(transaction)
        
    db.session.commit()
        
    ACCT_EMAIL = current_user.email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        body = f"Subject: Transaction Added\n\n A transaction has been added to your account: \nTitle: {title}\nDate: {date}\n Amount: {amount} \nType: {type}\nCategory: {category} \nComments: {comments} \n has been added to your account."
        server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

        server.quit()
    
    except Exception as e:
        return f"Error: {e}" 

    flash('Transaction Added!', 'success')
    return redirect(url_for('index'))

@app.route('/addpaymentmethod', methods=['GET', 'POST'])
@login_required
def add_payment_method():
    
    number = request.form['number']
    name = request.form['name']
    expiration = request.form['expiration']
    code = request.form['code']
    
    # Add payment method to database
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
    
    flash('Payment Method Added!', 'success')
    return redirect(url_for('index'))  
    
def view_payment_methods():
    all_payment_methods = PaymentMethod.query.filter_by(user_id=current_user.id).all()
    payment_methods = []
    
    for payment_method in all_payment_methods:
        payment_methods.append((payment_method.card_id, payment_method.number, payment_method.name, payment_method.expiration, payment_method.code))
    
    if len(payment_methods) < 3:
        length = len(payment_methods)
        length *= -1
        payment_methods_preview = payment_methods[length:]
    else:   
        payment_methods_preview = payment_methods[-3:]
        
    return payment_methods, payment_methods_preview
    
def view_transactions():
    all_transactions = Transaction.query.order_by(Transaction.id).filter_by(user_id=current_user.id).all()
    transactions = []
    for transaction in all_transactions:
        transactions.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
    
    transactions_preview=[]
    
    if len(transactions) < 3:
        length = len(transactions)
        length *= -1
        transactions_preview = transactions[length:]
    else:   
        transactions_preview.append(transactions[-1])
        transactions_preview.append(transactions[-2])
        transactions_preview.append(transactions[-3])

    return transactions, transactions_preview

def create_graphs():
    # get all transactions
    all_transactions = Transaction.query.order_by(Transaction.id).filter_by(user_id=current_user.id).all()
    transactions = []
    gas = []
    subscriptions = []
    food = []
    purchases = []
    etc = []
    
    x = []
    y = []
    type = []
    amount = []
    titles = []
    
    text = []
    
    gas_total = 0
    subscriptions_total = 0
    food_total = 0
    purchases_total = 0
    
    i = 0
    total = 0
    # sort into lists based on category
    for transaction in all_transactions:
        transactions.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
        text.append(f"{transaction.title}: \n{transaction.comments}")
        titles.append(transaction.title)
        
        if transaction.category != "ONLINE TRANSFER":
            type.append(transaction.category)
            amount.append(transaction.amount)
        
        if transaction.category == "GAS":
            gas.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
            gas_total += abs(transaction.amount)
        
        elif transaction.category == "SUBSCRIPTION":
            subscriptions.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
            subscriptions_total += abs(transaction.amount)
        
        elif transaction.category == "FOOD":
            food.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
            food_total += abs(transaction.amount)
            
        elif transaction.category == "PURCHASE":
            purchases.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
            purchases_total += abs(transaction.amount)
            
        else:
            etc.append((transaction.id, transaction.title, str(transaction.date),transaction.amount, transaction.type, transaction.category, transaction.comments))
        
        total += transaction.amount
        total = round(total, 2)
        i += 1
        x.append(i)
        y.append(total)
        
    # creating graphs
    
    line = [go.Scatter(x=x, 
                        y=y,
                        mode='lines', 
                        name='test',
                        opacity=0.8, 
                        hovertext = titles,
                        marker_color='blue')]
    
    pie = [go.Pie(labels=["Gas", "Subscription", "Food", "Purchase"], 
                       values=[gas_total, subscriptions_total, food_total, purchases_total], 
                       title='Types of Transactions')]

    
    fig = go.Figure(data = line)
    fig.update_layout(
                      plot_bgcolor='#1e1e1e',
                      paper_bgcolor = '#1e1e1e',
                      title_text="Transaction History",
                      font_color="#918e8e"
                      )
    fig.update_xaxes(
                    mirror=True,
                    showline=True,
                    linecolor='#1e1e1e',
                    gridcolor='#1e1e1e',
                    title='Transaction Number'
                    )
    fig.update_yaxes(
                    mirror=True,
                    showline=True,
                    linecolor='#1e1e1e',
                    gridcolor='#1e1e1e',
                    title='Account Balance ($USD)'
                )
    line_graph = plot(fig, output_type = 'div')
    
    fig = go.Figure(data = pie)
    fig.update_layout(
                      plot_bgcolor='#1e1e1e',
                      paper_bgcolor = '#1e1e1e',
                      title_text="Transaction Breakdown",
                      font_color="#918e8e"
                      )
    
    pie_chart = plot(fig, output_type = 'div')
    # return graphs
    return line_graph, pie_chart
    


@app.route('/viewPaymentMethod/<int:payment_method_id>', methods=['GET', 'POST'])
@login_required
def PaymentMethodDetails(payment_method_id):
    payment_method= PaymentMethod.query.filter_by(card_id=payment_method_id).first()
    
    if current_user.id == payment_method.user_id:
        info = [("payment_method",payment_method.card_id, payment_method.number, payment_method.name, payment_method.expiration, payment_method.code)]
        return render_template('details.html', info=info)
    else:
        msg ='You do not have permission to view this transaction'
        return render_template('error.html',msg = msg)

@app.route('/viewTransaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def TransactionDetails(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id).first()

    if current_user.id == transaction.user_id:
        info = [("transaction", transaction.title, transaction.date, transaction.amount, transaction.payment_id, transaction.type, transaction.category, transaction.comments, transaction.id)]
        return render_template('details.html', info=info)
    
    else:
        msg ='You do not have permission to view this transaction'
        return render_template('error.html',msg = msg)

@app.route('/deletePaymentMethod/<int:payment_method_id>', methods=['GET', 'POST'])
@login_required
def DeletePaymentMethod(payment_method_id):
    payment_method = PaymentMethod.query.filter_by(card_id=payment_method_id).first()
    transactions = Transaction.query.filter_by(payment_id = payment_method_id).all()
    for transaction in transactions:
        transaction.payment_id = None
    
    db.session.commit()
    
    if current_user.id == payment_method.user_id:
        PaymentMethod.query.filter(PaymentMethod.card_id == payment_method_id).delete()
        db.session.commit()
    
        info = [(payment_method.card_id, payment_method.number, payment_method.name, payment_method.expiration, payment_method.code)]
        print(f'Payment method with info: {info} has been deleted.')
        
        ACCT_EMAIL = current_user.email
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL_USER, EMAIL_PASSWORD)

            body = f"Subject: Payment Method Deleted\n\n A payment method including the following: \nName: {payment_method.name}\nNumber: {payment_method.number}\n Expiration: {payment_method.expiration} \n has been deleted from your account."
            server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

            server.quit()
        
        except Exception as e:
            return f"Error: {e}" 
        
        flash('Payment Method Deleted!', 'success')
        return redirect(url_for('index'))
        
    else:
        msg ='You do not have permission to delete this payment method'
        return render_template('error.html',msg = msg)

@app.route('/deleteTransaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def DeleteTransaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    
    if current_user.id == transaction.user_id:
        Transaction.query.filter(Transaction.id == transaction_id).delete()
        db.session.commit()
        
        info = [(transaction.title, str(transaction.timestamp),transaction.amount, transaction.type, transaction.category, transaction.comments)]
        print(f'Transaction with info: {info} has been deleted.')
        
        ACCT_EMAIL = current_user.email
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL_USER, EMAIL_PASSWORD)

            body = f"Subject: Transaction Deleted\n\n A transaction has been added to your account: \nTitle: {transaction.title}\nDate: {transaction.date}\n Amount: {transaction.amount} \nType: {transaction.type}\nCategory: {transaction.category} \nComments: {transaction.comments} \n has been deleted from your account."
            server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

            server.quit()
        
        except Exception as e:
            return f"Error: {e}"
    
        flash('Transaction Deleted!', 'success')
        return redirect(url_for('index'))
        
    else:
        msg ='You do not have permission to delete this transaction'
        return render_template('error.html',msg = msg)
    
@app.route('/updateTransaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def UpdateTransaction(transaction_id):
    
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    
    title = request.form['title']
    date = request.form['date']
    amount = request.form['amount']
    payment_id = request.form['card']
    if payment_id == '':
        payment_id = None
    type = request.form['type']
    category = request.form['category']
    comments = request.form['comments']
    
    if current_user.id == transaction.user_id:
        transaction.title = title
        transaction.date = date
        transaction.amount = amount
        transaction.payment_id = payment_id
        transaction.type = type 
        transaction.category = category
        transaction.comments = comments
        db.session.commit()
        
        info = [(transaction.title, str(transaction.timestamp),transaction.amount, transaction.type, transaction.category, transaction.comments)]
        print(f'Transaction with info: {info} has been updated.')
        
        ACCT_EMAIL = current_user.email
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(EMAIL_USER, EMAIL_PASSWORD)

            body = f"Subject: Transaction Updated\n\n A transaction on your account has been updated: \nTitle: {transaction.title}\nDate: {transaction.date}\n Amount: {transaction.amount} \nType: {transaction.type}\nCategory: {transaction.category} \nComments: {transaction.comments} \n"
            server.sendmail(EMAIL_USER, ACCT_EMAIL, body)

            server.quit()
        
        except Exception as e:
            return f"Error: {e}"
    
        flash('Transaction Updated!', 'success')
        info = [("transaction", transaction.title, transaction.date, transaction.amount, transaction.payment_id, transaction.type, transaction.category, transaction.comments, transaction.id)]
        return redirect(url_for("TransactionDetails",transaction_id = transaction.id))
        
    else:
        msg ='You do not have permission to delete this transaction'
        return render_template('error.html',msg = msg)