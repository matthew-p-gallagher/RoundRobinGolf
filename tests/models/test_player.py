"""Tests for Player model."""

from app.models import Player


def test_new_player(_db, test_match):
    """Test creating a new player"""
    player = Player(name="John Doe", match_id=test_match.id)
    _db.session.add(player)
    _db.session.commit()

    assert player.name == "John Doe"
    assert player.match_id == test_match.id
    assert player.scorecard == [None] * 18
    assert str(player) == f"<Player {player.id} John Doe>"
