import pytest
from app.services.pointstable_service import PointstableService
from app.services.hole_service import HoleService
from app.models import PointsTable


def test_pointstable_creation_from_match(service_created_match):
    """Test that points table is created correctly when a match is created"""
    pointstable = PointsTable.query.filter_by(match_id=service_created_match.id).all()

    # Should have one row per player
    assert len(pointstable) == 4

    # All rows should start with zero values
    for row in pointstable:
        assert row.match_id == service_created_match.id
        assert row.thru == 0
        assert row.wins == 0
        assert row.draws == 0
        assert row.losses == 0
        assert row.points == 0


def test_get_pointstable(service_created_match):
    """Test retrieving the complete points table"""
    pointstable = PointstableService.get_pointstable(service_created_match.id)
    assert len(pointstable) == 4
    assert all(row.match_id == service_created_match.id for row in pointstable)


def test_get_formatted_pointstable_after_results(service_created_match):
    """Test retrieving formatted points table after recording some results"""
    # Get first hole and its matches
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch1, holematch2 = hole.holematches

    # Record a win and a draw
    HoleService.handle_hole_outcome(
        service_created_match.id,
        hole.id,
        [holematch1.player1_id, -1],  # First player wins, second match is a draw
    )

    # Get formatted table
    formatted = PointstableService.get_formatted_pointstable(service_created_match.id)

    # Verify formatting and sorting
    assert len(formatted) == 4

    # Winner should be first (3 points)
    assert formatted[0]["points"] == 3
    assert formatted[0]["wins"] == 1
    assert formatted[0]["player_name"] == "Player 1"

    # Draw players should be next (1 point each)
    assert formatted[1]["points"] == 1
    assert formatted[1]["draws"] == 1
    assert formatted[2]["points"] == 1
    assert formatted[2]["draws"] == 1


def test_points_calculation_through_match(service_created_match):
    """Test points calculation through a series of hole results"""
    # Complete first three holes with different outcomes
    for hole_num in range(1, 4):
        hole = HoleService.get_hole_by_match_hole_num(
            service_created_match.id, hole_num
        )
        holematch1, holematch2 = hole.holematches

        if hole_num == 1:
            # Hole 1: Player 1 wins, Players 3&4 draw
            winners = [holematch1.player1_id, -1]
        elif hole_num == 2:
            # Hole 2: All draws
            winners = [-1, -1]
        else:
            # Hole 3: Players 1&3 win
            winners = [holematch1.player1_id, holematch2.player2_id]

        HoleService.handle_hole_outcome(service_created_match.id, hole.id, winners)

    # Get final table
    formatted = PointstableService.get_formatted_pointstable(service_created_match.id)

    # Verify each player's results
    player_results = {row["player_name"]: row for row in formatted}

    # Player 1: 2 win, 1 draw, 0 loss = 7 points
    assert player_results["Player 1"]["points"] == 7
    assert player_results["Player 1"]["wins"] == 2
    assert player_results["Player 1"]["draws"] == 1
    assert player_results["Player 1"]["losses"] == 0

    # Player 2: 0 win, 1 draw, 2 loss = 1 point
    assert player_results["Player 2"]["points"] == 1
    assert player_results["Player 2"]["wins"] == 0
    assert player_results["Player 2"]["draws"] == 1
    assert player_results["Player 2"]["losses"] == 2

    # Player 3: 1 win, 2 draws = 5 points
    assert player_results["Player 3"]["points"] == 5
    assert player_results["Player 3"]["wins"] == 1
    assert player_results["Player 3"]["draws"] == 2
    assert player_results["Player 3"]["losses"] == 0

    # Player 4: 2 draws, 1 loss = 2 points
    assert player_results["Player 4"]["points"] == 2
    assert player_results["Player 4"]["wins"] == 0
    assert player_results["Player 4"]["draws"] == 2
    assert player_results["Player 4"]["losses"] == 1


def test_thru_calculation(service_created_match):
    """Test that thru holes are calculated correctly"""
    # Complete first two holes
    for i in range(1, 3):
        hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, i)
        HoleService.handle_hole_outcome(
            service_created_match.id,
            hole.id,
            [hole.holematches[0].player1_id, hole.holematches[1].player1_id],
        )

    # Check thru holes count
    pointstable = PointstableService.get_pointstable(service_created_match.id)
    assert all(row.thru == 2 for row in pointstable)
