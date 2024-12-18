from flask import Blueprint, render_template
from app.models import db

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    """Home page route."""
    return render_template("home.html")
