"""Tests for User model."""

import pytest
from app.models import User


def test_new_user(_db):
    """Test creating a new user"""
    user = User(username="newuser", email="new@example.com")
    user.set_password("testpass123")

    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.check_password("testpass123")
    assert not user.check_password("wrongpass")
    assert user.is_active


def test_user_repr(test_user):
    """Test user string representation"""
    assert str(test_user) == f"<User {test_user.username}>"


def test_user_email_unique(_db):
    """Test that users cannot have duplicate emails"""
    user1 = User(username="user1", email="test@example.com")
    user2 = User(username="user2", email="test@example.com")
    _db.session.add(user1)
    _db.session.commit()

    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        _db.session.add(user2)
        _db.session.commit()


def test_user_username_unique(_db):
    """Test that usernames must be unique"""
    user1 = User(username="testuser", email="test1@example.com")
    user2 = User(username="testuser", email="test2@example.com")
    _db.session.add(user1)
    _db.session.commit()

    with pytest.raises(Exception):
        _db.session.add(user2)
        _db.session.commit()
