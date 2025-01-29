from typing import List, Dict
from app.models import PointsTable, Player
from app.services.player_service import PlayerService
from app import db
from sqlalchemy.exc import SQLAlchemyError


class PointstableService:
    @staticmethod
    def create_pointsrow(
        match_id: int, player_id: int, commit: bool = True
    ) -> PointsTable:
        """Create a new points table row.

        Args:
            match_id: The ID of the match
            player_id: The ID of the player
            commit: Whether to commit the transaction (default: True)
        """
        try:
            pointsrow = PointsTable(match_id=match_id, player_id=player_id)
            db.session.add(pointsrow)

            if commit:
                db.session.commit()
            return pointsrow
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create points table row: {str(e)}")

    @staticmethod
    def create_pointstable(match_id: int, commit: bool = True) -> List[PointsTable]:
        """Create a complete points table for a match.

        Args:
            match_id: The ID of the match
            commit: Whether to commit the transaction (default: True)
        """
        try:
            players = PlayerService.get_all_players(match_id)
            pointstable = []
            for player in players:
                pointsrow = PointstableService.create_pointsrow(
                    match_id, player.id, commit=False
                )
                pointstable.append(pointsrow)

            if commit:
                db.session.commit()
            return pointstable
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create points table: {str(e)}")

    @staticmethod
    def get_pointsrow(match_id: int, player_id: int) -> PointsTable:
        """Get a specific points table row."""
        return db.session.get(PointsTable, (match_id, player_id))

    @staticmethod
    def get_pointstable(match_id: int) -> List[PointsTable]:
        """Get the complete points table for a match."""
        return PointsTable.query.filter_by(match_id=match_id).all()

    @staticmethod
    def get_formatted_pointstable(match_id: int) -> List[Dict]:
        """Get a formatted points table for display."""
        try:
            pointstable = PointsTable.query.filter_by(match_id=match_id).all()
            formatted_table = []
            for row in pointstable:
                player = PlayerService.get_player(row.player_id)
                formatted_row = {
                    "player_name": player.name,
                    "thru": row.thru,
                    "wins": row.wins,
                    "draws": row.draws,
                    "losses": row.losses,
                    "points": row.points,
                }
                formatted_table.append(formatted_row)

            # Sort final_results by points in descending order, then by wins
            formatted_table.sort(key=lambda x: (x["points"], x["wins"]), reverse=True)
            return formatted_table
        except SQLAlchemyError as e:
            raise Exception(f"Failed to get formatted points table: {str(e)}")

    @staticmethod
    def update_pointstable_from_player_scorecard(
        player_id: int, commit: bool = True
    ) -> None:
        """Update points table from a player's scorecard.

        Args:
            player_id: The ID of the player
            commit: Whether to commit the transaction (default: True)
        """
        try:
            player = db.session.get(Player, player_id)
            if not player:
                raise ValueError("Player not found")

            pointsrow = db.session.get(PointsTable, (player.match_id, player_id))
            if not pointsrow:
                raise ValueError("Points table row not found")

            scorecard = player.scorecard
            if not all(score in [None, "W", "L", "D"] for score in scorecard):
                raise ValueError("Invalid scorecard entry")

            pointsrow.thru = len([score for score in scorecard if score is not None])
            pointsrow.wins = scorecard.count("W")
            pointsrow.draws = scorecard.count("D")
            pointsrow.losses = scorecard.count("L")
            pointsrow.points = pointsrow.wins * 3 + pointsrow.draws

            if commit:
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update points table row: {str(e)}")
        except ValueError as e:
            raise e

    @staticmethod
    def update_pointstable_for_all(match_id: int, commit: bool = True):
        """Update points table for all players in a match.

        Args:
            match_id: The ID of the match
            commit: Whether to commit the transaction (default: True)
        """
        try:
            players = Player.query.filter_by(match_id=match_id).all()
            if not players:
                raise ValueError("No players found for match")

            for player in players:
                PointstableService.update_pointstable_from_player_scorecard(
                    player.id, commit=False
                )

            if commit:
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update points table: {str(e)}")
        except ValueError as e:
            raise e

    @staticmethod
    def delete_pointstable(pointstable_id: int) -> None:
        """Delete a points table row."""
        try:
            pointstable = db.session.get(PointsTable, pointstable_id)
            if pointstable:
                db.session.delete(pointstable)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to delete points table row: {str(e)}")
