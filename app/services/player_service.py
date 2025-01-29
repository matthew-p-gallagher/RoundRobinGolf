from typing import List
from app.models import Player
from app import db
from sqlalchemy.exc import SQLAlchemyError


class PlayerService:
    VALID_RESULTS = {"W", "L", "D"}

    @staticmethod
    def create_player(name: str, match_id: int, commit: bool = True) -> Player:
        """Create a new player.

        Args:
            name: The player's name
            match_id: The ID of the match
            commit: Whether to commit the transaction (default: True)
        """
        try:
            player = Player(name=name, match_id=match_id)
            db.session.add(player)
            db.session.flush()

            if commit:
                db.session.commit()
            return player
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create player: {str(e)}")

    @staticmethod
    def update_scorecard(
        player_id: int, hole: int, result: str, commit: bool = True
    ) -> None:
        """Update a player's scorecard.

        Args:
            player_id: The ID of the player
            hole: The hole number (1-18)
            result: The result (W/L/D)
            commit: Whether to commit the transaction (default: True)
        """
        if hole < 1 or hole > 18:
            raise ValueError("Hole number must be between 1 and 18")

        if result not in PlayerService.VALID_RESULTS:
            raise ValueError("Result must be one of: W (win), L (loss), or D (draw)")

        try:
            player = db.session.get(Player, player_id)
            if not player:
                raise ValueError("Player not found")

            scorecard = player.scorecard.copy()
            scorecard[hole - 1] = result
            player.scorecard = scorecard

            if commit:
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update scorecard: {str(e)}")
        except ValueError as e:
            raise e

    @staticmethod
    def get_player(player_id: int):
        """Get a player by ID."""
        return db.session.get(Player, player_id)

    @staticmethod
    def get_player_name(player_id: int):
        """Get a player's name."""
        player = db.session.get(Player, player_id)
        return player.name if player else None

    @staticmethod
    def get_all_players(match_id: int) -> List[Player]:
        """Get all players for a match."""
        return Player.query.filter_by(match_id=match_id).all()

    @staticmethod
    def delete_player(player_id: int, commit: bool = True) -> None:
        """Delete a player.

        Args:
            player_id: The ID of the player
            commit: Whether to commit the transaction (default: True)
        """
        try:
            player = db.session.get(Player, player_id)
            if player:
                db.session.delete(player)
                if commit:
                    db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to delete player: {str(e)}")
