from app.models import Hole, HoleMatch
from app.services.player_service import PlayerService
from app.services.pointstable_service import PointstableService
from app import db
from sqlalchemy.exc import SQLAlchemyError


class HoleService:

    @staticmethod
    def create_hole(num: int, match_id: int, player_ids: list, commit: bool = False):
        """Create a new hole with its matches.

        Args:
            num: The hole number
            match_id: The ID of the match
            player_ids: List of player IDs
            commit: Whether to commit the transaction (default: False)
        """
        try:
            hole = Hole(num=num, match_id=match_id)
            db.session.add(hole)
            db.session.flush()

            matchups = [
                [(0, 1), (2, 3)],  # Hole 1, 4, 7, 10, 13, 16
                [(0, 2), (1, 3)],  # Hole 2, 5, 8, 11, 14, 17
                [(0, 3), (1, 2)],  # Hole 3, 6, 9, 12, 15, 18
            ][(num - 1) % 3]

            for matchup in matchups:
                holematch = HoleMatch(
                    hole_id=hole.id,
                    match_id=match_id,
                    player1_id=player_ids[matchup[0]],
                    player2_id=player_ids[matchup[1]],
                )
                db.session.add(holematch)

            if commit:
                db.session.commit()
            return hole
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create hole: {str(e)}")

    @staticmethod
    def get_hole(hole_id: int):
        """Get a hole by ID."""
        return Hole.query.get(hole_id)

    @staticmethod
    def get_hole_by_match_hole_num(match_id, hole_num):
        """Get a hole by match ID and hole number."""
        return Hole.query.filter_by(match_id=match_id, num=hole_num).first()

    @staticmethod
    def get_all_holes():
        """Get all holes."""
        return Hole.query.all()

    @staticmethod
    def handle_hole_outcome(match_id: int, hole_id: int, winners_ids: list):
        """Handle the outcome of a hole."""
        if len(winners_ids) != 2:
            raise ValueError("Must provide winner for each match")

        hole = HoleService.get_hole(hole_id)
        if not hole:
            raise ValueError("Hole not found")

        try:
            for holematch, winner_id in zip(hole.holematches, winners_ids):
                holematch.winner_id = winner_id

                if winner_id is None:
                    continue

                if winner_id == -1:
                    PlayerService.update_scorecard(
                        holematch.player1_id, hole.num, "D", commit=False
                    )
                    PlayerService.update_scorecard(
                        holematch.player2_id, hole.num, "D", commit=False
                    )
                else:
                    winner = (
                        holematch.player1
                        if winner_id == holematch.player1_id
                        else holematch.player2
                    )
                    loser = (
                        holematch.player2
                        if winner_id == holematch.player1_id
                        else holematch.player1
                    )
                    PlayerService.update_scorecard(
                        winner.id, hole.num, "W", commit=False
                    )
                    PlayerService.update_scorecard(
                        loser.id, hole.num, "L", commit=False
                    )

            PointstableService.update_pointstable_for_all(match_id, commit=False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if isinstance(e, ValueError):
                raise e
            raise Exception(f"Failed to update hole outcome: {str(e)}")

    @staticmethod
    def get_next_hole_num(hole_id: int) -> int:
        """Get the next hole number."""
        current_hole = Hole.query.get(hole_id)
        return current_hole.num + 1

    @staticmethod
    def get_previous_results(hole_id: int) -> dict:
        """Get previous hole results."""
        hole = Hole.query.get(hole_id)
        return {
            f"winner{i+1}": holematch.winner_id
            for i, holematch in enumerate(hole.holematches)
        }

    @staticmethod
    def get_first_incomplete_hole(match_id):
        """Get the first incomplete hole in a match."""
        holes = Hole.query.filter_by(match_id=match_id).order_by(Hole.num).all()
        for hole in holes:
            for holematch in hole.holematches:
                if holematch.winner_id is None:
                    return hole
        return None
