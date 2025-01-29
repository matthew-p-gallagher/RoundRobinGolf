from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    abort,
    get_flashed_messages,
)
from flask_login import login_required, current_user
from app.models import db
from app.services.match_service import MatchService
from app.services.hole_service import HoleService
from app.services.pointstable_service import PointstableService
from app.forms import HoleForm, MatchForm
from . import bp


@bp.route("/")
@login_required
def matches():
    """List all matches for the current user."""
    matches = MatchService.get_all_matches()
    return render_template("matches.html", matches=matches)


@bp.route("/new")
@login_required
def new_match():
    """Create a new match."""
    form = MatchForm()
    return render_template("new_match.html", form=form)


@bp.route("/start", methods=["POST"])
@login_required
def start_match():
    """Start a new match with the provided players."""
    player_names = [
        request.form["player1"],
        request.form["player2"],
        request.form["player3"],
        request.form["player4"],
    ]
    match = MatchService.create_match(player_names)
    flash("New match created successfully!", "success")
    return redirect(url_for("matches.matches"))


@bp.route("/<int:match_id>")
@login_required
def match_overview(match_id):
    """Show match overview."""
    match = MatchService.get_match(match_id)
    # If match is None or belongs to another user, return 404
    if not match or match.user_id != current_user.id:
        abort(404)
    pointstable = PointstableService.get_formatted_pointstable(match_id)
    return render_template("match_overview.html", match=match, pointstable=pointstable)


@bp.route("/delete/<int:match_id>")
@login_required
def delete_match(match_id):
    match = MatchService.get_match(match_id)
    # get_match will return 404 if match doesn't exist or belong to current user
    MatchService.delete_match(match_id)
    return redirect(url_for("matches.matches"))


@bp.route("/finish/<int:match_id>", methods=["GET"])
@login_required
def finish_round(match_id):
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


@bp.route("/<int:match_id>/hole/<int:hole_num>", methods=["GET"])
@login_required
def hole(match_id, hole_num):
    """Show a specific hole for a match."""
    match = MatchService.get_match(match_id)
    if not match:
        abort(404)

    hole = HoleService.get_hole_by_match_hole_num(match_id, hole_num)
    if not hole:
        abort(404)

    form = HoleForm()
    previous_results = HoleService.get_previous_results(hole.id)

    # Filter hole matches by match_id
    hole_matches = [hm for hm in hole.holematches if hm.match_id == match_id]
    hole.holematches = hole_matches

    return render_template(
        "hole.html",
        hole=hole,
        form=form,
        previous_results=previous_results,
        match=match,
    )


@bp.route("/<int:match_id>/hole/<int:hole_num>/process", methods=["POST"])
@login_required
def process_hole(match_id, hole_num):
    hole = HoleService.get_hole_by_match_hole_num(match_id, hole_num)
    winners_ids = []
    for i in range(1, len(hole.holematches) + 1):
        if request.form.get(f"winner{i}"):
            winner = request.form.get(f"winner{i}")
            winners_ids.append(-1 if winner == "draw" else int(winner))
        else:
            winners_ids.append(None)

    HoleService.handle_hole_outcome(match_id, hole.id, winners_ids)
    return jsonify({"status": "success"})
