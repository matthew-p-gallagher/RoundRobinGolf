import pytest
from app.services.hole_service import HoleService
from app.models import Hole, HoleMatch, Player


def test_hole_creation_from_match(service_created_match):
    """Test that holes are created correctly when a match is created"""
    holes = (
        Hole.query.filter_by(match_id=service_created_match.id).order_by(Hole.num).all()
    )

    # Verify basic hole creation
    assert len(holes) == 18
    assert [h.num for h in holes] == list(range(1, 19))

    # Verify hole matches for first three holes follow the rotation pattern
    hole1, hole2, hole3 = holes[:3]
    players = (
        Player.query.filter_by(match_id=service_created_match.id)
        .order_by(Player.id)
        .all()
    )
    player_ids = [p.id for p in players]

    # Hole 1: (0,1) (2,3)
    matches1 = hole1.holematches
    assert matches1[0].player1_id == player_ids[0]
    assert matches1[0].player2_id == player_ids[1]
    assert matches1[1].player1_id == player_ids[2]
    assert matches1[1].player2_id == player_ids[3]

    # Hole 2: (0,2) (1,3)
    matches2 = hole2.holematches
    assert matches2[0].player1_id == player_ids[0]
    assert matches2[0].player2_id == player_ids[2]
    assert matches2[1].player1_id == player_ids[1]
    assert matches2[1].player2_id == player_ids[3]

    # Hole 3: (0,3) (1,2)
    matches3 = hole3.holematches
    assert matches3[0].player1_id == player_ids[0]
    assert matches3[0].player2_id == player_ids[3]
    assert matches3[1].player1_id == player_ids[1]
    assert matches3[1].player2_id == player_ids[2]


def test_get_hole(service_created_match):
    """Test retrieving a specific hole"""
    holes = Hole.query.filter_by(match_id=service_created_match.id).all()
    first_hole = holes[0]

    retrieved_hole = HoleService.get_hole(first_hole.id)
    assert retrieved_hole.id == first_hole.id
    assert retrieved_hole.num == 1


def test_get_hole_by_match_hole_num(service_created_match):
    """Test retrieving a hole by match ID and hole number"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    assert hole.num == 1
    assert hole.match_id == service_created_match.id


def test_handle_hole_outcome(service_created_match):
    """Test handling the outcome of a hole"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch1, holematch2 = hole.holematches

    # Set winners for both matches
    winners = [holematch1.player1_id, holematch2.player2_id]
    HoleService.handle_hole_outcome(service_created_match.id, hole.id, winners)

    # Verify winners were set
    assert holematch1.winner_id == winners[0]
    assert holematch2.winner_id == winners[1]

    # Verify scorecards were updated
    assert holematch1.player1.scorecard[0] == "W"  # Winner
    assert holematch1.player2.scorecard[0] == "L"  # Loser
    assert holematch2.player1.scorecard[0] == "L"  # Loser
    assert holematch2.player2.scorecard[0] == "W"  # Winner


def test_handle_hole_outcome_draw(service_created_match):
    """Test handling a draw outcome"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch = hole.holematches[0]

    # Set a draw (-1 indicates draw)
    HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, None])

    # Verify draw was recorded
    assert holematch.player1.scorecard[0] == "D"
    assert holematch.player2.scorecard[0] == "D"


def test_get_next_hole_num(service_created_match):
    """Test getting the next hole number"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    next_num = HoleService.get_next_hole_num(hole.id)
    assert next_num == 2


def test_get_previous_results(service_created_match):
    """Test getting previous results"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch1, holematch2 = hole.holematches

    # Set some results
    winners = [holematch1.player1_id, holematch2.player2_id]
    HoleService.handle_hole_outcome(service_created_match.id, hole.id, winners)

    results = HoleService.get_previous_results(hole.id)
    assert results["winner1"] == winners[0]
    assert results["winner2"] == winners[1]


def test_get_first_incomplete_hole(service_created_match):
    """Test finding the first incomplete hole"""
    # Initially, hole 1 should be first incomplete
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete.num == 1

    # Complete hole 1
    hole1 = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch1, holematch2 = hole1.holematches
    HoleService.handle_hole_outcome(
        service_created_match.id,
        hole1.id,
        [holematch1.player1_id, holematch2.player1_id],
    )

    # Now hole 2 should be first incomplete
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete.num == 2

    # Complete all holes
    for i in range(2, 19):
        hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, i)
        holematch1, holematch2 = hole.holematches
        HoleService.handle_hole_outcome(
            service_created_match.id,
            hole.id,
            [holematch1.player1_id, holematch2.player1_id],
        )

    # Now no incomplete holes
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete is None
