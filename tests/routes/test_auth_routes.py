import pytest
from flask import url_for
from app.models import User


def test_login_page(client):
    """Test that the login page loads correctly"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_login_authenticated_redirect(client, logged_in_user):
    """Test that authenticated users are redirected from login page"""
    response = client.get("/auth/login", follow_redirects=True)
    assert response.status_code == 200
    assert b"Home" in response.data


def test_login_with_next(client, test_user):
    """Test login with next parameter"""
    # First get the login page to get the CSRF token
    response = client.get("/auth/login?next=/matches/")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        "/auth/login?next=/matches/",
        data={
            "username": "testuser",
            "password": "password123",
            "remember_me": False,
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"matches" in response.data.lower()


def test_register_authenticated_redirect(client, logged_in_user):
    """Test that authenticated users are redirected from register page"""
    response = client.get("/auth/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"Home" in response.data


def test_successful_login(client, test_user):
    """Test successful login with correct credentials"""
    # First get the login page to get the CSRF token
    response = client.get("/auth/login")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    # Now post the login form with the CSRF token
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "password123",
            "remember_me": False,
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" not in response.data


def test_failed_login(client):
    """Test login with incorrect credentials"""
    # First get the login page to get the CSRF token
    response = client.get("/auth/login")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        "/auth/login",
        data={
            "username": "wronguser",
            "password": "wrongpass",
            "remember_me": False,
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


def test_logout(client, logged_in_user):
    """Test logout functionality"""
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_register_page(client):
    """Test that the registration page loads correctly"""
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_successful_registration(client):
    """Test successful user registration"""
    # First get the registration page to get the CSRF token
    response = client.get("/auth/register")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "password2": "newpass123",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Verify user was created
    user = User.query.filter_by(username="newuser").first()
    assert user is not None
    # Verify success message
    assert b"Registration successful" in response.data
    # Verify redirect to home page
    assert b"Home" in response.data


def test_registration_auto_login(client):
    """Test that users are automatically logged in after registration"""
    # Get CSRF token
    response = client.get("/auth/register")
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    # Register new user
    response = client.post(
        "/auth/register",
        data={
            "username": "autologinuser",
            "email": "autologin@example.com",
            "password": "password123",
            "password2": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )

    # Verify user is logged in
    response = client.get("/matches/")  # This route requires login
    assert response.status_code == 200
    assert b"matches" in response.data.lower()  # Can access protected route

    # Try accessing register page (should redirect since authenticated)
    response = client.get("/auth/register")
    assert response.status_code == 302  # Redirect status code
    response = client.get("/auth/register", follow_redirects=True)
    assert b"Home" in response.data  # Redirects to home as authenticated user


def test_duplicate_registration(client, test_user):
    """Test registration with existing username"""
    # First get the registration page to get the CSRF token
    response = client.get("/auth/register")
    assert response.status_code == 200
    html = response.data.decode()
    csrf_token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123",
            "password2": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Please use a different username" in response.data
