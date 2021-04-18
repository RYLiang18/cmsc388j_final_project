import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review

def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    ("query", "message"), 
    (
        ("", b"This field is required"),
        ("a", b"Too many results"),
        ("sheeeeeeesh", b"Movie not found"),
        (
            "sheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeesh",
            b"Field must be between 1 and 100 characters long."
        )
    )
)
def test_search_input_validation(client, query, message):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data = form.data, follow_redirects=True)

    assert message in response.data


def test_movie_review(client, auth):
    # %%%%%% TESTING GUARDIANS OF THE GALAXY %%%%%%
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    # %%%%%% REGISTER AND LOGIN %%%%%%
    auth.register(
        username="pytest",
        email="pytest@gmail.com",
        passwrd="pytesting",
        confirm="pytesting"
    )
    auth.login(username="pytest", password="pytesting")

    # %%%%%% RANDOM STRING %%%%%%
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for i in range(42))

    # %%%%%% REVIEWING %%%%%%
    resp = client.get(url)
    assert resp.status_code == 200
    
    review_input = SimpleNamespace(
        text=random_str,
        submit="Enter Comment"
    )
    form = MovieReviewForm(formdata=None, obj=review_input)
    response = client.post(url, data=form.data, follow_redirects=True)
    assert response.status_code == 200
    assert bytes(random_str, 'utf-8') in response.data 

    # %%%%%% CHECKING IF IN DB %%%%%%
    reviews = Review.objects(
        imdb_id = guardians_id,
        content = random_str
    )
    assert len(reviews)>=1

    # assert False

@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("", b"Page Not Found"),
        ("a", b"Incorrect IMDb ID"),
        ("123456789", b"Incorrect IMDb ID"),
        ("goteeeeeeeeeeeeeem", b"Incorrect IMDb ID")
    )
)
def test_movie_review_redirects(client, movie_id, message):
    resp = client.get(f"/movies/{movie_id}", follow_redirects=False)
    
    if len(movie_id)==0:
        assert resp.status_code == 404
    else:
        assert resp.status_code == 302

    resp = client.get(f"/movies/{movie_id}", follow_redirects=True)

    assert message in resp.data


@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("", b"This field is required"),
        ("sheeeeeeeeeeesh"*50, b"Field must be between 5 and 500 characters long"),
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    # %%%%%% TESTING GUARDIANS OF THE GALAXY %%%%%%
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    # %%%%%% REGISTER AND LOGIN %%%%%%
    auth.register(
        username="pytest",
        email="pytest@gmail.com",
        passwrd="pytesting",
        confirm="pytesting"
    )
    auth.login(username="pytest", password="pytesting")

    resp = client.get(url)
    assert resp.status_code == 200

    review_input = SimpleNamespace(
        text=comment,
        submit="Enter Comment"
    )

    form = MovieReviewForm(formdata=None, obj=review_input)
    response = client.post(url, data=form.data, follow_redirects=True)

    assert response.status_code == 200

    assert message in response.data


    # assert False
