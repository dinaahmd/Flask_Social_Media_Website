from flask_project import db, app
# from flask_project.models import User, Post
import sys

# Create Database
def create_db():
    with app.app_context():
        db.create_all()

# Drop All data in tables
def drop_db():
    with app.app_context():
        db.drop_all()



# Snippet allows us to run func from within terminal with :
# python db_test.py create_db
if __name__ == '__main__':
    globals()[sys.argv[1]]()