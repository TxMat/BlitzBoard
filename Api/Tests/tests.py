import json


class Test:

    def test_invalid_player_name(self, client, db):
        response = client.post('/players', data={
            "id": "1",
            "name": "",
        })
        assert response.status_code == 400

    def test_empty_body(self, client, db):
        response = client.post('/players', data={
        })
        assert response.status_code == 400

    def test_create_player(self, client, db):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
