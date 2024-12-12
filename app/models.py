from . import db
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.sqlite import JSON


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    # order = db.Column(db.Integer, nullable=False)
    # handicap = db.Column(db.Float, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    scorecard = db.Column(JSON, default=lambda: [None] * 18)

    def __repr__(self):
        return f"<Player {self.id} {self.name}>"


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    players = relationship("Player", backref="match", lazy=True)
    holes = relationship("Hole", backref="match", lazy=True)
    pointstable = relationship("PointsTable", backref="match", lazy=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Match {self.id}>"


class PointsTable(db.Model):
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), primary_key=True)
    thru = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<PointsTable {self.player_id}>"


class Hole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)

    holematches = relationship("HoleMatch", backref="hole", lazy=True)

    def __repr__(self):
        return f"<Hole {self.num}>"


class HoleMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hole_id = db.Column(db.Integer, db.ForeignKey("hole.id"), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=True)

    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    winner = relationship("Player", foreign_keys=[winner_id])

    def __repr__(self):
        return f"<HoleMatch {self.id} for Hole {self.hole_id}>"
