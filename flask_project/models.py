from flask_project import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Association table for many-to-many relationship between users for friend requests

friend_requests = db.Table('friend_requests',
    db.Column('sender_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipient_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for many-to-many relationship between users for friends
friends = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(6))
    birth_date = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    friend_requests_sent = db.relationship(
        'User', secondary=friend_requests,
        primaryjoin=(friend_requests.c.sender_id == id),
        secondaryjoin=(friend_requests.c.recipient_id == id),
        backref=db.backref('friend_requests_received', lazy='dynamic'), lazy='dynamic')
    
    
    friends = db.relationship(
        'User', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id),
        backref=db.backref('friend_of', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def send_friend_request(self, user):
        if not self.is_friends_with(user) and not self.is_friend_request_sent_to(user):
            self.friend_requests_sent.append(user)

    def cancel_friend_request(self, user):
        if self.is_friend_request_sent_to(user):
            self.friend_requests_sent.remove(user)

    def accept_friend_request(self, user):
        if not self.is_friends_with(user) and self.is_friend_request_received_from(user):
            self.friend_requests_received.remove(user)
            self.friends.append(user)

    def unfriend(self, user):
        if self.is_friends_with(user):
            self.friends.remove(user)

    def is_friends_with(self, user):
        return self.friends.filter(friends.c.friend_id == user.id).count() > 0

    def is_friend_request_sent_to(self, user):
        return self.friend_requests_sent.filter(friend_requests.c.recipient_id == user.id).count() > 0

    def is_friend_request_received_from(self, user):
        return self.friend_requests_received.filter(friend_requests.c.sender_id == user.id).count() > 0

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140))
    privacy = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body) 

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text, nullable=False)
#     privacy = db.Column(db.String(20), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)