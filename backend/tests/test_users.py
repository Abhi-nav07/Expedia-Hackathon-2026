"""
Tests for the /users/* endpoints.
"""
import io

VALID_PASSWORD = "Str0ngPassw0rd!"


async def register_and_login(client, email="jane@example.com"):
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": VALID_PASSWORD, "full_name": "Jane Doe"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD}
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_get_profile_requires_auth(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_update_profile_full_name(client):
    headers = await register_and_login(client)
    resp = await client.patch(
        "/api/v1/users/me", json={"full_name": "Jane A. Doe"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Jane A. Doe"


async def test_update_profile_partial_update_ignores_omitted_fields(client):
    headers = await register_and_login(client)
    resp = await client.patch("/api/v1/users/me", json={}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Jane Doe"  # unchanged


async def test_preferences_get_defaults_to_empty(client):
    headers = await register_and_login(client)
    resp = await client.get("/api/v1/users/me/preferences", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["preferences"] == {}


async def test_preferences_update_merges_not_replaces(client):
    headers = await register_and_login(client)

    first = await client.put(
        "/api/v1/users/me/preferences", json={"theme": "dark"}, headers=headers
    )
    assert first.json()["preferences"] == {"theme": "dark"}

    second = await client.put(
        "/api/v1/users/me/preferences", json={"currency": "USD"}, headers=headers
    )
    # theme from the first call must still be present — merge, not replace
    assert second.json()["preferences"] == {"theme": "dark", "currency": "USD"}


async def test_preferences_rejects_invalid_theme(client):
    headers = await register_and_login(client)
    resp = await client.put(
        "/api/v1/users/me/preferences", json={"theme": "not-a-real-theme"}, headers=headers
    )
    assert resp.status_code == 422


async def test_avatar_upload_rejects_unsupported_content_type(client):
    headers = await register_and_login(client)
    fake_file = io.BytesIO(b"not actually an image")
    resp = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("shell.sh", fake_file, "application/x-sh")},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_avatar_upload_rejects_oversized_file(client, monkeypatch):
    # Shrink the limit so we don't need to construct a multi-megabyte
    # fixture file to exercise this path.
    monkeypatch.setattr("app.services.user_service.settings.AVATAR_MAX_SIZE_MB", 0.000001)
    headers = await register_and_login(client)
    fake_file = io.BytesIO(b"\xff\xd8\xff" + b"0" * 1000)  # fake-ish JPEG magic bytes + padding
    resp = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("avatar.jpg", fake_file, "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_avatar_upload_success(client):
    headers = await register_and_login(client)
    fake_file = io.BytesIO(b"\xff\xd8\xff" + b"0" * 100)
    resp = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("avatar.jpg", fake_file, "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["avatar_url"].startswith("/uploads/avatars/")

    # Confirm it persisted onto the profile
    me_resp = await client.get("/api/v1/users/me", headers=headers)
    assert me_resp.json()["avatar_url"] == resp.json()["avatar_url"]
