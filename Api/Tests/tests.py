import json


class Test:
    def test_create_player_and_lobby(self, client):
        response = client.post('/join', data={
            "lobby_name": "Test Lobby 1",
            "player_name": "Test Player 1",
            "player_id": "player-1"
        })
        assert response.status_code == 404

