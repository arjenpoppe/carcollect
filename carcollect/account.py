import os, functools

from flask import Blueprint, redirect, render_template, request, url_for, current_app, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash

from carcollect.db import get_db

bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/login', methods=["POST", "GET"])
def login():
    if is_logged_in():
        flash("You are already logged in!")
        return redirect(url_for('account.user'))

    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'The combination of email and password is incorrect. Please try again.'
            

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('index'))

        flash(error)
    return render_template('account/login.html')


@bp.route('/create_account', methods=["POST", "GET"])
def create_account():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        error = None

        if not firstname:
            error = 'First Name is required.'
        elif not lastname:
            error = 'Last Name is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
            
        elif get_user_by_email(email) is not None:
            error = f'Email {email} already exists in our database. It is not possible to recover your account. Good ' \
                    f'luck remembering the password.'

        if error is None:
            db.execute('INSERT INTO user (firstname, lastname, email, password) VALUES (?, ?, ?, ?)',
                       (firstname, lastname, email, generate_password_hash(password)))
            db.commit()

            flash('Account created successfully.')
            return redirect(url_for('account.login'))

        flash(error)

    return render_template('account/create_account.html')


@bp.route('/user', methods=["POST", "GET"])
def user():
    if is_logged_in():
        user = get_user_by_id(session['user_id'])

        return render_template('account/user.html', user=user)
    else:
        return redirect(url_for('account.login'))


@bp.route('/logout')
def logout():
    if is_logged_in():
        session.clear()
        flash("You are now logged out!")
    else:
        flash("You were not logged in")

    return redirect(url_for('account.login'))


def get_user_by_id(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    return user


def get_user_by_email(email):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
    return user


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('account.login'))
        return view(*args, **kwargs)

    return wrapped_view


def is_logged_in():
    return "user_id" in session


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)
