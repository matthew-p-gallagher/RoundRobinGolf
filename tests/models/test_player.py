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


def test_player_scorecard_modification(_db, test_player):
    """Test modifying player scorecard"""
    new_scorecard = [1] * 18
    test_player.scorecard = new_scorecard
    _db.session.commit()
    assert test_player.scorecard == new_scorecard
