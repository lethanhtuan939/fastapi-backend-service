import pytest
import jwt
from datetime import timedelta, datetime, timezone
import uuid
from app.models.user import User
from app.models.token import Token
from app.core.security import hash_password
from app.core.config import settings
from app.core.enum import TokenType


def create_user(db, username, password, uid):
    hashed = hash_password(password)
    user = User(u_id=uid, u_username=username, u_password=hashed)
    db.add(user)
    db.commit()
    return user


def create_dummy_token(db, user_id, token_str, token_type):
    token = Token(
        user_id=user_id,
        token=token_str,
        token_type=token_type,
        expired=False,
        revoked=False,
    )
    db.add(token)
    db.commit()
    return token


def test_login(client, db_session):
    create_user(db_session, "testuser", "testpassword", "1")
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    assert isinstance(data["expires_in"], int)
    assert data["token_type"] == "bearer"

    # Verify token in DB
    token = db_session.query(Token).filter(Token.token == data["access_token"]).first()
    assert token is not None
    assert token.user_id == "1"
    assert token.token_type == "ACCESS"
    assert token.revoked == False


def test_login_limit(client, db_session):
    create_user(db_session, "limituser", "testpassword", "5")

    # 1st Login
    res1 = client.post(
        "/auth/login", data={"username": "limituser", "password": "testpassword"}
    )
    assert res1.status_code == 200
    rt1 = res1.json()["refresh_token"]

    # 2nd Login
    res2 = client.post(
        "/auth/login", data={"username": "limituser", "password": "testpassword"}
    )
    assert res2.status_code == 200
    rt2 = res2.json()["refresh_token"]

    # 3rd Login - Should revoke 1st session (Refresh Token)
    res3 = client.post(
        "/auth/login", data={"username": "limituser", "password": "testpassword"}
    )
    assert res3.status_code == 200

    t1 = db_session.query(Token).filter(Token.token == rt1).first()
    assert t1 is None  # Should be deleted

    t2 = db_session.query(Token).filter(Token.token == rt2).first()
    # t2 might be deleted or valid?
    # Logic:
    # 1st login -> RT1
    # 2nd login -> RT2 (limit 2, count=2)
    # 3rd login -> RT3. Count=3. Delete oldest (RT1).
    # But wait, logic is: get active refresh tokens (RT1, RT2). len=2.
    # delete oldest (RT1).
    # add RT3.
    # So RT2 should be remaining.
    assert t2 is not None and t2.revoked == False


def test_login_fail(client):
    response = client.post(
        "/auth/login", data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401


def test_refresh(client, db_session):
    create_user(db_session, "refreshuser", "testpassword", "2")
    login_res = client.post(
        "/auth/login", data={"username": "refreshuser", "password": "testpassword"}
    )
    refresh_token = login_res.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Old refresh token should be deleted
    old_rt = db_session.query(Token).filter(Token.token == refresh_token).first()
    assert old_rt is None


def test_refresh_invalid_token(client, db_session):
    create_user(db_session, "refreshuser_inv", "testpassword", "20")
    login_res = client.post(
        "/auth/login", data={"username": "refreshuser_inv", "password": "testpassword"}
    )
    refresh_token = login_res.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401


def test_logout(client, db_session):
    create_user(db_session, "logoutuser", "testpassword", "3")
    login_res = client.post(
        "/auth/login", data={"username": "logoutuser", "password": "testpassword"}
    )
    access_token = login_res.json()["access_token"]

    response = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    db_token = db_session.query(Token).filter(Token.token == access_token).first()
    assert db_token is None


def test_access_with_revoked_token(client, db_session):
    create_user(db_session, "revokeduser", "testpassword", "4")
    login_res = client.post(
        "/auth/login", data={"username": "revokeduser", "password": "testpassword"}
    )
    access_token = login_res.json()["access_token"]

    # Logout to revoke
    client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

    # Try to access logout again (it requires auth)
    response = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401


def test_refresh_token_not_found(client):
    # Case 1: Token not in DB
    response = client.post(
        "/auth/refresh", json={"refresh_token": "non_existent_token"}
    )
    assert response.status_code == 401


def test_refresh_token_invalid_jwt_format(client, db_session):
    # Case 2: Token in DB but invalid JWT format
    create_user(db_session, "invalidjwt", "testpassword", "10")
    bad_token_str = "bad.jwt.token"
    # Create dummy token manually
    create_dummy_token(db_session, "10", bad_token_str, TokenType.REFRESH)

    response = client.post("/auth/refresh", json={"refresh_token": bad_token_str})
    # This should raise InvalidTokenError caught and re-raised as 401
    assert response.status_code == 401


def test_refresh_token_missing_sub(client, db_session):
    # Case 3: Token in DB, valid JWT signature, but missing 'sub'
    create_user(db_session, "nosubuser", "testpassword", "11")

    # Manually create JWT without sub
    data = {"type": "refresh", "jti": str(uuid.uuid4())}
    bad_token_str = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    create_dummy_token(db_session, "11", bad_token_str, TokenType.REFRESH)

    response = client.post("/auth/refresh", json={"refresh_token": bad_token_str})
    assert response.status_code == 401


def test_refresh_token_user_not_found(client, db_session):
    # Case 4: Token in DB, valid JWT, but User deleted
    user = create_user(db_session, "deleteduser", "testpassword", "12")

    # Create valid refresh token logic
    data = {"sub": "deleteduser", "type": "refresh", "jti": str(uuid.uuid4())}
    token_str = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    create_dummy_token(db_session, "12", token_str, TokenType.REFRESH)

    # Delete user
    db_session.delete(user)
    db_session.commit()

    response = client.post("/auth/refresh", json={"refresh_token": token_str})
    assert response.status_code == 401
