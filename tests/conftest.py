import pytest
from app import create_app, db
from app.models import User, Player, Match, PointsTable, Hole, HoleMatch
from flask_login import login_user
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
from app.services.pointstable_service import PointstableService


@pytest.fixture
def app():
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def _db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(_db):
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def logged_in_user(_db, test_user):
    """Fixture for a logged-in user"""
    login_user(test_user)
    return test_user


@pytest.fixture
def test_match(_db, test_user):
    match = Match(user_id=test_user.id)
    _db.session.add(match)
    _db.session.commit()
    return match


@pytest.fixture
def test_player(_db, test_match):
    player = Player(name="Test Player", match_id=test_match.id)
    _db.session.add(player)
    _db.session.commit()
    return player


@pytest.fixture
def service_created_match(logged_in_user):
    """Create a match using the service method"""
    player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
    return MatchService.create_match(player_names)


@pytest.fixture
def service_created_player(service_created_match):
    """Create a player using the service method"""
    return PlayerService.create_player("Test Player", service_created_match.id)


@pytest.fixture
def service_created_pointsrow(service_created_match, service_created_player):
    """Create a points table row using the service method"""
    return PointstableService.create_pointsrow(
        service_created_match.id, service_created_player.id
    )
