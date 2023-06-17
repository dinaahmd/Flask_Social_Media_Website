from flask_project import db, app
from flask_project.models import User, Post
import sys

# Create Database
def create_db():
    with app.app_context():
        db.create_all()

# Drop All data in tables
def drop_db():
    with app.app_context():
        db.drop_all()

def create_users():
    with app.app_context():
        new_user = User(username='Yahia2', email='Yahia2@gmail.com', password='123')
        db.session.add(new_user)
        db.session.commit()
        
def create_posts():
    with app.app_context():
        user = User.query.first()
        post_1 = Post(content='test content 1', user_id=user.id)
        post_2 = Post(content='test content 2', user_id=user.id)
        db.session.add(post_1)
        db.session.add(post_2)
        db.session.commit()
# Snippet allows us to run func from within terminal with :
# python run_db.py create_db
if __name__ == '__main__':
    globals()[sys.argv[1]]()