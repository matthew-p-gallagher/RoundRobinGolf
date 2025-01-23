import pytest
from app.services.pointstable_service import PointstableService
from app.services.player_service import PlayerService
from app.models import PointsTable


def test_create_pointsrow(service_created_match, service_created_player):
    """Test creating a single points table row"""
    pointsrow = PointstableService.create_pointsrow(
        service_created_match.id, service_created_player.id
    )

    assert pointsrow.match_id == service_created_match.id
    assert pointsrow.player_id == service_created_player.id
    assert pointsrow.thru == 0
    assert pointsrow.wins == 0
    assert pointsrow.draws == 0
    assert pointsrow.losses == 0
    assert pointsrow.points == 0


def test_create_pointstable(service_created_match):
    """Test creating a complete points table for all players in a match"""
    # Create multiple players
    players = [
        PlayerService.create_player(f"Player {i}", service_created_match.id)
        for i in range(1, 5)
    ]

    # Create points table
    pointstable = PointstableService.create_pointstable(service_created_match.id)

    assert len(pointstable) == 4
    for row, player in zip(pointstable, players):
        assert row.match_id == service_created_match.id
        assert row.player_id == player.id
        assert row.thru == 0
        assert row.wins == 0
        assert row.draws == 0
        assert row.losses == 0
        assert row.points == 0


@pytest.fixture
def service_created_pointsrow(service_created_match, service_created_player):
    """Create a points table row using the service method"""
    return PointstableService.create_pointsrow(
        service_created_match.id, service_created_player.id
    )


def test_get_pointsrow(
    service_created_pointsrow, service_created_match, service_created_player
):
    """Test retrieving a specific points table row"""
    row = PointstableService.get_pointsrow(
        service_created_match.id, service_created_player.id
    )
    assert row.match_id == service_created_match.id
    assert row.player_id == service_created_player.id


def test_get_pointstable(service_created_match):
    """Test retrieving the complete points table"""
    # Create players and points table
    players = [
        PlayerService.create_player(f"Player {i}", service_created_match.id)
        for i in range(1, 5)
    ]
    PointstableService.create_pointstable(service_created_match.id)

    # Get points table
    pointstable = PointstableService.get_pointstable(service_created_match.id)
    assert len(pointstable) == 4
    assert all(row.match_id == service_created_match.id for row in pointstable)


def test_get_formatted_pointstable(service_created_match):
    """Test retrieving formatted points table with player names"""
    # Create players with points
    players = [
        PlayerService.create_player(f"Player {i}", service_created_match.id)
        for i in range(1, 5)
    ]
    pointstable = PointstableService.create_pointstable(service_created_match.id)

    # Update some scores
    PlayerService.update_scorecard(players[0].id, 1, "W")  # 3 points
    PlayerService.update_scorecard(players[1].id, 1, "L")  # 0 points
    PlayerService.update_scorecard(players[2].id, 1, "D")  # 1 point

    # Update points table
    PointstableService.update_pointstable_for_all(service_created_match.id)

    # Get formatted table
    formatted = PointstableService.get_formatted_pointstable(service_created_match.id)

    assert len(formatted) == 4
    # First player should be the winner (Player 1)
    assert formatted[0]["player_name"] == "Player 1"
    assert formatted[0]["points"] == 3
    assert formatted[0]["wins"] == 1

    # Second player should be the one with draw (Player 3)
    assert formatted[1]["player_name"] == "Player 3"
    assert formatted[1]["points"] == 1
    assert formatted[1]["draws"] == 1


def test_update_pointstable_from_player_scorecard(
    service_created_match, service_created_player
):
    """Test updating points table from player's scorecard"""
    # Create points row
    pointsrow = PointstableService.create_pointsrow(
        service_created_match.id, service_created_player.id
    )

    # Update player's scorecard with various results
    PlayerService.update_scorecard(service_created_player.id, 1, "W")
    PlayerService.update_scorecard(service_created_player.id, 2, "L")
    PlayerService.update_scorecard(service_created_player.id, 3, "D")
    PlayerService.update_scorecard(service_created_player.id, 4, "W")

    # Update points table
    PointstableService.update_pointstable_from_player_scorecard(
        service_created_player.id
    )

    # Verify points calculation
    updated_row = PointstableService.get_pointsrow(
        service_created_match.id, service_created_player.id
    )
    assert updated_row.thru == 4
    assert updated_row.wins == 2  # 2 wins
    assert updated_row.draws == 1  # 1 draw
    assert updated_row.losses == 1  # 1 loss
    assert updated_row.points == 7  # (2 wins * 3) + (1 draw * 1) = 7 points


def test_update_pointstable_for_all(service_created_match):
    """Test updating points table for all players"""
    # Create players and points table
    players = [
        PlayerService.create_player(f"Player {i}", service_created_match.id)
        for i in range(1, 5)
    ]
    PointstableService.create_pointstable(service_created_match.id)

    # Update scorecards for all players
    for i, player in enumerate(players):
        PlayerService.update_scorecard(player.id, 1, "W" if i == 0 else "L")

    # Update points table
    PointstableService.update_pointstable_for_all(service_created_match.id)

    # Verify updates
    pointstable = PointstableService.get_pointstable(service_created_match.id)

    # First player should have a win
    winner_row = next(row for row in pointstable if row.player_id == players[0].id)
    assert winner_row.wins == 1
    assert winner_row.points == 3

    # Other players should have losses
    for player in players[1:]:
        loser_row = next(row for row in pointstable if row.player_id == player.id)
        assert loser_row.losses == 1
        assert loser_row.points == 0


def test_points_calculation():
    """Test points calculation logic"""
    # Create test data
    match = service_created_match
    player = PlayerService.create_player("Test Player", match.id)
    pointsrow = PointstableService.create_pointsrow(match.id, player.id)

    # Test different combinations of results
    test_cases = [
        (["W"], 3),  # Single win = 3 points
        (["D"], 1),  # Single draw = 1 point
        (["L"], 0),  # Single loss = 0 points
        (["W", "W"], 6),  # Two wins = 6 points
        (["W", "D"], 4),  # Win + Draw = 4 points
        (["W", "L"], 3),  # Win + Loss = 3 points
        (["D", "D"], 2),  # Two draws = 2 points
        (["W", "W", "D", "L"], 7),  # Complex case = 7 points
    ]

    for results, expected_points in test_cases:
        # Reset scorecard
        player.scorecard = [None] * 18

        # Apply results
        for hole, result in enumerate(results, 1):
            PlayerService.update_scorecard(player.id, hole, result)

        # Update points
        PointstableService.update_pointstable_from_player_scorecard(player.id)

        # Verify points
        updated_row = PointstableService.get_pointsrow(match.id, player.id)
        assert updated_row.points == expected_points, f"Failed for results {results}"
