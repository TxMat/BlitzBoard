import json

CONFIG = {
    "template": {
        "score": {
            "weight": 0.8,
            "type": "int"
        },
        "text_lol": {
            "weight": 0,
            "type": "str"
        },
        "nb_ennemis": {
            "weight": 0.2,
            "type": "int"
        }
    },
    "keep_lower_scores": False,
    "allow_ties": True
}

CONFIG_KEEP_LOWER_AND_DONT_ALLOW_TIES = {
    "template": {
        "score": {
            "weight": 0.8,
            "type": "int"
        },
        "text_lol": {
            "weight": 0,
            "type": "str"
        },
        "nb_ennemis": {
            "weight": 0.2,
            "type": "int"
        }
    },
    "keep_lower_scores": True,
    "allow_ties": False
}

SCORE = {"score": 120, "text_lol": "coucou", "nb_ennemis": 20}

BETTER_SCORE = {"score": 130, "text_lol": "TEST", "nb_ennemis": 20}

WORSE_SCORE = {"score": 120, "text_lol": "AAAA", "nb_ennemis": 10}

INVALID_SCORE = {"score": "", "text_lol": "coucou", "nb_ennemis": 20}


def create_score(client, g_id, p_id, score, rc=201):
    response = client.post('/games/' + g_id + '/scores/' + p_id, data={
        "score": json.dumps(score)
    })
    assert response.status_code == rc


def check_score(client, g_id, p_id, score,  rank=1):
    response = client.get('/games/' + g_id + '/scores/' + p_id)
    print(response.json)
    assert response.status_code == 200
    assert response.json['name'] == client.get('/players/' + p_id).json['name']
    assert response.json['score'] == score
    assert response.json['rank'] == rank


def create_player(client, name, rc=201):
    response = client.post('/players', data={
        "name": name,
    })
    assert response.status_code == rc
    return response


def check_player(client, p_id, name):
    response = client.get('/players/' + p_id)
    assert response.status_code == 200
    assert response.json['id'] == p_id
    assert response.json['name'] == name


def patch_player(client, p_id, name):
    response = client.patch('/players/' + p_id, data={
        "name": name,
    })
    return response.status_code


def create_game(client, name, rc=201):
    config = CONFIG
    response = client.post('/games', data={
        "name": name,
        "config": json.dumps(config)
    })
    assert response.status_code == rc


def patch_game(client, name, rc=200):
    config = CONFIG_KEEP_LOWER_AND_DONT_ALLOW_TIES
    response = client.patch('/games/' + name, data={
        "name": name,
        "config": json.dumps(config)
    })
    assert response.status_code == rc


class TestPlayer:

    def test_invalid_player_name(self, client):
        create_player(client, "", 400)

    def test_empty_body(self, client):
        response = client.post('/players', data={
        })
        assert response.status_code == 400

    def test_create_player(self, client):
        response = create_player(client, "hugo")

    def test_create_player_with_existing_name(self, client):
        response = create_player(client, "hugo")
        id = response.json['id']
        # allow duplicate names
        response = create_player(client, "hugo")
        assert response.json['id'] != id

    def test_get_player(self, client):
        response = create_player(client, "hugo")
        check_player(client, response.json['id'], "hugo")

    def test_get_player_with_invalid_id(self, client):
        response = client.get('/players/1')
        assert response.status_code == 404

    def test_get_player_with_invalid_id_type(self, client):
        response = client.get('/players/hugo')
        assert response.status_code == 404

    def test_delete_player(self, client):
        response = create_player(client, "hugo")
        p_id = str(response.json['id'])
        response = client.delete('/players/' + p_id)
        assert response.status_code == 204
        response = client.get('/players/' + p_id)
        assert response.status_code == 404

    def test_delete_player_with_invalid_id(self, client):
        response = client.delete('/players/1000')
        assert response.status_code == 404

    def test_delete_player_with_invalid_id_type(self, client):
        response = client.delete('/players/hugo')
        assert response.status_code == 404

    def test_update_player(self, client):
        response = create_player(client, "hugo")
        p_id = str(response.json['id'])
        assert response.status_code == 201
        assert patch_player(client, p_id, "hugo2") == 200

        check_player(client, p_id, "hugo2")

    def test_update_player_with_invalid_id(self, client):
        assert patch_player(client, "1", "hugo2") == 404

    def test_update_player_with_invalid_id_type(self, client):
        assert patch_player(client, "hugo", "hugo2") == 404

    def test_update_player_with_invalid_name(self, client):
        response = create_player(client, "hugo")
        p_id = str(response.json['id'])
        assert patch_player(client, p_id, "") == 400

    def test_update_player_with_same_name(self, client):
        response = create_player(client, "hugo")
        p_id = str(response.json['id'])
        assert patch_player(client, p_id, "hugo") == 200

    def test_get_all_players(self, client):
        response = create_player(client, "hugo")
        p_id1 = str(response.json['id'])
        response = create_player(client, "hugo2")
        assert response.status_code == 201
        p_id2 = str(response.json['id'])

        response = client.get('/players')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id'] == p_id1
        assert response.json[0]['name'] == "hugo"
        assert response.json[1]['id'] == p_id2
        assert response.json[1]['name'] == "hugo2"

    def test_get_all_players_with_empty_db(self, client):
        response = client.get('/players')
        assert response.status_code == 200
        assert len(response.json) == 0


class TestGame:
    def test_create_game(self, client):
        create_game(client, "Game 1")

    def test_create_game_with_existing_name(self, client):
        create_game(client, "Game 1")
        create_game(client, "Game 1", 409)

    def test_create_game_with_invalid_name(self, client):
        create_game(client, "", 400)

    def test_create_game_with_empty_config(self, client):
        response = client.post('/games', data={
            "name": "Game 1",
            "config": "",
        })
        assert response.status_code == 400

    def test_create_game_with_invalid_config(self, client):
        response = client.post('/games', data={
            "name": "Game 1",
            "config": "invalid",
        })
        assert response.status_code == 400

    def test_get_game(self, client):
        create_game(client, "Game 1")

        response = client.get('/games/Game 1')
        assert response.status_code == 200
        assert response.json['name'] == "Game 1"

        assert response.json['config']['template'] == CONFIG['template']
        assert response.json['config']['keep_lower_scores'] == CONFIG['keep_lower_scores']
        assert response.json['config']['allow_ties'] == CONFIG['allow_ties']

    def test_get_game_with_invalid_id(self, client):
        response = client.get('/games/1')
        assert response.status_code == 404

    def test_delete_game(self, client):
        create_game(client, "Game 1")
        response = client.delete('/games/Game 1')
        assert response.status_code == 204
        response = client.get('/games/Game 1')
        assert response.status_code == 404

    def test_delete_game_with_invalid_id(self, client):
        response = client.delete('/games/1')
        assert response.status_code == 404

    def test_update_game(self, client):
        create_game(client, "Game 1")
        patch_game(client, "Game 1")

        response = client.get('/games/Game 1')
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == "Game 1"

        assert response.json['config']['template'] == CONFIG_KEEP_LOWER_AND_DONT_ALLOW_TIES['template']
        assert response.json['config']['keep_lower_scores'] == CONFIG_KEEP_LOWER_AND_DONT_ALLOW_TIES[
            'keep_lower_scores']
        assert response.json['config']['allow_ties'] == CONFIG_KEEP_LOWER_AND_DONT_ALLOW_TIES['allow_ties']

    def test_update_game_with_invalid_id(self, client):
        patch_game(client, "Game 1", 404)

    def test_update_game_with_invalid_config(self, client):
        create_game(client, "Game 1")
        response = client.patch('/games/Game 1', data={
            "config": "invalid",
        })
        assert response.status_code == 400

    def test_get_all_games(self, client):
        create_game(client, "Game 1")
        create_game(client, "Game 2")

        response = client.get('/games')
        assert response.status_code == 200
        assert len(response.json) == 2

    def test_get_all_games_with_no_game(self, client):
        response = client.get('/games')
        assert response.status_code == 200
        assert len(response.json) == 0


class TestScore:

    def test_post_score(self, client):
        p_id = create_player(client, "Player 1").json['id']

        create_game(client, "Game 1")

        # create score
        create_score(client, "Game 1", p_id, SCORE)
        check_score(client, "Game 1", p_id, SCORE)

    def test_post_score_with_invalid_game_id(self, client):
        p_id = create_player(client, "Player 1").json['id']

        create_score(client, "Game 1", p_id, SCORE, 404)

    def test_post_score_with_invalid_player_id(self, client):
        create_game(client, "Game 1")

        create_score(client, "Game 1", "1", SCORE, 404)

    def test_post_score_with_invalid_score(self, client):
        p_id = create_player(client, "Player 1").json['id']

        create_game(client, "Game 1")

        create_score(client, "Game 1", p_id, "invalid", 400)
        create_score(client, "Game 1", p_id, INVALID_SCORE, 400)

    def test_get_score(self, client):
        p_id = create_player(client, "Player 1").json['id']

        create_game(client, "Game 1")

        # create score
        create_score(client, "Game 1", p_id, SCORE)
        check_score(client, "Game 1", p_id, SCORE)

    def test_get_score_with_invalid_game_id(self, client):
        response = client.get('/games/1/scores/1')
        assert response.status_code == 404

    def test_get_all_scores(self, client):
        p_id = create_player(client, "Player 1").json['id']
        p_id2 = create_player(client, "Player 2").json['id']

        create_game(client, "Game 1")

        # create score
        create_score(client, "Game 1", p_id, SCORE)
        check_score(client, "Game 1", p_id, SCORE)

        create_score(client, "Game 1", p_id2, WORSE_SCORE)
        check_score(client, "Game 1", p_id2, WORSE_SCORE, 2)

        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 2

    def test_get_all_scores_with_invalid_game_id(self, client):
        response = client.get('/games/1/scores')
        assert response.status_code == 404

    def test_get_all_scores_with_no_score(self, client):
        create_game(client, "Game 1")
        response = client.get('/games/1/scores')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_all_scores_with_no_player(self, client):
        create_game(client, "Game 1")

        create_score(client, "Game 1", "1", SCORE, 404)

    def test_get_all_scores_with_no_game(self, client):
        p_id = create_player(client, "Player 1").json['id']

        create_score(client, "Game 1", p_id, SCORE, 404)

    def test_get_all_scores_with_no_player_and_no_game(self, client):
        create_score(client, "Game 1", "1", SCORE, 404)

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
        client.post('/games', data={
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
        client.post('/games', data={
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
