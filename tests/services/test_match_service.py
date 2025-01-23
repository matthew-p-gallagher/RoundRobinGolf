import pytest
from app.services.match_service import MatchService
from app.models import Match, Player, PointsTable, Hole, HoleMatch


def test_create_match(logged_in_user):
    """Test creating a new match with players"""
    player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
    match = MatchService.create_match(player_names)

    # Verify match was created
    assert match.user_id == logged_in_user.id

    # Verify players were created
    players = Player.query.filter_by(match_id=match.id).all()
    assert len(players) == 4
    assert [p.name for p in players] == player_names

    # Verify holes were created
    holes = Hole.query.filter_by(match_id=match.id).all()
    assert len(holes) == 18
    assert [h.num for h in holes] == list(range(1, 19))

    # Verify points table entries were created
    points = PointsTable.query.filter_by(match_id=match.id).all()
    assert len(points) == 4


def test_create_match_invalid_players(logged_in_user):
    """Test creating a match with invalid number of players"""
    with pytest.raises(ValueError, match="Exactly 4 player names are required"):
        MatchService.create_match(["Player 1", "Player 2", "Player 3"])


def test_create_match_empty_name(logged_in_user):
    """Test creating a match with an empty player name"""
    with pytest.raises(ValueError, match="Player names cannot be empty"):
        MatchService.create_match(["Player 1", "", "Player 3", "Player 4"])


@pytest.fixture
def service_created_match(logged_in_user):
    """Fixture that creates a match using the service method"""
    player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
    return MatchService.create_match(player_names)


@pytest.fixture
def matches(logged_in_user):
    """Fixture creating multiple test matches using the service"""
    matches = [
        MatchService.create_match([f"Player {i}" for i in range(1, 5)]),
        MatchService.create_match([f"Player {i}" for i in range(5, 9)]),
    ]
    return matches


def test_get_all_matches(logged_in_user, matches):
    """Test retrieving all matches for a user"""
    matches = MatchService.get_all_matches()
    assert len(matches) == 2
    assert all(match.user_id == logged_in_user.id for match in matches)


def test_get_match(logged_in_user, service_created_match):
    """Test retrieving a specific match"""
    match = MatchService.get_match(service_created_match.id)
    assert match.id == service_created_match.id
    assert match.user_id == logged_in_user.id


def test_delete_match(service_created_match):
    """Test deleting a match and all related entities"""
    match_id = service_created_match.id

    # Delete the match
    result = MatchService.delete_match(match_id)
    assert result is True

    # Verify everything was deleted
    assert Match.query.get(match_id) is None
    assert Player.query.filter_by(match_id=match_id).first() is None
    assert Hole.query.filter_by(match_id=match_id).first() is None
    assert PointsTable.query.filter_by(match_id=match_id).first() is None
    assert HoleMatch.query.filter_by(match_id=match_id).first() is None


def test_delete_nonexistent_match(_db):
    """Test attempting to delete a match that doesn't exist"""
    result = MatchService.delete_match(999)
    assert result is False
