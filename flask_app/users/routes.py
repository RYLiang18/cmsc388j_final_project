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
    LoginForm
    # UpdateUsernameForm
)

from ..models import User

users = Blueprint('users', __name__)



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
    return render_template(
        "account.html",
        title="Account"
    )

#Logs out the user
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("photos.index"))

# Searches for a single user
@users.route("/search", methods=["GET", "POST"])
def search():
    search_form = SearchForm()
    if search_form.valudate_on_submit():
        user = User.objects(username=search_form.user.data).first()
        if user is None:
            flash("User does not exist")
            return redirect(url_for('photos.index'))
        return render_template("search_results", result=user)
    return render_template("search", search_form=search_form)


# Shows friends page, including their photos
@users.route("/profile/<user>")
def profile(user):
    friend = User.objects(username=user).first()
    if friend is None:
        return render_template("404")
    return render_template("user_detail", user=friend)
