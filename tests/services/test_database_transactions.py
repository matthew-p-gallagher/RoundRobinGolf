"""Tests for database transaction handling in services."""

import pytest
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
from app.services.hole_service import HoleService
from app.services.pointstable_service import PointstableService
from app.models import Match, Player, Hole, PointsTable


# Success Tests


def test_successful_match_creation_transaction(mocker, logged_in_user):
    """Test successful match creation commits once at the end"""
    mock_commit = mocker.patch("app.models.db.session.commit")

    # Create the match
    match = MatchService.create_match(["Player 1", "Player 2", "Player 3", "Player 4"])

    # Should commit only once at the end
    assert mock_commit.call_count == 1

    # Verify the match was created with all its related entities
    assert match.user_id == logged_in_user.id
    assert len(Player.query.filter_by(match_id=match.id).all()) == 4
    assert len(Hole.query.filter_by(match_id=match.id).all()) == 18
    assert len(PointsTable.query.filter_by(match_id=match.id).all()) == 4


def test_successful_hole_outcome_transaction(mocker, service_created_match):
    """Test successful hole outcome update commits once at the end"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    mock_commit = mocker.patch("app.models.db.session.commit")

    HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, -1])

    # Should commit only once at the end, not for each nested operation
    assert mock_commit.call_count == 1


def test_successful_pointstable_update_transaction(mocker, service_created_match):
    """Test successful points table update commits once at the end"""
    mock_commit = mocker.patch("app.models.db.session.commit")

    PointstableService.update_pointstable_for_all(service_created_match.id)

    # Should commit only once at the end
    assert mock_commit.call_count == 1


def test_successful_nested_transaction_control(mocker, service_created_match):
    """Test that nested operations don't commit until parent operation completes"""
    mock_commit = mocker.patch("app.models.db.session.commit")
    mock_scorecard = mocker.spy(PlayerService, "update_scorecard")
    mock_pointstable = mocker.spy(PointstableService, "update_pointstable_for_all")

    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, -1])

    # Verify nested operations were called with commit=False
    for call in mock_scorecard.call_args_list:
        assert call.kwargs.get("commit") is False

    assert mock_pointstable.call_args.kwargs.get("commit") is False
    # Only one commit at the end
    assert mock_commit.call_count == 1


# Error Tests


def test_create_match_database_error(mocker, logged_in_user):
    """Test match creation when database commit fails"""
    # Mock both flush and rollback before the test
    mock_flush = mocker.patch(
        "app.models.db.session.flush", side_effect=SQLAlchemyError("Database error")
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        MatchService.create_match(["Player 1", "Player 2", "Player 3", "Player 4"])

    assert "Failed to create match" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_create_match_nested_transaction_error(mocker, logged_in_user):
    """Test match creation when a nested operation fails"""
    mock_create_hole = mocker.patch(
        "app.services.hole_service.HoleService.create_hole",
        side_effect=SQLAlchemyError("Database error"),
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        MatchService.create_match(["Player 1", "Player 2", "Player 3", "Player 4"])

    assert "Failed to create match" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_handle_hole_outcome_nested_transaction_error(mocker, service_created_match):
    """Test hole outcome when player scorecard update fails"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    mock_update = mocker.patch(
        "app.services.player_service.PlayerService.update_scorecard",
        side_effect=SQLAlchemyError("Database error"),
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, -1])

    assert "Failed to update hole outcome" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_pointstable_nested_transaction_error(mocker, service_created_match):
    """Test points table update when player scorecard update fails"""
    mock_update = mocker.patch(
        "app.services.pointstable_service.PointstableService.update_pointstable_from_player_scorecard",
        side_effect=SQLAlchemyError("Database error"),
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        PointstableService.update_pointstable_for_all(service_created_match.id)

    assert "Failed to update points table" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_create_match_integrity_error(mocker, logged_in_user):
    """Test match creation with integrity constraint violation"""
    mocker.patch(
        "app.models.db.session.commit",
        side_effect=IntegrityError("statement", "params", "orig"),
    )

    with pytest.raises(Exception) as exc_info:
        MatchService.create_match(["Player 1", "Player 2", "Player 3", "Player 4"])
    assert "Failed to create match" in str(exc_info.value)


def test_delete_match_database_error(mocker, service_created_match):
    """Test match deletion when database operations fail"""
    mock_commit = mocker.patch(
        "app.models.db.session.commit", side_effect=SQLAlchemyError("Database error")
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        MatchService.delete_match(service_created_match.id)

    assert "Failed to delete match" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_update_player_scorecard_database_error(mocker, service_created_match):
    """Test updating player scorecard when database commit fails"""
    player = PlayerService.get_all_players(service_created_match.id)[0]
    mock_commit = mocker.patch(
        "app.models.db.session.commit", side_effect=SQLAlchemyError("Database error")
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        PlayerService.update_scorecard(player.id, 1, "W")

    assert "Failed to update scorecard" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_handle_hole_outcome_database_error(mocker, service_created_match):
    """Test handling hole outcome when database commit fails"""
    hole = HoleService.get_hole_by_match_hole_num(service_created_match.id, 1)
    mock_commit = mocker.patch(
        "app.models.db.session.commit", side_effect=SQLAlchemyError("Database error")
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        HoleService.handle_hole_outcome(service_created_match.id, hole.id, [-1, -1])

    assert "Failed to update hole outcome" in str(exc_info.value)
    assert mock_rollback.call_count == 1


def test_update_pointstable_database_error(mocker, service_created_match):
    """Test updating points table when database commit fails"""
    mock_commit = mocker.patch(
        "app.models.db.session.commit", side_effect=SQLAlchemyError("Database error")
    )
    mock_rollback = mocker.patch("app.models.db.session.rollback")

    with pytest.raises(Exception) as exc_info:
        PointstableService.update_pointstable_for_all(service_created_match.id)

    assert "Failed to update points table" in str(exc_info.value)
    assert mock_rollback.call_count == 1
