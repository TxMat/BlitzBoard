import json


class Test:

    def test_invalid_player_name(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "",
        })
        assert response.status_code == 400

    def test_empty_body(self, client):
        response = client.post('/players', data={
        })
        assert response.status_code == 400

    def test_create_player(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201

    def test_create_player_with_existing_id(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 409

    def test_create_player_with_existing_name(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.post('/players', data={
            "id": "2",
            "name": "hugo",
        })
        assert response.status_code == 201

    def test_get_player(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.get('/players/1')
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == "hugo"

    def test_get_player_with_invalid_id(self, client):
        response = client.get('/players/1')
        assert response.status_code == 404

    def test_get_player_with_invalid_id_type(self, client):
        response = client.get('/players/hugo')
        assert response.status_code == 404

    def test_delete_player(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.delete('/players/1')
        assert response.status_code == 204
        response = client.get('/players/1')
        assert response.status_code == 404

    def test_delete_player_with_invalid_id(self, client):
        response = client.delete('/players/1000')
        assert response.status_code == 404

    def test_delete_player_with_invalid_id_type(self, client):
        response = client.delete('/players/hugo')
        assert response.status_code == 404

    def test_update_player(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.patch('/players/1', data={
            "name": "hugo2",
        })
        assert response.status_code == 200
        response = client.get('/players/1')
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == "hugo2"

    def test_update_player_with_invalid_id(self, client):
        response = client.patch('/players/1', data={
            "name": "hugo2",
        })
        assert response.status_code == 404

    def test_update_player_with_invalid_id_type(self, client):
        response = client.patch('/players/hugo', data={
            "name": "hugo2",
        })
        assert response.status_code == 404

    def test_update_player_with_invalid_name(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.patch('/players/1', data={
            "name": "",
        })
        assert response.status_code == 400

    def test_update_player_with_same_name(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.patch('/players/1', data={
            "name": "hugo",
        })
        assert response.status_code == 200

    def test_get_all_players(self, client):
        response = client.post('/players', data={
            "id": "1",
            "name": "hugo",
        })
        assert response.status_code == 201
        response = client.post('/players', data={
            "id": "2",
            "name": "hugo2",
        })
        assert response.status_code == 201
        response = client.get('/players')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id'] == 1
        assert response.json[0]['name'] == "hugo"
        assert response.json[1]['id'] == 2
        assert response.json[1]['name'] == "hugo2"

    def test_get_all_players_with_empty_db(self, client):
        response = client.get('/players')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_create_game(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

    def test_create_game_with_existing_id(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 409

    def test_create_game_with_invalid_id(self, client):
        response = client.post('/games', data={
            "id": "",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 400

    def test_create_game_with_invalid_name(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 400

    def test_create_game_with_empty_config(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "",
        })
        assert response.status_code == 400

    def test_create_game_with_invalid_config(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "invalid",
        })

    def test_get_game(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.get('/games/1')
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == "Game 1"
        assert json.loads(response.json['config']) == json.loads("{"
                                                                 "\"intscore\" : 0,"
                                                                 "\"ennemykilled\" : 0"
                                                                 "}")

    def test_get_game_with_invalid_id(self, client):
        response = client.get('/games/1')
        assert response.status_code == 404

    def test_get_game_with_invalid_id_type(self, client):
        response = client.get('/games/hugo')
        assert response.status_code == 404

    def test_delete_game(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.delete('/games/1')
        assert response.status_code == 204
        response = client.get('/games/1')
        assert response.status_code == 404

    def test_delete_game_with_invalid_id(self, client):
        response = client.delete('/games/1')
        assert response.status_code == 404

    def test_delete_game_with_invalid_id_type(self, client):
        response = client.delete('/games/hugo')
        assert response.status_code == 404

    def test_update_game(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.patch('/games/1', data={
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 200
        response = client.get('/games/1')
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == "Game 1"
        assert json.loads(response.json['config']) == json.loads("{"
                                                                 "\"intscore\" : 0,"
                                                                 "\"ennemykilled\" : 0"
                                                                 "}")

    def test_update_game_with_invalid_id(self, client):
        response = client.patch('/games/1', data={
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 404

    def test_update_game_with_invalid_id_type(self, client):
        response = client.patch('/games/hugo', data={
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 404

    def test_update_game_with_invalid_name(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.patch('/games/1', data={
            "name": "",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 400

    def test_update_game_with_invalid_config(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.patch('/games/1', data={
            "name": "Game 1",
            "config": "",
        })
        assert response.status_code == 400

    def test_get_all_games(self, client):
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.post('/games', data={
            "id": "2",
            "name": "Game 2",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.get('/games')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id'] == 1
        assert response.json[0]['name'] == "Game 1"
        assert json.loads(response.json[0]['config']) == json.loads("{"
                                                                    "\"intscore\" : 0,"
                                                                    "\"ennemykilled\" : 0"
                                                                    "}")
        assert response.json[1]['id'] == 2
        assert response.json[1]['name'] == "Game 2"
        assert json.loads(response.json[1]['config']) == json.loads("{"
                                                                    "\"intscore\" : 0,"
                                                                    "\"ennemykilled\" : 0"
                                                                    "}")

    def test_get_all_games_with_no_game(self, client):
        response = client.get('/games')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_post_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201
        response = client.get('/games/1/scores/1')
        assert response.status_code == 200
        assert response.json == json.loads("{"
                                           "\"intscore\" : 100,"
                                           "\"ennemykilled\" : 0"
                                           "}")

    def test_post_score_with_invalid_game_id(self, client):
        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_post_score_with_invalid_player_id(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_post_score_with_invalid_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "invalid score",
        })
        assert response.status_code == 400

    def test_get_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201
        response = client.get('/games/1/scores/1')
        assert response.status_code == 200
        assert response.json == json.loads("{"
                                           "\"intscore\" : 100,"
                                           "\"ennemykilled\" : 0"
                                           "}")

    def test_get_score_with_invalid_game_id(self, client):
        response = client.get('/games/1/scores/1')
        assert response.status_code == 404

    def test_get_score_with_invalid_score_id(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.get('/games/1/scores/1')
        assert response.status_code == 404

    def test_get_all_scores(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player 1
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create player 2
        response = client.post('/players', data={
            "id": "2",
            "name": "Player 2"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/2', data={
            "score": "{"
                     "\"intscore\" : 200,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['name'] == "Player 1"
        assert response.json[0]['score'] == json.loads("{"
                                                       "\"intscore\" : 100,"
                                                       "\"ennemykilled\" : 0"
                                                       "}")
        assert response.json[1]['name'] == "Player 2"
        assert response.json[1]['score'] == json.loads("{"
                                                       "\"intscore\" : 200,"
                                                       "\"ennemykilled\" : 0"
                                                       "}")

    def test_get_all_scores_with_invalid_game_id(self, client):
        response = client.get('/games/1/scores')
        assert response.status_code == 404

    def test_get_all_scores_with_no_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201
        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_all_scores_with_no_player(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_get_all_scores_with_no_game(self, client):
        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_get_all_scores_with_no_player_and_no_game(self, client):
        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_get_all_scores_with_invalid_player_id(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 404

    def test_get_all_scores_with_invalid_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : invalid,json,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 400

    def test_delete_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.delete('/games/1/scores/1')
        assert response.status_code == 204

        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_delete_score_with_invalid_score_id(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        response = client.delete('/games/1/scores/1')
        assert response.status_code == 404

    def test_delete_score_with_invalid_game_and_score_id(self, client):
        response = client.delete('/games/1/scores/1')
        assert response.status_code == 404

    def test_update_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 200,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 200

        response = client.get('/games/1/scores/1')
        assert response.status_code == 200
        assert response.json == json.loads("{"
                                           "\"intscore\" : 200,"
                                           "\"ennemykilled\" : 0"
                                           "}")

    def test_update_score_with_worse_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 50,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 200

        response = client.get('/games/1/scores/1')
        assert response.status_code == 200
        assert response.json == json.loads("{"
                                           "\"intscore\" : 100,"
                                           "\"ennemykilled\" : 0"
                                           "}")

    def test_get_all_player_scores(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create game
        response = client.post('/games', data={
            "id": "2",
            "name": "Game 2",
            "config": "{"
                      "\"game2score\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/2/scores/1', data={
            "score": "{"
                     "\"game2score\" : 200,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.get('/players/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0] == json.loads("{"
                                                "\"intscore\" : 100,"
                                                "\"ennemykilled\" : 0"
                                                "}")
        assert response.json[1] == json.loads("{"
                                                "\"game2score\" : 200,"
                                                "\"ennemykilled\" : 0"
                                                "}")

    def test_delete_all_player_scores(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create game
        response = client.post('/games', data={
            "id": "2",
            "name": "Game 2",
            "config": "{"
                      "\"game2score\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/2/scores/1', data={
            "score": "{"
                     "\"game2score\" : 200,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        response = client.delete('/players/1/scores')
        assert response.status_code == 204

        response = client.get('/players/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_delete_all_game_score(self, client):
        # create game
        response = client.post('/games', data={
            "id": "1",
            "name": "Game 1",
            "config": "{"
                      "\"intscore\" : 0,"
                      "\"ennemykilled\" : 0"
                      "}",
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "1",
            "name": "Player 1"
        })
        assert response.status_code == 201

        # create player
        response = client.post('/players', data={
            "id": "2",
            "name": "Player 2"
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/1', data={
            "score": "{"
                     "\"intscore\" : 100,"
                     "\"ennemykilled\" : 0"
                     "}",
        })
        assert response.status_code == 201

        # create score
        response = client.post('/games/1/scores/2', data={
            "score": "{"
                        "\"intscore\" : 200,"
                        "\"ennemykilled\" : 0"
                        "}",
        })
        assert response.status_code == 201

        response = client.delete('/games/1/scores')
        assert response.status_code == 204

        response = client.get('/games/1/scores/1')
        assert response.status_code == 404

        response = client.get('/games/1/scores/2')
        assert response.status_code == 404

        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 0




