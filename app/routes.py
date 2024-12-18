from flask import (
    current_app as app,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    session,
    jsonify,
)
from .models import db, User
from services.match_service import MatchService
from services.player_service import PlayerService
from services.hole_service import HoleService
from services.pointstable_service import PointstableService
from app.forms import HoleForm


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/users")
def users():
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/new_match")
def new_match():
    return render_template("new_match.html")


@app.route("/start_match", methods=["POST"])
def start_match():
    player_names = [
        request.form["player1"],
        request.form["player2"],
        request.form["player3"],
        request.form["player4"],
    ]

    match = MatchService.create_match(player_names)

    return redirect(url_for("matches"))


@app.route("/matches")
def matches():
    matches = MatchService.get_all_matches()
    return render_template("matches.html", matches=matches)


@app.route("/match/<int:match_id>/<int:hole_num>", methods=["GET"])
def hole(match_id, hole_num):
    session["match_id"] = match_id
    session["hole_num"] = hole_num
    return redirect(url_for("render_hole"))


@app.route("/hole", methods=["GET"])
def render_hole():
    match_id = session.get("match_id")
    hole_num = session.get("hole_num")

    if match_id is None or hole_num is None:
        flash("Invalid hole access", "error")
        return redirect(url_for("matches"))

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


@app.route("/match/<int:match_id>")
def match_overview(match_id):
    match = MatchService.get_match(match_id)
    pointstable = PointstableService.get_formatted_pointstable(match_id)
    return render_template("match_overview.html", match=match, pointstable=pointstable)


@app.route("/delete_match/<int:match_id>", methods=["GET"])
def delete_match(match_id):
    MatchService.delete_match(match_id)
    flash("Match deleted", "success")
    return redirect(url_for("matches"))


@app.route("/process_hole/<int:match_id>/<int:hole_num>", methods=["POST"])
def process_hole(match_id, hole_num):

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


@app.route("/finish_round/<int:match_id>", methods=["GET"])
def finish_round(match_id):
    match = MatchService.get_match(match_id)

    # Check if all holes have been played and all holematches have a result
    incomplete_hole = HoleService.get_first_incomplete_hole(match_id)
    if incomplete_hole:
        flash(
            f"Cannot finish round. Hole {incomplete_hole.num} is not complete.", "error"
        )
        return redirect(
            url_for("hole", match_id=match_id, hole_num=incomplete_hole.num)
        )

    final_results = PointstableService.get_formatted_pointstable(match_id)

    match.completed = True
    db.session.commit()

    return render_template(
        "round_summary.html", match=match, final_results=final_results
    )
