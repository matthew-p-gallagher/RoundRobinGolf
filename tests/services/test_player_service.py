import pytest
from app.services.player_service import PlayerService
from app.models import Player


def test_create_player(logged_in_user, service_created_match):
    """Test creating a new player"""
    player = PlayerService.create_player("Test Player", service_created_match.id)

    assert player.name == "Test Player"
    assert player.match_id == service_created_match.id
    assert player.scorecard == [None] * 18


@pytest.fixture
def service_created_player(service_created_match):
    """Create a player using the service method"""
    return PlayerService.create_player("Test Player", service_created_match.id)


def test_update_scorecard(service_created_player):
    """Test updating a player's scorecard"""
    # Update first hole result
    PlayerService.update_scorecard(service_created_player.id, 1, "W")
    player = PlayerService.get_player(service_created_player.id)
    assert player.scorecard[0] == "W"

    # Update second hole result
    PlayerService.update_scorecard(service_created_player.id, 2, "L")
    player = PlayerService.get_player(service_created_player.id)
    assert player.scorecard[1] == "L"

    # Verify other holes remain unchanged
    assert player.scorecard[2:] == [None] * 16


def test_update_scorecard_multiple_results(service_created_player):
    """Test updating multiple results in a scorecard"""
    results = ["W", "L", "D", "W"]
    for hole, result in enumerate(results, 1):
        PlayerService.update_scorecard(service_created_player.id, hole, result)

    player = PlayerService.get_player(service_created_player.id)
    assert player.scorecard[:4] == results
    assert player.scorecard[4:] == [None] * 14


def test_get_player(service_created_player):
    """Test retrieving a player by ID"""
    player = PlayerService.get_player(service_created_player.id)
    assert player.id == service_created_player.id
    assert player.name == service_created_player.name


def test_get_player_name(service_created_player):
    """Test retrieving just the player's name"""
    name = PlayerService.get_player_name(service_created_player.id)
    assert name == service_created_player.name


def test_get_player_name_nonexistent():
    """Test retrieving name of non-existent player"""
    name = PlayerService.get_player_name(999)
    assert name is None


def test_get_all_players(service_created_match):
    """Test retrieving all players for a match"""
    # Create multiple players
    players = [
        PlayerService.create_player(f"Player {i}", service_created_match.id)
        for i in range(1, 5)
    ]

    # Get all players
    all_players = PlayerService.get_all_players(service_created_match.id)
    assert len(all_players) == 4
    assert all(p.match_id == service_created_match.id for p in all_players)
    assert [p.name for p in all_players] == [f"Player {i}" for i in range(1, 5)]


def test_delete_player(service_created_player):
    """Test deleting a player"""
    player_id = service_created_player.id

    # Delete the player
    PlayerService.delete_player(player_id)

    # Verify player was deleted
    assert PlayerService.get_player(player_id) is None


def test_delete_nonexistent_player(_db):
    """Test attempting to delete a player that doesn't exist"""
    # Should not raise an exception
    PlayerService.delete_player(999)


def test_update_scorecard_invalid_hole_too_high(service_created_player):
    """Test updating scorecard with hole number > 18"""
    with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
        PlayerService.update_scorecard(service_created_player.id, 19, "W")


def test_update_scorecard_invalid_hole_too_low(service_created_player):
    """Test updating scorecard with hole number < 1"""
    with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
        PlayerService.update_scorecard(service_created_player.id, 0, "W")


def test_update_scorecard_invalid_result(service_created_player):
    """Test updating scorecard with invalid result"""
    with pytest.raises(
        ValueError,
        match="Result must be one of: W \\(win\\), L \\(loss\\), or D \\(draw\\)",
    ):
        PlayerService.update_scorecard(service_created_player.id, 1, "X")


def test_update_scorecard_nonexistent_player(_db):
    """Test updating scorecard for non-existent player"""
    with pytest.raises(ValueError, match="Player not found"):
        PlayerService.update_scorecard(999, 1, "W")


@pytest.mark.parametrize("result", ["W", "L", "D"])
def test_update_scorecard_valid_results(service_created_player, result):
    """Test all valid result values"""
    PlayerService.update_scorecard(service_created_player.id, 1, result)
    player = PlayerService.get_player(service_created_player.id)
    assert player.scorecard[0] == result
