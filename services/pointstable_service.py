from typing import List, Dict
from app.models import PointsTable, Player
from services.player_service import PlayerService
from app import db


class PointstableService:
    @staticmethod
    def create_pointsrow(match_id: int, player_id: int) -> PointsTable:
        pointsrow = PointsTable(match_id=match_id, player_id=player_id)
        db.session.add(pointsrow)
        return pointsrow

    @staticmethod
    def create_pointstable(match_id: int) -> List[PointsTable]:
        players = PlayerService.get_all_players(match_id)
        pointstable = []
        for player in players:
            pointsrow = PointstableService.create_pointsrow(match_id, player.id)
            db.session.add(pointsrow)
            pointstable.append(pointsrow)
        db.session.commit()
        return pointstable

    @staticmethod
    def get_pointsrow(match_id: int, player_id: int) -> PointsTable:
        return PointsTable.query.get((match_id, player_id))

    @staticmethod
    def get_pointstable(match_id: int) -> List[PointsTable]:
        return PointsTable.query.filter_by(match_id=match_id).all()

    @staticmethod
    def get_formatted_pointstable(match_id: int) -> List[Dict]:
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

    @staticmethod
    def update_pointstable_from_player_scorecard(player_id: int) -> None:
        player = Player.query.get(player_id)
        pointsrow = PointsTable.query.get((player.match_id, player_id))

        scorecard = player.scorecard
        pointsrow.thru = len([score for score in scorecard if score is not None])
        pointsrow.wins = scorecard.count("W")
        pointsrow.draws = scorecard.count("D")
        pointsrow.losses = scorecard.count("L")
        pointsrow.points = pointsrow.wins * 3 + pointsrow.draws

        db.session.commit()

    @staticmethod
    def update_pointstable_for_all(match_id: int):
        players = Player.query.filter_by(match_id=match_id).all()

        for player in players:
            PointstableService.update_pointstable_from_player_scorecard(player.id)

    @staticmethod
    def delete_pointstable(pointstable_id: int) -> None:
        pointstable = PointsTable.query.get(pointstable_id)
        if pointstable:
            db.session.delete(pointstable)
            db.session.commit()
