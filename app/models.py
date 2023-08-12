from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_active(self):
        # return True if the user is active
        return True
    
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    title = db.Column(db.String(50), nullable=False)
    date =  db.Column(db.Date, nullable=False)
    amount =  db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number =  db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    expiration =  db.Column(db.Date, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    
# note: find encryption method for first 12 digits of CC