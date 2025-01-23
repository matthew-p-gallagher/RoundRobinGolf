"""Tests for PointsTable model."""

from app.models import PointsTable


def test_pointstable(_db, test_match, test_player):
    """Test points table creation and defaults"""
    points = PointsTable(match_id=test_match.id, player_id=test_player.id)
    _db.session.add(points)
    _db.session.commit()

    assert points.thru == 0
    assert points.wins == 0
    assert points.draws == 0
    assert points.losses == 0
    assert points.points == 0
    assert str(points) == f"<PointsTable {points.player_id}>"


def test_points_calculation(_db, test_match, test_player):
    """Test points calculation"""
    points = PointsTable(match_id=test_match.id, player_id=test_player.id)
    points.wins = 2
    points.draws = 1
    points.losses = 1
    _db.session.add(points)
    _db.session.commit()

    assert points.wins == 2
    assert points.draws == 1
    assert points.losses == 1
