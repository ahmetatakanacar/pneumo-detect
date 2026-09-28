def test_register_creates_user_with_default_role(register_user):
    response, creds = register_user()
    assert response.status_code == 201, response.text

    body = response.json()
    assert body["email"] == creds["email"]
    assert body["role"] == "readonly"
    assert "id" in body

def test_register_duplicate_email_fails(test_client, register_user):
    _, creds = register_user()

    response = test_client.post(
        "/auth/register",
        json={
            "email": creds["email"],
            "password": "AnotherPassword123!",
            "role": "readonly",
        },
    )
    assert response.status_code == 400

def test_login_with_correct_credentials_returns_token(test_client, register_user):
    _, creds = register_user()

    response = test_client.post(
        "/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_with_wrong_password_fails(test_client, register_user):
    _, creds = register_user()

    response = test_client.post(
        "/auth/login",
        json={"email": creds["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == 401

def test_me_without_token_is_rejected(test_client):
    response = test_client.get("/auth/me")
    assert response.status_code == 401

def test_me_returns_current_user(test_client, auth_headers):
    headers = auth_headers()

    response = test_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()