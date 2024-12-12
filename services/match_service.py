from app.models import Match, Hole, Player, PointsTable, HoleMatch
from services.player_service import PlayerService
from services.hole_service import HoleService
from services.pointstable_service import PointstableService
from app import db


class MatchService:
    @staticmethod
    def create_match(player_names):
        match = Match()
        db.session.add(match)
        db.session.flush()

        # Create players and associate them with the match
        # TODO sort the 1 indexing
        player_ids = []
        for index, name in enumerate(player_names, start=1):
            player = PlayerService.create_player(name, match.id)
            player_ids.append(player.id)

        # Create 18 holes for the match
        holes = []
        for hole_number in range(1, 19):
            hole = HoleService.create_hole(hole_number, match.id, player_ids)
            db.session.add(hole)
            holes.append(hole)

        PointstableService.create_pointstable(match.id)

        db.session.commit()
        return match

    @staticmethod
    def get_match(match_id):
        return Match.query.get(match_id)

    @staticmethod
    def get_all_matches():
        return Match.query.all()

    @staticmethod
    def delete_match(match_id):
        match = Match.query.get(match_id)
        if match:
            # Delete related HoleMatch entries
            HoleMatch.query.filter(
                HoleMatch.hole_id.in_(
                    Hole.query.with_entities(Hole.id).filter_by(match_id=match_id)
                )
            ).delete(synchronize_session=False)

            # Delete related PointsTable entries
            PointsTable.query.filter_by(match_id=match_id).delete()

            # Delete related Hole entries
            Hole.query.filter_by(match_id=match_id).delete()

            # Delete related Player entries
            Player.query.filter_by(match_id=match_id).delete()

            # Delete the Match itself
            db.session.delete(match)

            db.session.commit()
            return True
        return False
