"""
Tests for the /auth/* endpoints. Uses the `client` fixture (conftest.py),
which gives each test an isolated in-memory SQLite DB and a fake Redis.
pytest.ini sets asyncio_mode=auto, so no explicit markers are needed on
these async test functions.
"""

VALID_PASSWORD = "Str0ngPassw0rd!"


async def register_user(client, email="jane@example.com", password=VALID_PASSWORD):
    return await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Jane Doe"},
    )


async def test_register_success(client):
    resp = await register_user(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "jane@example.com"
    assert body["is_email_verified"] is False
    assert "hashed_password" not in body  # never leak the hash in a response


async def test_register_duplicate_email_returns_409(client):
    await register_user(client)
    resp = await register_user(client)
    assert resp.status_code == 409


async def test_register_weak_password_returns_422(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "alllowercase1", "full_name": "Weak Pw"},
    )
    assert resp.status_code == 422


async def test_login_success_sets_cookie_and_returns_access_token(client):
    await register_user(client)
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["user"]["email"] == "jane@example.com"
    assert "refresh_token" in resp.cookies


async def test_login_wrong_password_returns_401(client):
    await register_user(client)
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": "WrongPassword1"}
    )
    assert resp.status_code == 401


async def test_login_lockout_after_five_failed_attempts(client):
    await register_user(client)
    for _ in range(5):
        resp = await client.post(
            "/api/v1/auth/login", json={"email": "jane@example.com", "password": "WrongPassword1"}
        )
        assert resp.status_code == 401

    # Reset slowapi's IP rate limiter here so this assertion tests the
    # APPLICATION's account-lockout logic specifically, not slowapi's
    # separate (and here, coincidentally identical) 5/minute IP limit on
    # this same endpoint — the two are independent security layers and
    # should be verified independently.
    from app.middleware.rate_limit import limiter

    limiter.reset()

    # 6th attempt, even with the CORRECT password, should now be locked out
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    assert resp.status_code == 401
    assert "locked" in resp.json()["error"]["message"].lower()


async def test_refresh_rotates_token_and_old_token_is_rejected(client):
    await register_user(client)
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    old_refresh_cookie = login_resp.cookies["refresh_token"]

    # First refresh: should succeed and rotate to a new refresh token
    refresh_resp = await client.post(
        "/api/v1/auth/refresh", cookies={"refresh_token": old_refresh_cookie}
    )
    assert refresh_resp.status_code == 200
    new_refresh_cookie = refresh_resp.cookies["refresh_token"]
    assert new_refresh_cookie != old_refresh_cookie

    # Reusing the OLD refresh token should now be rejected (rotation)
    replay_resp = await client.post(
        "/api/v1/auth/refresh", cookies={"refresh_token": old_refresh_cookie}
    )
    assert replay_resp.status_code == 401


async def test_change_password_success_and_old_password_rejected(client):
    await register_user(client)
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    change_resp = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": VALID_PASSWORD, "new_password": "N3wStr0ngPass!"},
        headers=headers,
    )
    assert change_resp.status_code == 204

    old_login = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": "N3wStr0ngPass!"}
    )
    assert new_login.status_code == 200


async def test_change_password_wrong_current_returns_401(client):
    await register_user(client)
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "WrongCurrent1", "new_password": "N3wStr0ngPass!"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 401


async def test_forgot_password_returns_202_for_unknown_email(client):
    """Must not reveal whether the email is registered — same 202 either way."""
    resp = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
    )
    assert resp.status_code == 202


async def test_forgot_and_reset_password_flow(client, monkeypatch):
    await register_user(client)

    captured = {}

    async def capture_reset_email(self, to_email, reset_url):
        captured["url"] = reset_url

    monkeypatch.setattr(
        "app.core.email.ConsoleEmailService.send_password_reset", capture_reset_email
    )

    forgot_resp = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "jane@example.com"}
    )
    assert forgot_resp.status_code == 202
    assert "url" in captured

    token = captured["url"].split("token=")[-1]
    reset_resp = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "Br4ndNewPass!"}
    )
    assert reset_resp.status_code == 204

    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": "Br4ndNewPass!"}
    )
    assert login_resp.status_code == 200


async def test_email_verification_flow(client, monkeypatch):
    await register_user(client)
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "jane@example.com", "password": VALID_PASSWORD}
    )
    access_token = login_resp.json()["access_token"]
    assert login_resp.json()["user"]["is_email_verified"] is False

    captured = {}

    async def capture_verification_email(self, to_email, verification_url):
        captured["url"] = verification_url

    monkeypatch.setattr(
        "app.core.email.ConsoleEmailService.send_email_verification",
        capture_verification_email,
    )

    resend_resp = await client.post(
        "/api/v1/auth/resend-verification",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resend_resp.status_code == 202
    assert "url" in captured

    token = captured["url"].split("token=")[-1]
    verify_resp = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verify_resp.status_code == 204

    me_resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.json()["is_email_verified"] is True


async def test_me_requires_authentication(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
