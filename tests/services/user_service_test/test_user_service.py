from app.services.user_service import get_user, get_users
from tests.services.user_service_test.test_data_user_service import insert_test_user


def test_get_user_not_found(db_session):
    insert_test_user(db_session)

    user = get_user(db_session, "nonexistentuser")
    assert user is None


def test_get_user_found(db_session):
    insert_test_user(db_session)

    user = get_user(db_session, "testuser1")
    assert user is not None
    assert user.u_id == "testuser1"
    assert user.u_username == "testuser1"


def test_get_users(db_session):
    insert_test_user(db_session)

    users = get_users(db_session, offset=0, limit=10)
    assert len(users) == 3
    usernames = [user.u_username for user in users]
    assert "testuser1" in usernames
    assert "testuser2" in usernames
    assert "testuser3" in usernames
