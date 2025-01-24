import pytest
from flask import url_for


def test_home_page(client):
    """Test that the home page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Home" in response.data


def test_home_page_logged_in(client, logged_in_user):
    """Test that the home page loads correctly for logged in users"""
    response = client.get("/")
    assert response.status_code == 200
    assert logged_in_user.username.encode() in response.data
