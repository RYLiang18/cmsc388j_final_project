from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    request,
    flash
)
from flask_login import (
    current_user,
    login_required
)

# from .. import movie_client
from ..forms import SearchForm, PhotoForm
from ..models import User, Comment, Photo
from ..utils import current_time
from werkzeug.utils import secure_filename

photos = Blueprint("photos", __name__)


# Default view of the page, should present all public photos posted
@photos.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("photos.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)

# Private photo view, only shows photos from who a user follows
@photos.route("/feed", methods=["GET"])
@login_required
def private_feed():
    friends = current_user.following
    print("0000000000000000000000000000000000")
    print(type(friends))
    if friends is None:
        flash("No friends!")
        return redirect(url_for('photos.index'))
    photos_feed = Photos.objects(poster__in=friends)
    if photos_feed is None:
        flash("No friends have posted photos")
        return redirect(url_for('photos.index'))
    return render_template("feed", photos=photos_feed)


# Detail of a photo when clicked
@photos.route("/photos/<photo_id>", methods=["GET", "POST"])
def movie_detail(photo_id):
    info = photo_id.split("-")
    photo = Photo.objects(poster=photo_id[0], date=photo_id[1]).first()
    if photo is None:
        return render_template("404")

    form = PhotoCommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            commenter=current_user._get_current_object(),
            caption=form.text.data,
            date=current_time(),
            photo=photo
        )
        comment.save()

        return redirect(request.path)

    comments = Comment.objects(photo=photo)

    return render_template(
        "photo_detail.html", form=form, photo=photo, comments=comments
    )

@photos.route("/photos/new", methods=["GET","POST"])
@login_required
def new_photo():
    form = PhotoForm()
    if form.validate_on_submit():
        new_pic = form.photo.data
        filename = secure_filename(new_pic.filename)
        content_type =f'images/{filename[-3:]}'
        photo = Photo(
            poster=current_user,
            caption=form.caption.data,
            date=current_time(),
        )
        photo.image.put(new_pic.stream, content_type=content_type)
        photo.save()
        flash("Photo successfully posted!")
        return redirect(url_for('photos.index'))
    return render_template("post_photo", form=form)
