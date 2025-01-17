from app.models import db, Match, Player, PointsTable, HoleMatch, Hole
from services.hole_service import HoleService
from flask_login import current_user


class MatchService:
    @staticmethod
    def get_all_matches():
        """Get all matches for the current user."""
        return (
            Match.query.filter_by(user_id=current_user.id)
            .order_by(Match.created_at.desc())
            .all()
        )

    @staticmethod
    def get_match(match_id):
        """Get a specific match, ensuring it belongs to the current user."""
        return Match.query.filter_by(
            id=match_id, user_id=current_user.id
        ).first_or_404()

    @staticmethod
    def create_match(player_names):
        """Create a new match with the given player names."""
        if len(player_names) != 4:
            raise ValueError("Exactly 4 player names are required")

        try:
            match = Match(user_id=current_user.id)
            db.session.add(match)
            db.session.flush()

            # Create players
            players = []
            for name in player_names:
                if not name.strip():
                    raise ValueError("Player names cannot be empty")
                player = Player(name=name, match=match)
                players.append(player)
                db.session.add(player)
            db.session.flush()

            # Create holes
            for i in range(1, 19):
                hole = HoleService.create_hole(
                    i, match.id, [player.id for player in players]
                )
                db.session.add(hole)

            # Create points table entries
            for player in players:
                points_table = PointsTable(match_id=match.id, player_id=player.id)
                db.session.add(points_table)

            db.session.commit()
            return match

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create match: {str(e)}")

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

            PointsTable.query.filter_by(match_id=match_id).delete()
            Hole.query.filter_by(match_id=match_id).delete()
            Player.query.filter_by(match_id=match_id).delete()
            db.session.delete(match)

            db.session.commit()
            return True
        return False
