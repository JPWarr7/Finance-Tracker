from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    newuser = db.Column(db.Boolean)

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

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number =  db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    expiration =  db.Column(db.String(8), nullable=False)
    code = db.Column(db.String(3), nullable=False)
    
class Transaction(db.Model):
    __tablename__ = 'transaction'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment_method.card_id'))
    title = db.Column(db.String(50), nullable=False)
    date =  db.Column(db.String(12), nullable=False)
    amount =  db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    comments = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    