import pytest
from app.models import User, Player, Match, PointsTable, Hole, HoleMatch


def test_new_user(_db):
    """Test creating a new user"""
    user = User(username="newuser", email="new@example.com")
    user.set_password("testpass123")

    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.check_password("testpass123")
    assert not user.check_password("wrongpass")
    assert user.is_active


def test_user_repr(test_user):
    """Test user string representation"""
    assert str(test_user) == f"<User {test_user.username}>"


def test_new_player(_db, test_match):
    """Test creating a new player"""
    player = Player(name="John Doe", match_id=test_match.id)
    _db.session.add(player)
    _db.session.commit()

    assert player.name == "John Doe"
    assert player.match_id == test_match.id
    assert player.scorecard == [None] * 18
    assert str(player) == f"<Player {player.id} John Doe>"


def test_match_relationships(test_match, test_user, test_player):
    """Test match relationships"""
    assert test_match.user_id == test_user.id
    assert test_match.creator == test_user
    assert test_player in test_match.players
    assert not test_match.completed
    assert test_match.created_at is not None
    assert str(test_match) == f"<Match {test_match.id}>"


def test_points_table(_db, test_match, test_player):
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


def test_hole(_db, test_match):
    """Test hole creation"""
    hole = Hole(num=1, match_id=test_match.id)
    _db.session.add(hole)
    _db.session.commit()

    assert hole.num == 1
    assert hole.match_id == test_match.id
    assert str(hole) == f"<Hole {hole.num}>"


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
