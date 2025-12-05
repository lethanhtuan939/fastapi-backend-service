from app.repositories.user_repository import UserRepository


def insert_test_user(db):
    users_data = [
        {"u_id": "testuser1", "u_username": "testuser1", "u_password": "password1"},
        {"u_id": "testuser2", "u_username": "testuser2", "u_password": "password2"},
        {"u_id": "testuser3", "u_username": "testuser3", "u_password": "password3"},
    ]

    user_repo = UserRepository()
    user_repo.bulk_create(db, users_data)
