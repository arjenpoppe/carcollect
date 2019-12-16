import os, functools

from flask import Blueprint, redirect, render_template, request, url_for, current_app, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash

from carcollect.db import get_db

bp = Blueprint('account', __name__, url_prefix='/account')


def login_required(view):
    """Handles authentication for pages that require logging in
    
    Args:
        view (Wrapper): Description
    """
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('account.login'))
        return view(*args, **kwargs)

    return wrapped_view


@bp.route('/login', methods=["POST", "GET"])
def login():
    """Return login view, also handles the actual authentication
    
    Returns:
        template: Default login page
    """
    is_logged_in()

    if request.method == "POST":
        session.permanent = True
        
        user, password = handle_login_form_data()
        error = authenticate(user, password)  
        
        if error is None:
            add_user_to_session(user)
            return redirect(url_for('index'))

        flash(error)
    return render_template('account/login.html')


def add_user_to_session(user):
    """add user to session data, gets called by main login function
    
    Arguments:
        user {sqlite.object} -- user object from database
    """
    session.clear()
    session['user_id'] = user['id']
    session['email'] = user['email']


def handle_login_form_data():
    """Handles login post data, gets called by main login function
    
    Returns:
        sqlite.object, str -- user and password
    """
    email = request.form["email"]
    password = request.form["password"]
    user = get_user_by_email(email)

    return user, password


def authenticate(user, password):
    """Authenticate user
    
    Args:
        user (sqlite.object): user database object
        password (str): password
    
    Returns:
        str: Error message
    """
    error = None
    if user is None or not check_password_hash(user['password'], password):
        error = 'The combination of email and password is incorrect. Please try again.'
        return error
            

@bp.route('/create_account', methods=["POST", "GET"])
def create_account():
    """Return default account creation view and does the actual registration
    
    Returns:
        template: login page if successful
        template: create_account page if error
    """
    if request.method == "POST":
        firstname, lastname, email, password, error = handle_create_account_form_data()

        if error is None:
            add_user_to_db(firstname, lastname, email, password)
            return redirect(url_for('account.login'))

        flash(error)
    return render_template('account/create_account.html')


def add_user_to_db(firstname, lastname, email, password):
    """add user data to database
    
    Arguments:
        firstname {str} -- First Name of user
        lastname {str} -- Last Name of user
        email {str} -- Email adress of user
        password {str} -- Unhashed password of user
    """
    db = get_db()
    db.execute('INSERT INTO user (firstname, lastname, email, password) VALUES (?, ?, ?, ?)',
                (firstname, lastname, email, generate_password_hash(password)))
    db.commit()
    flash('Account created successfully.')



def handle_create_account_form_data():
    """Handles form data for login
    
    Returns:
        str -- error message
    """
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    password = request.form["password"]

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
        error = f'Email {email} already exists in our database.'
    
    return firstname, lastname, email, password, error


@bp.route('/user')
@login_required
def user():
    """Default user page
    
    Returns:
        template: user page template
    """
    user = get_user_by_id(session['user_id'])
    return render_template('account/user.html', user=user)


@bp.route('/logout')
def logout():
    """Clears session data
    
    Returns:
        redirect -- Login page
    """
    if is_logged_in():
        session.clear()
        flash("You are now logged out!")
    else:
        flash("You were not logged in")

    return redirect(url_for('account.login'))


def get_user_by_id(user_id):
    """returns a user from the database
    
    Arguments:
        user_id {integer} -- the user id
    
    Returns:
        sqlite.object -- the requested user
    """
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    return user


def get_user_by_email(email):
    """returns a user from the database
    
    Arguments:
        email {str} -- email adress of user
    
    Returns:
        sqlite.object -- the requested user
    """
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
    return user


@bp.before_app_request
def load_logged_in_user():
    """Executed before every http request. Load the logged in user
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def is_logged_in():
    """Redirects user to user page if already logged in
    
    Returns:
        redirect: user page
    """
    if "user_id" in session:
        flash("You are already logged in!")
        return redirect(url_for('account.user'))

