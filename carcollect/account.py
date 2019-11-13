import os

from flask import Blueprint, redirect, render_template, request, url_for, current_app, session, flash

bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/login', methods = ["POST", "GET"])
def login():
	if "user" in session:
		flash("You are already logged in!")
		return redirect(url_for('account.user'))

	if request.method == "POST":
		session.permanent = True
		user = request.form["username"]
		password = request.form["password"]
		
		# TODO implement authentication
		session["user"] = user
		return redirect(url_for('account.user'))
	else:
		return render_template('account/login.html')


@bp.route('/create_account', methods = ["POST", "GET"])
def create_account():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]

		# TODO encrypt and save credentials to database

		session["user"] = username
		return redirect(url_for('account.user'))

	return render_template('account/create_account.html')


@bp.route('/user', methods = ["POST", "GET"])
def user():
	email = None
	if "user" in session:
		user = session["user"]
		if request.method == "POST":
			email = request.form["email"]
			session["email"] = email
			flash("Email was saved!")
		else:
			if "email" in session:
				email = session["email"]

		return render_template('account/user.html', user=user, email=email)
	else:
		return redirect(url_for('account.login'))


@bp.route('/logout')
def logout():
	if "user" in session:
		session.pop("user", None)
		session.pop("email", None)
		flash("You are now logged out!")
	else:
		flash("You were not logged in")

	return redirect(url_for('account.login'))