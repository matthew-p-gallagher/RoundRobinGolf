from typing import List
from app.models import Player
from app import db


class PlayerService:
    VALID_RESULTS = {"W", "L", "D"}

    @staticmethod
    def create_player(name: str, match_id: int) -> Player:
        player = Player(name=name, match_id=match_id)
        db.session.add(player)
        db.session.flush()
        return player

    @staticmethod
    def update_scorecard(player_id: int, hole: int, result: str) -> None:
        if hole < 1 or hole > 18:
            raise ValueError("Hole number must be between 1 and 18")

        if result not in PlayerService.VALID_RESULTS:
            raise ValueError("Result must be one of: W (win), L (loss), or D (draw)")

        player = Player.query.get(player_id)
        if not player:
            raise ValueError("Player not found")

        scorecard = player.scorecard.copy()
        scorecard[hole - 1] = result
        player.scorecard = scorecard
        db.session.commit()

    @staticmethod
    def get_player(player_id: int):
        return Player.query.get(player_id)

    @staticmethod
    def get_player_name(player_id: int):
        player = Player.query.get(player_id)
        return player.name if player else None

    @staticmethod
    def get_all_players(match_id: int) -> List[Player]:
        return Player.query.filter_by(match_id=match_id).all()

    @staticmethod
    def delete_player(player_id: int) -> None:
        player = Player.query.get(player_id)
        if player:
            db.session.delete(player)
            db.session.commit()
