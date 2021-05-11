from flask import (
    Blueprint,
    redirect,
    url_for,
    render_template,
    flash,
    request
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from .. import bcrypt
from ..forms import (
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm
)

from ..models import User, Photo
from ..client import send_mail

users = Blueprint('users', __name__)

import re

# registers the user
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("photos.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()
        send_mail(form.email.data, "Hi {}, welcome to Memories!".format(form.username.data),
        "Welcome to memories!")

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)

# logs in the user
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("photos.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


# Shows user info like username, number of posts, etc, number of friends
@users.route("/account")
@login_required
def account():
    username_form = UpdateUsernameForm()

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
    )


#Logs out the user
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("photos.index"))

# Searches for a single user
@users.route("/search/<query>", methods=["GET", "POST"])
def search(query):
    regex = re.compile(query, re.IGNORECASE)
    users = User.objects(username=regex)

    if users is None:
        flash("User(s) does not exist")
        return redirect(url_for('photos.index'))
    
    return render_template("search_results.html", results=users)
    
    # search_form = SearchForm()
    # if search_form.validate_on_submit():
    #     user = User.objects(username=search_form.user.data).first()
    #     if user is None:
            
    #     return render_template("search_results", result=user)
    # return render_template("search", search_form=search_form)


# Shows friends page, including their photos
@users.route("/profile/<user>")
def profile(user):
    friend = User.objects(username=user).first()
    if friend is None:
        return render_template("404")
    friend_photos = Photo.objects(poster = friend)
    return render_template("user_detail.html", user=friend, photos=friend_photos)

@users.route("/follow/<user>")
@login_required
def follow(user):
    friend = User.objects(username=user).first()
    if friend is None:
        flash("Unable to follow! D:")
    current_user.update(add_to_set__following=friend)
    return redirect(url_for('users.profile', user=user))

@users.route("/unfollow/<user>")
@login_required
def unfollow(user):
    enemy = User.objects(username=user).first()
    if enemy is None:
        flash("Unable to unfollow! D:")
    current_user.update(pull__following=enemy)
    return redirect(url_for('users.profile', user=user))
