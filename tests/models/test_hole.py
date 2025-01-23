"""Tests for Hole model."""

from app.models import Hole


def test_hole(_db, test_match):
    """Test hole creation"""
    hole = Hole(num=1, match_id=test_match.id)
    _db.session.add(hole)
    _db.session.commit()

    assert hole.num == 1
    assert hole.match_id == test_match.id
    assert str(hole) == f"<Hole {hole.num}>"
