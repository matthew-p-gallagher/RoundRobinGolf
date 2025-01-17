from app.models import Hole, HoleMatch
from services.player_service import PlayerService
from services.pointstable_service import PointstableService
from app import db


class HoleService:

    @staticmethod
    def create_hole(num: int, match_id: int, player_ids: list):
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

        return hole

    @staticmethod
    def get_hole(hole_id: int):
        return Hole.query.get(hole_id)

    @staticmethod
    def get_hole_by_match_hole_num(match_id, hole_num):
        return Hole.query.filter_by(match_id=match_id, num=hole_num).first()

    @staticmethod
    def get_all_holes():
        return Hole.query.all()

    @staticmethod
    def handle_hole_outcome(match_id: int, hole_id: int, winners_ids: list):

        hole = HoleService.get_hole(hole_id)

        for holematch, winner_id in zip(hole.holematches, winners_ids):
            holematch.winner_id = winner_id

            if winner_id is None:
                continue

            if winner_id == -1:
                PlayerService.update_scorecard(holematch.player1_id, hole.num, "D")
                PlayerService.update_scorecard(holematch.player2_id, hole.num, "D")
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
                PlayerService.update_scorecard(winner.id, hole.num, "W")
                PlayerService.update_scorecard(loser.id, hole.num, "L")

        PointstableService.update_pointstable_for_all(match_id)
        db.session.commit()

    @staticmethod
    def get_next_hole_num(hole_id: int) -> int:
        current_hole = Hole.query.get(hole_id)
        return current_hole.num + 1

    @staticmethod
    def get_previous_results(hole_id: int) -> dict:
        hole = Hole.query.get(hole_id)
        return {
            f"winner{i+1}": holematch.winner_id
            for i, holematch in enumerate(hole.holematches)
        }

    @staticmethod
    def get_first_incomplete_hole(match_id):
        holes = Hole.query.filter_by(match_id=match_id).order_by(Hole.num).all()
        for hole in holes:
            for holematch in hole.holematches:
                if holematch.winner_id is None:
                    return hole
        return None
