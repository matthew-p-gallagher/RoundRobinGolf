"""Tests for Match model."""

from datetime import datetime
from app.models import Match


def test_match_relationships(test_match, test_user, test_player):
    """Test match relationships"""
    assert test_match.user_id == test_user.id
    assert test_match.creator == test_user
    assert test_player in test_match.players
    assert not test_match.completed
    assert test_match.created_at is not None
    assert str(test_match) == f"<Match {test_match.id}>"


def test_match_completion(_db, test_match):
    """Test match completion status"""
    assert not test_match.completed
    test_match.completed = True
    _db.session.commit()
    assert test_match.completed


def test_match_creation_timestamp(_db, test_match):
    """Test that match creation timestamp is set"""
    assert isinstance(test_match.created_at, datetime)
    assert test_match.created_at <= datetime.now()
