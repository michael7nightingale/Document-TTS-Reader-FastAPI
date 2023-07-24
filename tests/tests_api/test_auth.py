import pytest
from fastapi import status

from tests_api.conftest import get_auth_url


class TestMain:
    async def test_token_bad_request(self, client):
        user_nonexisted_data = {
            "password": "user1['password']",
            "username": "user1['username']"
        }
        response = await client.post(
            get_auth_url("get_token"),
            json=user_nonexisted_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Invalid credentials provided."}

    async def test_token_success(self, client, users_test_data, user1):
        user_existed_data = {
            "password": user1['password'],
            "username": user1['username']
        }
        response = await client.post(
            get_auth_url("get_token"),
            json=user_existed_data
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_register_user(self, client, user1):
        response = await client.post(
            get_auth_url("register"),
            json=user1
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == f"Activation link is send on email {user1['email']}"

    async def test_register_not_active(self, client, user1):
        response = await client.post(
            get_auth_url("register"),
            json=user1
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == f"Activation link is send on email {user1['email']}"
        user_existed_data = {
            "password": user1['password'],
            "username": user1['username']
        }
        response = await client.post(
            get_auth_url("get_token"),
            json=user_existed_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Invalid credentials provided."}

    async def test_me_success(self, authorized_client, user2):
        response = await authorized_client.get(get_auth_url("me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == user2['username']
        assert response.json()["email"] == user2['email']
        assert response.json()["is_active"]
        assert response.json()["is_authnticated"]
        assert "id" in response.json()
