import postgresqlite
import flask
import flask_sqlalchemy
import datetime
from flask_login import UserMixin

db = flask_sqlalchemy.SQLAlchemy()

participants = db.Table(
    'participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('meal_id', db.Integer, db.ForeignKey('meals.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    cooking_balance = db.Column(db.Integer, default=0)
    expenses_balance = db.Column(db.Float, default=0.0)

    def calculate_balances(self, meals):
        self.cooking_balance = sum(len(meal.participants)
                                   for meal in meals if meal.cook == self.name)
        self.expenses_balance = sum(meal.total_expenses / len(meal.participants) for meal in meals if
                                    meal.cook == self.name and meal.total_expenses)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cooking_balance': self.cooking_balance,
            'expenses_balance': self.expenses_balance,
        }


class LoginToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    time = db.Column(db.DateTime, default=datetime.datetime.now() + datetime.timedelta(hours=1), nullable=False)
    secret = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def is_valid_token(self):
        if self.secret and datetime.datetime.now() <= self.time:
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time,
            'secret': self.secret,
        }


class Meals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    cook = db.Column(db.String(50))
    meal_desc = db.Column(db.String(50))
    total_expenses = db.Column(db.Float)
    participants = db.relationship('User', secondary=participants, backref=db.backref('meals', lazy='dynamic'))
    photo_filename = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'cook': self.cook,
            'meal_desc': self.meal_desc,
            'total_expenses': self.total_expenses,
            'participants': [participant.to_dict() for participant in self.participants],
            'photo_filename': self.photo_filename
        }