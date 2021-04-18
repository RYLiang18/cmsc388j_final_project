from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm
from flask_app.models import User

from flask_app.forms import UpdateUsernameForm


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"
        assert "_user_id" in session


@pytest.mark.parametrize(
    ("username", "password", "message"), (
        ("", "asdf", b"This field is required"),
        ("asdf", "", b"This field is required"),
        ("", "", b"This field is required"),
        ("pepehands", "pepega", b"Login failed. Check your username and/or password"),
        ("test", "pepega", b"Login failed. Check your username and/or password"),
        ("pepega", "test", b"Login failed. Check your username and/or password")
    )
)
def test_login_input_validation(auth, username, password, message):
    auth.register()
    response = auth.login(username=username, password=password)
    assert message in response.data


def test_logout(client, auth):
    auth.register()
    resp = auth.login()
    assert b"test" in resp.data

    auth.logout()

    with client:
        client.get("/")
        assert "_user_id" not in session
    


def test_change_username(client, auth):
    auth.register()
    auth.login()

    resp = client.get("/account")
    assert resp.status_code == 200


    new_username = SimpleNamespace(
        username = "peepeehands",
        submit= "Update Username"
    )
    form = UpdateUsernameForm(formdata = None, obj=new_username)
    response = client.post("/account", data=form.data, follow_redirects=True)

    auth.login(username="peepeehands")

    response = client.get("/account")

    assert b"peepeehands" in response.data

    users = User.objects(
        username = "peepeehands"
    )
    assert len(users) == 1


def test_change_username_taken(client, auth):
    auth.register(username="deeznuts", email="asdf@gmail.com", passwrd="goteem", confirm="goteem")
    
    auth.register()
    auth.login()


    resp = client.get("/account")
    assert resp.status_code == 200

    new_username = SimpleNamespace(
        username = "deeznuts",
        submit= "Update Username"
    )
    form = UpdateUsernameForm(formdata = None, obj=new_username)
    response = client.post("/account", data=form.data, follow_redirects=True)

    assert b"That username is already taken" in response.data


@pytest.mark.parametrize(
    ("new_username"), 
    (
        (""),
        ("sheeeesh"*10)
    )
)
def test_change_username_input_validation(client, auth, new_username):
    auth.register()
    auth.login()
    
    resp = client.get("/account")
    assert resp.status_code == 200

    new_username_namespace = SimpleNamespace(
        username = new_username,
        submit= "Update Username"
    )
    form = UpdateUsernameForm(formdata = None, obj=new_username_namespace)
    response = client.post("/account", data=form.data, follow_redirects=True)

    if len(new_username) == 0:
        assert b"This field is required" in response.data
    else:
        assert b"Field must be between 1 and 40 characters long" in response.data
