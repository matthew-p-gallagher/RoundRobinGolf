from flask import Blueprint, render_template
from app.models import db, User

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
def users():
    """List all users."""
    users = User.query.all()
    return render_template("users.html", users=users)
