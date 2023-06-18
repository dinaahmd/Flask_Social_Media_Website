from flask import render_template, redirect, url_for, flash, request
from flask_project import app, db, bcrypt
from flask_project.forms import RegistrationForm, LoginForm, PostForm, ProfileUpdateForm
from flask_project.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
import os
from datetime import datetime



navbar_items = [
    {'title': 'Home', 'route': 'home'},
    {'title': 'Register', 'route': 'register'},
    {'title': 'Login', 'route': 'login'},
    {'title': 'Logout', 'route': 'logout'},
    {'title': 'Users', 'route': 'users'},
    {'title': 'Friend Requests', 'route': 'friendRequest'}


]


@app.route('/friendRequest', methods=['GET', 'POST'])
def friendRequest():
    requests = current_user.friend_requests_received.all()
    return render_template('friend_request.html', data = {'requests':requests, 'navbar': navbar_items})





def save_image(picture_file):
    picture_name = picture_file.filename
    picture_path = os.path.join(app.root_path,'static/profile_pictures', picture_name)
    picture_file.save(picture_path)
    return picture_name






# Profile Endpoints
# @app.route('/profile/<user_id>')
# @login_required
# def profile(user_id): 
#     user_obj = User.query.get(user_id)
#     return render_template('profile.html', data={'user':user_obj, 'navbar': navbar_items})

    # form = ProfileUpdateForm()
    # if form.validate_on_submit():
    #     image_file = save_image(form.picture.data)
    #     current_user.image_file = image_file
    #     db.session.commit()
    #     return redirect(url_for('profile'))
    # image_url = url_for('static', filename = 'profile_pictures/'+current_user.image_file)

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
    return render_template('home.html', form=form, posts=posts, data = {'navbar': navbar_items})


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
                password=hashed_pw,
                gender= 'female',
                birth_date= datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0)
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
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
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


@app.route('/users')
@login_required
def users():
    with app.app_context():
        user_ids = [current_user.id]
        for friend in current_user.friends:
            user_ids.append(friend.id)
        for friend in current_user.friend_requests_sent:
            user_ids.append(friend.id)        
        users = User.query.filter(User.id.notin_(user_ids)).all()
    return render_template('users.html', data={'users':users,'navbar': navbar_items})


@app.route('/add_friend/<user_id>')
@login_required
def add_friend(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if user is None:
            flash('User not found.', 'error')
            return redirect(url_for('users'))
        current_user.friend_requests_sent.append(user)
        db.session.commit()
        flash('Friend added successfully!', 'success')
    return redirect(url_for('users'))


@app.route('/profile/<user_id>')
@login_required
def profile(user_id):
    with app.app_context():
        user_obj = User.query.get(user_id)
        friends = user_obj.friends.all()
        posts = user_obj.posts.all()
    return render_template('profile.html', data={'user':user_obj, 'friends': friends, 'posts': posts, 'navbar': navbar_items})

