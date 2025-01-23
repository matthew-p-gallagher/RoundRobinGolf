import pytest
from app import create_app, db
from app.models import User, Player, Match, PointsTable, Hole, HoleMatch
from flask_login import login_user


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
