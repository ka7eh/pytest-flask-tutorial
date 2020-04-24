import warnings

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import requests
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


def get_post(id, check_author=True):
    # If the requested post is for author, then return both published (1) and unpublished posts (0),
    # otherwise, only return published posts.
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, is_published, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ? AND p.is_published >= ?",
            (id, 0 if check_author else 1),
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/")
def index():
    user_id = session.get("user_id")

    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, is_published, username"
        "  FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.is_published OR p.author_id = ?"
        " ORDER BY created DESC",
        (user_id,)
    ).fetchall()

    # get a random quote and show it on the template
    quotes_response = requests.get("https://quotes.rest/qod").json()
    quotes = [] if quotes_response.get("error") else quotes_response["contents"]["quotes"]

    if not quotes:
        warnings.warn("Could not fetch any quote!")

    return render_template("blog/index.html", posts=posts, quotes=quotes)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        is_published = 1 if "is_published" in request.form else 0
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, is_published, author_id)"
                " VALUES (?, ?, ?, ?)",
                (title, body, is_published, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        is_published = 1 if "is_published" in request.form else 0
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?, is_published = ?" " WHERE id = ?",
                (title, body, is_published, id),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
