from flask import Blueprint, render_template, session
from flask_login import login_required, current_user

# from . import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/profile")
@login_required
def profile():
    # this is where the user lands after a login, hence the extra parameters
    return render_template(
        "profile.html",
        name=current_user.name.title(),
        regdate=current_user.regdate,
        email=session.get("email"),
        username=session.get("username"),
        storeUser=session.get("storeUser"),
    )
