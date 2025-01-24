import pytest
from flask import url_for
from app.models import Match, Player, User


@pytest.fixture
def other_user(_db):
    """Create another user for testing access control"""
    user = User(username="otheruser", email="other@example.com")
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def other_user_match(_db, other_user):
    """Create a match owned by other_user"""
    match = Match(user_id=other_user.id)
    _db.session.add(match)
    _db.session.commit()
    return match


def test_matches_page_requires_login(client):
    """Test that the matches page requires login"""
    response = client.get("/matches/", follow_redirects=True)
    assert b"Please log in to access this page" in response.data


def test_matches_page(client, logged_in_user):
    """Test that the matches page loads correctly for logged in user"""
    response = client.get("/matches/")
    assert response.status_code == 200
    assert b"matches" in response.data.lower()


def test_new_match_page(client, logged_in_user):
    """Test that the new match page loads correctly"""
    response = client.get("/matches/new")
    assert response.status_code == 200
    assert b"new match" in response.data.lower()


def test_create_match(client, logged_in_user):
    """Test creating a new match"""
    # First get the new match page to get the CSRF token
    response = client.get("/matches/new")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        "/matches/start",
        data={
            "player1": "Player One",
            "player2": "Player Two",
            "player3": "Player Three",
            "player4": "Player Four",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"New match created successfully!" in response.data

    # Verify match was created in database
    match = Match.query.first()
    assert match is not None
    players = Player.query.filter_by(match_id=match.id).all()
    assert len(players) == 4


def test_match_overview(client, service_created_match, logged_in_user):
    """Test viewing match overview"""
    response = client.get(f"/matches/{service_created_match.id}")
    assert response.status_code == 200


def test_match_overview_404(client, logged_in_user):
    """Test viewing non-existent match returns 404"""
    response = client.get("/matches/999")
    assert response.status_code == 404


def test_delete_match(client, service_created_match, logged_in_user):
    """Test deleting a match"""
    match_id = service_created_match.id
    response = client.get(f"/matches/delete/{match_id}", follow_redirects=True)
    assert response.status_code == 200
    assert Match.query.get(match_id) is None


def test_finish_round_incomplete(client, service_created_match, logged_in_user):
    """Test finishing a round with incomplete holes"""
    response = client.get(
        f"/matches/finish/{service_created_match.id}", follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Cannot finish round" in response.data


def test_hole_view(client, service_created_match, logged_in_user):
    """Test viewing a specific hole"""
    response = client.get(f"/matches/{service_created_match.id}/hole/1")
    assert response.status_code == 200


def test_process_hole(client, service_created_match, logged_in_user):
    """Test processing hole results"""
    # First get the hole page to get the CSRF token
    match_id = service_created_match.id
    response = client.get(f"/matches/{match_id}/hole/1")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        f"/matches/{match_id}/hole/1/process",
        data={
            "winner1": "1",
            "winner2": "2",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_match_other_user_404(client, logged_in_user, other_user_match):
    """Test that accessing another user's match returns 404"""
    response = client.get(f"/matches/{other_user_match.id}")
    assert response.status_code == 404


def test_delete_other_user_match(client, logged_in_user, other_user_match):
    """Test that deleting another user's match fails"""
    match_id = other_user_match.id
    response = client.get(f"/matches/delete/{match_id}", follow_redirects=True)
    assert response.status_code == 404
    assert Match.query.get(match_id) is not None


def test_hole_invalid_number(client, service_created_match, logged_in_user):
    """Test accessing an invalid hole number"""
    response = client.get(f"/matches/{service_created_match.id}/hole/999")
    assert response.status_code == 200


def test_process_hole_with_draws(client, service_created_match, logged_in_user):
    """Test processing hole results with draws"""
    # First get the hole page to get the CSRF token
    match_id = service_created_match.id
    response = client.get(f"/matches/{match_id}/hole/1")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        f"/matches/{match_id}/hole/1/process",
        data={
            "winner1": "draw",
            "winner2": "draw",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_process_hole_missing_winners(client, service_created_match, logged_in_user):
    """Test processing hole results with missing winners"""
    # First get the hole page to get the CSRF token
    match_id = service_created_match.id
    response = client.get(f"/matches/{match_id}/hole/1")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        f"/matches/{match_id}/hole/1/process",
        data={
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
