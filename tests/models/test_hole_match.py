"""Tests for HoleMatch model."""

import pytest
from app.models import HoleMatch, Player, Hole


def test_hole_match(_db, test_match):
    """Test hole match creation and relationships"""
    # Create two players
    player1 = Player(name="Player 1", match_id=test_match.id)
    player2 = Player(name="Player 2", match_id=test_match.id)
    _db.session.add_all([player1, player2])

    # Create a hole
    hole = Hole(num=1, match_id=test_match.id)
    _db.session.add(hole)
    _db.session.commit()

    # Create hole match
    hole_match = HoleMatch(
        hole_id=hole.id,
        match_id=test_match.id,
        player1_id=player1.id,
        player2_id=player2.id,
    )
    _db.session.add(hole_match)
    _db.session.commit()

    assert hole_match.hole_id == hole.id
    assert hole_match.match_id == test_match.id
    assert hole_match.player1_id == player1.id
    assert hole_match.player2_id == player2.id
    assert hole_match.winner_id is None
    assert (
        str(hole_match) == f"<HoleMatch {hole_match.id} for Hole {hole_match.hole_id}>"
    )

    # Test winner assignment
    hole_match.winner_id = player1.id
    _db.session.commit()
    assert hole_match.winner.id == player1.id


def test_invalid_hole_match(_db, test_match):
    """Test that a player cannot play against themselves"""
    player = Player(name="Player 1", match_id=test_match.id)
    _db.session.add(player)
    hole = Hole(num=1, match_id=test_match.id)
    _db.session.add(hole)
    _db.session.commit()

    hole_match = HoleMatch(
        hole_id=hole.id,
        match_id=test_match.id,
        player1_id=player.id,
        player2_id=player.id,  # Same player
    )
    _db.session.add(hole_match)

    with pytest.raises(Exception):
        _db.session.commit()
