# import unicodedata
import os
import pathlib
import functools
from datetime import datetime
import random

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import current_user
from flask_wtf import csrf
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename


from . import db, conf
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    # logging in for the first time (after signing up)
    first = session.pop("firstLogin", False)
    email = session.pop("email", "")
    prompt = session.pop("prompt", False)
    return render_template("login.html", email=email, first_time=first, prompt=prompt)


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    email = email.lower().strip()
    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to
    # the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        # if the user doesn't exist or password is wrong, reload the page
        session["email"] = email
        session["prompt"] = True
        return redirect(url_for("auth.login"))

    if not (root := pathlib.Path(user.directory)).exists():
        root.mkdir()
    
    

    # if the above check passes, then we know the user has the right credentials
    session["storeUser"] = True
    session["email"] = email
    session["username"] = user.name
    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))


def restrict_registration(func):
    """Limits registrations to a desired number of accounts"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # currently limited to a single account
        if db.session.query(User).count():
            flash("Registrations are closed")
            return render_template("signup.html", disabled=True)
        return func(*args, **kwargs)

    return wrapper



@auth.route("/signup")
# @restrict_registration  # restricted to a single user atm
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    return render_template("signup.html")






@auth.route("/signup", methods=["POST"])
# @restrict_registration
def signup_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    

    # fields can't be empty
    if not all([email, name, password]):
        flash("Please fill in all the details")
        return redirect(url_for("auth.signup"))
    email = email.lower().strip()
    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()

    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash("Email address already exists")
        return redirect(url_for("auth.signup"))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method="sha256"),
        directory=new_directory(name, email),
        regdate=datetime.utcnow().date(),
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    session["firstLogin"] = True
    session["email"] = email

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


def new_directory(name: str, email: str) -> str:
    """Create and return a sub directory in the root for the specified user."""
    cloud = pathlib.Path(conf["localeCloud"]).expanduser()
    unique = cloud / (safe := secure_filename(email))
    while unique.exists():
        number = random.randint(1e6, 1e7)
        unique = cloud / f"{safe}_{number}"
    unique.mkdir(parents=True, exist_ok=True)
    return str(unique)
