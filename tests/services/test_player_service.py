import pytest
from app.services.player_service import PlayerService
from app.services.hole_service import HoleService
from app.models import Player


def test_player_creation_from_match(service_created_match):
    """Test that players are created correctly when a match is created"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()

    # Should have all 4 players
    assert len(players) == 4

    # Verify player names and initial scorecards
    for i, player in enumerate(players, 1):
        assert player.name == f"Player {i}"
        assert player.match_id == service_created_match.id
        assert len(player.scorecard) == 18
        assert all(result is None for result in player.scorecard)


def test_get_player(service_created_match):
    """Test retrieving a player"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    first_player = players[0]

    retrieved = PlayerService.get_player(first_player.id)
    assert retrieved.id == first_player.id
    assert retrieved.name == first_player.name


def test_get_player_name(service_created_match):
    """Test retrieving just the player name"""
    players = Player.query.filter_by(match_id=service_created_match.id).all()
    first_player = players[0]

    name = PlayerService.get_player_name(first_player.id)
    assert name == "Player 1"


def test_get_all_players(service_created_match):
    """Test retrieving all players for a match"""
    players = PlayerService.get_all_players(service_created_match.id)
    assert len(players) == 4
    assert all(player.match_id == service_created_match.id for player in players)
    assert [player.name for player in players] == [f"Player {i}" for i in range(1, 5)]


def test_scorecard_updates_from_hole_outcomes(service_created_match):
    """Test that player scorecards are updated correctly from hole outcomes"""
    # Get first hole and record an outcome
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    holematch1, holematch2 = hole.holematches

    # Record wins for first player in each match
    HoleService.handle_hole_outcome(
        service_created_match.id,
        hole.id,
        [holematch1.player1_id, holematch2.player1_id],
    )

    # Verify scorecards
    players = PlayerService.get_all_players(service_created_match.id)
    player_results = {player.id: player for player in players}

    # Winners should have "W"
    assert player_results[holematch1.player1_id].scorecard[0] == "W"
    assert player_results[holematch2.player1_id].scorecard[0] == "W"

    # Losers should have "L"
    assert player_results[holematch1.player2_id].scorecard[0] == "L"
    assert player_results[holematch2.player2_id].scorecard[0] == "L"


def test_scorecard_updates_with_draws(service_created_match):
    """Test scorecard updates with draws"""
    # Get first hole
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)

    # Record all draws
    HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, -1])

    # Verify all players have "D" for first hole
    players = PlayerService.get_all_players(service_created_match.id)
    for player in players:
        assert player.scorecard[0] == "D"


def test_scorecard_multiple_holes(service_created_match):
    """Test scorecard updates across multiple holes"""
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

    # Verify final scorecards
    players = PlayerService.get_all_players(service_created_match.id)
    player_results = {player.name: player.scorecard[:3] for player in players}

    assert player_results["Player 1"] == ["W", "D", "W"]
    assert player_results["Player 2"] == ["L", "D", "L"]
    assert player_results["Player 3"] == ["D", "D", "W"]
    assert player_results["Player 4"] == ["D", "D", "L"]
