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
from ..forms import SearchForm, PhotoForm, PhotoCommentForm
from ..models import User, Comment, Photo
from ..utils import current_time
from ..client import get_holiday
from werkzeug.utils import secure_filename
import os

photos = Blueprint("photos", __name__)

from flask import send_file
import io
import base64

# @photos.context_processor
# def utility_processor():
#     def get_image(photo_object):
#         bytes_im = io.BytesIO(photo_object.image.read())
#         image = base64.b64encode(bytes_im.getvalue()).decode()
#         return image
#     return dict(get_image=get_image)

def prepopulate():
    #### Prepopulating Users
    fiend = User(
    username = "FrogFiend",
    email = "ltnwkjsdljkfjal@gmail.com",
    password = "whereTheFr0gsAt"
    )
    fiend.save()

    bean = User(
        username = "BeanFreak",
        email = "soijdljksdcnvjlsjk@hotmail.com",
        password = "eatinBeansOnATuesday"
    )
    bean.save()

    bread = User(
        username = "BreadHead",
        email = "eerkljngkljerng@aol.com",
        password = "theyCallmeToastTheWayIBurnAllThisBread"
    )
    bread.save()

    #### Prepopulating Photos

    with open("flask_app/photos/images/phrog1.jpg", 'rb') as f:
        frog1 = Photo (
            poster=fiend,
            date = current_time(),
            image=f,
            caption = "My man looking fresh",
        )
        frog1.save()

    with open("flask_app/photos/images/phrog2.jpg", 'rb') as f:
        frog2 = Photo (
            poster=fiend,
            date = current_time(),
            image=f,
            caption = "sheeeeeeesh",
        )
        frog2.save()

    with open("flask_app/photos/images/phrog3.jpg", 'rb') as f:
        frog3 = Photo (
            poster=fiend,
            date = current_time(),
            image=f,
            caption = "Throwback",
        )
        frog3.save()

    with open("flask_app/photos/images/beans1.jpg", 'rb') as f:
        beans1 = Photo (
            poster=bean,
            date = current_time(),
            image=f,
            caption = "Staying hyrdated",
        )
        beans1.save()

    with open("flask_app/photos/images/beans2.jpg", 'rb') as f:
        beans2 = Photo (
            poster=bean,
            date = current_time(),
            image=f,
            caption = "New kicks",
        )
        beans2.save()

    with open("flask_app/photos/images/bread1.jpg", 'rb') as f:
        bread1 = Photo (
            poster=bread,
            date = current_time(),
            image=f,
            caption = "Looking good",
        )
        bread1.save()




# Default view of the page, should present all photos posted
@photos.route("/", methods=["GET", "POST"])
def index():
    if len(User.objects) == 0:
        # prepopulate()
        pass

    holiday = get_holiday()
    if holiday is not None:
        flash("Happy {}!".format(holiday))
    form = SearchForm()

    all_photos = Photo.objects()

    if form.validate_on_submit():
        return redirect(url_for("users.search", query=form.user.data))
    return render_template(
        "index.html",
        form=form,
        photos = all_photos
    )

# Private photo view, only shows photos from who a user follows
@photos.route("/feed", methods=["GET"])
@login_required
def private_feed():
    friends = current_user.following
    if friends is None:
        flash("No friends!")
        return redirect(url_for('photos.index'))
    photos_feed = Photo.objects(poster__in=friends)
    if photos_feed is None:
        flash("No friends have posted photos")
        return redirect(url_for('photos.index'))
    return render_template("feed.html", photos=photos_feed)


# Detail of a photo when clicked
@photos.route("/photos/<photo_id>", methods=["GET", "POST"])
def photo_detail(photo_id):
    info = photo_id.split("-")
    photo = Photo.objects(
        poster__in = User.objects(username=info[0]), 
        date=info[1]
    ).first()
    if photo is None:
        return render_template("404.html")

    form = PhotoCommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        post_user = User.objects(username=current_user.get_id()).first()
        comment = Comment(
            commenter=post_user,
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

        post_user = User.objects(username=current_user.get_id()).first()


        photo = Photo(
            poster=post_user,
            caption=form.caption.data,
            date=current_time(),
        )
        photo.image.put(new_pic.stream, content_type=content_type)
        photo.save()
        flash("Photo successfully posted!")
        return redirect(url_for('photos.index'))
    return render_template("post_photo.html", form=form)
