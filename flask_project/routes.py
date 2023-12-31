from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_project import app, db, bcrypt
from flask_project.forms import RegistrationForm, LoginForm, PostForm, ProfileUpdateForm
from flask_project.models import User, Post
from sqlalchemy import or_
from flask_login import current_user, login_user, logout_user, login_required
import os
# users = Blueprint(
#     'users',
#     __name__,
#     url_prefix='/'
# )

navbar_items = [
    {'title': 'Home', 'route': 'home'},
    {'title': 'Post', 'route': 'post'},
    {'title': 'Profile', 'route': 'profile'},
    {'title': 'Register', 'route': 'register'},
    {'title': 'Login', 'route': 'login'},
    {'title': 'Logout', 'route': 'logout'}
]
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, privacy=form.privacy.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    posts = Post.query.filter((Post.privacy == 'Public') | (Post.user_id == current_user.id)).all()
    return render_template('home.html', posts=posts, data = {'form':form, 'navbar': navbar_items})

def save_image(picture_file):
    picture_name = picture_file.filename
    picture_path = os.path.join(app.root_path,'static/profile_pictures', picture_name)
    picture_file.save(picture_path)
    return picture_name
    
# Profile Endpoints
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        image_file = save_image(form.picture.data)
        current_user.image_file = image_file
        db.session.commit()
        return redirect(url_for('profile'))
    image_url = url_for('static', filename = 'profile_pictures/'+current_user.image_file)
    return render_template('profile.html', data={'form':form, 'navbar': navbar_items}, legend='Profile Details', image_url=image_url)

# Post Endpoint
@app.route('/post', methods=['GET', 'POST'])
def post():
    form = PostForm()
    if form.validate_on_submit():
        with app.app_context():
            content = form.content.data
            privacy = form.privacy.data
            post = Post(content=content, privacy=privacy, user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('profile'))
    posts = Post.query.filter(or_(Post.privacy == 'Public', Post.user_id == current_user.id)).all()
    return render_template('post.html', posts=posts ,data={'form':form, 'navbar': navbar_items})

# Register Endpoint
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()
            
        flash(f"Registration Successful for {form.username.data}!","success")
        return redirect(url_for('login'))
    return render_template('register.html', data={'form':form, 'navbar': navbar_items})

# Login Endpoint
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    # emails = ['dina@gmail.com', 'khalil@gmail.com']
    # passwords = ['123', '456']
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
        # if form.email.data in emails and form.password.data in passwords:
                login_user(user)
                flash("Login Successful!","success")
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('home'))
            else:
                flash("Login Unsuccessful!","danger")
                return redirect(url_for('login'))

    return render_template('login.html', data={'form':form,'navbar': navbar_items})

# Logout Endpoint
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

