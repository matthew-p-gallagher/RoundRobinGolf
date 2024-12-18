from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    session,
    jsonify,
)
from app.models import db
from services.match_service import MatchService
from services.hole_service import HoleService
from services.pointstable_service import PointstableService
from app.forms import HoleForm

bp = Blueprint("matches", __name__, url_prefix="/matches")


@bp.route("/")
def matches():
    """List all matches."""
    matches = MatchService.get_all_matches()
    return render_template("matches.html", matches=matches)


@bp.route("/new")
def new_match():
    """Create a new match."""
    return render_template("new_match.html")


@bp.route("/start", methods=["POST"])
def start_match():
    """Start a new match with the provided players."""
    player_names = [
        request.form["player1"],
        request.form["player2"],
        request.form["player3"],
        request.form["player4"],
    ]
    match = MatchService.create_match(player_names)
    return redirect(url_for("matches.matches"))


@bp.route("/<int:match_id>")
def match_overview(match_id):
    """Show match overview."""
    match = MatchService.get_match(match_id)
    pointstable = PointstableService.get_formatted_pointstable(match_id)
    return render_template("match_overview.html", match=match, pointstable=pointstable)


@bp.route("/<int:match_id>/delete", methods=["GET"])
def delete_match(match_id):
    """Delete a match."""
    MatchService.delete_match(match_id)
    flash("Match deleted", "success")
    return redirect(url_for("matches.matches"))


@bp.route("/<int:match_id>/<int:hole_num>")
def hole(match_id, hole_num):
    """Show specific hole for a match."""
    session["match_id"] = match_id
    session["hole_num"] = hole_num
    return redirect(url_for("matches.render_hole"))


@bp.route("/hole")
def render_hole():
    """Render the hole view."""
    match_id = session.get("match_id")
    hole_num = session.get("hole_num")

    if match_id is None or hole_num is None:
        flash("Invalid hole access", "error")
        return redirect(url_for("matches.matches"))

    match = MatchService.get_match(match_id)
    hole = HoleService.get_hole_by_match_num(match_id, hole_num)
    previous_results = HoleService.get_previous_results(hole.id)

    messages = get_flashed_messages(with_categories=True)
    hole_incomplete_message = next(
        (
            message
            for category, message in messages
            if "Hole" in message and "not complete" in message
        ),
        None,
    )

    form = HoleForm()
    return render_template(
        "hole.html",
        match=match,
        hole=hole,
        hole_incomplete_message=hole_incomplete_message,
        previous_results=previous_results,
        form=form,
    )


@bp.route("/<int:match_id>/<int:hole_num>/process", methods=["POST"])
def process_hole(match_id, hole_num):
    """Process the hole results."""
    hole = HoleService.get_hole_by_match_num(match_id, hole_num)

    winners_ids = []
    for i in range(1, len(hole.holematches) + 1):
        if request.form.get(f"winner{i}"):
            winner = request.form.get(f"winner{i}")
            winners_ids.append(-1 if winner == "draw" else int(winner))
        else:
            winners_ids.append(None)

    HoleService.handle_hole_outcome(match_id, hole.id, winners_ids)
    return jsonify({"success": True})


@bp.route("/<int:match_id>/finish", methods=["GET"])
def finish_round(match_id):
    """Finish a round."""
    match = MatchService.get_match(match_id)

    # Check if all holes have been played and all holematches have a result
    incomplete_hole = HoleService.get_first_incomplete_hole(match_id)
    if incomplete_hole:
        flash(
            f"Cannot finish round. Hole {incomplete_hole.num} is not complete.", "error"
        )
        return redirect(
            url_for("matches.hole", match_id=match_id, hole_num=incomplete_hole.num)
        )

    final_results = PointstableService.get_formatted_pointstable(match_id)
    match.completed = True
    db.session.commit()

    return render_template(
        "round_summary.html", match=match, final_results=final_results
    )
