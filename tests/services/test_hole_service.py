import pytest
from app.services.hole_service import HoleService
from app.models import Hole, HoleMatch, Player
from app.services.match_service import MatchService


def test_create_hole(logged_in_user, service_created_match):
    """Test creating a hole with its hole matches"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    player_ids = [p.id for p in players]

    # Test hole 1 (should create matches between players 0,1 and 2,3)
    hole = HoleService.create_hole(1, service_created_match.id, player_ids)

    assert hole.num == 1
    assert hole.match_id == service_created_match.id

    holematches = hole.holematches
    assert len(holematches) == 2

    # First match should be between players 0 and 1
    assert holematches[0].player1_id == player_ids[0]
    assert holematches[0].player2_id == player_ids[1]

    # Second match should be between players 2 and 3
    assert holematches[1].player1_id == player_ids[2]
    assert holematches[1].player2_id == player_ids[3]


def test_create_hole_rotation(logged_in_user, service_created_match):
    """Test that player matchups rotate correctly across holes"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    player_ids = [p.id for p in players]

    # Create first three holes and verify rotation
    hole1 = HoleService.create_hole(1, service_created_match.id, player_ids)  # 0-1, 2-3
    hole2 = HoleService.create_hole(2, service_created_match.id, player_ids)  # 0-2, 1-3
    hole3 = HoleService.create_hole(3, service_created_match.id, player_ids)  # 0-3, 1-2

    # Verify hole 1 matches
    matches1 = hole1.holematches
    assert matches1[0].player1_id == player_ids[0]
    assert matches1[0].player2_id == player_ids[1]
    assert matches1[1].player1_id == player_ids[2]
    assert matches1[1].player2_id == player_ids[3]

    # Verify hole 2 matches
    matches2 = hole2.holematches
    assert matches2[0].player1_id == player_ids[0]
    assert matches2[0].player2_id == player_ids[2]
    assert matches2[1].player1_id == player_ids[1]
    assert matches2[1].player2_id == player_ids[3]

    # Verify hole 3 matches
    matches3 = hole3.holematches
    assert matches3[0].player1_id == player_ids[0]
    assert matches3[0].player2_id == player_ids[3]
    assert matches3[1].player1_id == player_ids[1]
    assert matches3[1].player2_id == player_ids[2]


@pytest.fixture
def service_created_hole(service_created_match):
    """Create a hole using the service method"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    player_ids = [p.id for p in players]
    return HoleService.create_hole(1, service_created_match.id, player_ids)


def test_get_hole(service_created_hole):
    """Test retrieving a specific hole"""
    hole = HoleService.get_hole(service_created_hole.id)
    assert hole.id == service_created_hole.id
    assert hole.num == service_created_hole.num


def test_get_hole_by_match_hole_num(service_created_match, service_created_hole):
    """Test retrieving a hole by match ID and hole number"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    assert hole.id == service_created_hole.id
    assert hole.num == 1


def test_handle_hole_outcome(service_created_hole):
    """Test handling the outcome of a hole"""
    hole = service_created_hole
    holematch1, holematch2 = hole.holematches

    # Set winners for both matches
    winners = [holematch1.player1_id, holematch2.player2_id]
    HoleService.handle_hole_outcome(hole.match_id, hole.id, winners)

    # Verify winners were set
    assert holematch1.winner_id == winners[0]
    assert holematch2.winner_id == winners[1]

    # Verify scorecards were updated
    assert holematch1.player1.scorecard[0] == "W"  # Winner
    assert holematch1.player2.scorecard[0] == "L"  # Loser
    assert holematch2.player1.scorecard[0] == "L"  # Loser
    assert holematch2.player2.scorecard[0] == "W"  # Winner


def test_handle_hole_outcome_draw(service_created_hole):
    """Test handling a draw outcome"""
    hole = service_created_hole
    holematch = hole.holematches[0]

    # Set a draw (-1 indicates draw)
    HoleService.handle_hole_outcome(hole.match_id, hole.id, [-1, None])

    # Verify draw was recorded
    assert holematch.player1.scorecard[0] == "D"
    assert holematch.player2.scorecard[0] == "D"


def test_get_next_hole_num(service_created_hole):
    """Test getting the next hole number"""
    next_num = HoleService.get_next_hole_num(service_created_hole.id)
    assert next_num == service_created_hole.num + 1


def test_get_previous_results(service_created_hole):
    """Test getting previous results"""
    hole = service_created_hole
    holematch1, holematch2 = hole.holematches

    # Set some results
    winners = [holematch1.player1_id, holematch2.player2_id]
    HoleService.handle_hole_outcome(hole.match_id, hole.id, winners)

    results = HoleService.get_previous_results(hole.id)
    assert results["winner1"] == winners[0]
    assert results["winner2"] == winners[1]


def test_get_first_incomplete_hole(service_created_match):
    """Test finding the first incomplete hole"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    player_ids = [p.id for p in players]

    # Create two holes
    hole1 = HoleService.create_hole(1, service_created_match.id, player_ids)
    hole2 = HoleService.create_hole(2, service_created_match.id, player_ids)

    # Initially, hole1 should be first incomplete
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete.id == hole1.id

    # Complete hole1
    HoleService.handle_hole_outcome(
        service_created_match.id,
        hole1.id,
        [hole1.holematches[0].player1_id, hole1.holematches[1].player1_id],
    )

    # Now hole2 should be first incomplete
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete.id == hole2.id

    # Complete hole2
    HoleService.handle_hole_outcome(
        service_created_match.id,
        hole2.id,
        [hole2.holematches[0].player1_id, hole2.holematches[1].player1_id],
    )

    # Now no incomplete holes
    incomplete = HoleService.get_first_incomplete_hole(service_created_match.id)
    assert incomplete is None
