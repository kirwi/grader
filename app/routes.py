from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Course, Assignment

@app.route('/')
def to_login():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.find(login_form.email.data)
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid email address or password')
            return redirect(url_for('login'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=login_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/user/<email>')
@login_required
def user(email):
    user = User.find(email)
    return render_template('profile.html', user=user)

@app.route('/course/<int:section>')
@login_required
def course(section):
    course = Course.find(section)
    if current_user.role == 'student':
        return render_template('course_student.html', course=course)
    else:
        return render_template('course_instructor.html', course=course)

@app.route('/course/<int:section>/<feature>', methods=['GET', 'POST'])
@login_required
def course_feature(section, feature):
    course = Course.find(section)
    template_url = '{feature}.html'.format(feature=feature)
    return render_template(template_url, course=course)

@app.route('/updateassignment/<title>/<email>/<int:score>', methods=['GET', 'POST'])
def update_assignment(title, email, score):
    assignment = Assignment.find(title.strip())
    assignment.add_to_db(email, score)
    return 'Assignment updated', 204
