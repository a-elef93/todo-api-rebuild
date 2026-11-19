
from unittest.mock import MagicMock, patch

from app import app


def test_create_todo():
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = (1,)

    fake_connection = MagicMock()
    fake_connection.cursor.return_value.__enter__.return_value = fake_cursor

    with patch("app.get_db_connection", return_value=fake_connection):
        client = app.test_client()

        response = client.post(
            "/todos",
            json={"title": "Learn pytest"}
        )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "title": "Learn pytest",
        "completed": False
    }

    fake_connection.commit.assert_called_once()
    fake_connection.close.assert_called_once()
