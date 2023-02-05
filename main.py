from flask import Flask, jsonify, request
import db

app = Flask(__name__)

database = db.GameDatabase(".")


def json_error(error_code: int, error_message: str):
    return jsonify({
        "error_core": error_code,
        "error_message": error_message
    }), error_code


@app.route('/players/all', methods=['GET', "DELETE"])
def get_players():
    if request.method == "GET":
        players = database.get_players()
        players_dic_array = []
        for player in players:
            players_dic_array.append(player.to_dic())
        return jsonify(players_dic_array)
    else:
        if request.method == "DELETE":
            database.remove_all_players()
            return jsonify({"ok": 0}), 200


@app.route('/players/byId/<id>', methods=['GET', "DELETE"])
def get_player(id):
    if request.method == "GET":
        player = database.get_player(id)
        if player is not None:
            return jsonify(player.to_dic())
        else:
            return json_error(400, "The player id is not in the database")
    else:
        database.remove_player(id)
        return jsonify({"ok": 0}), 200


@app.route('/players/create', methods=['POST'])
def create_player():
    request_data: dict = request.get_json(force=True, silent=True)
    if request_data is None:
        return json_error(400, "Json is not encoded correctly")
    if "name" not in request_data or request_data["name"] is "":
        return json_error(400, "Data in the body need a column \"name\"")
    name = request_data["name"]
    if "score" in request_data:
        base_score = request_data["score"]
    else:
        base_score = None

    player_id = database.create_player(name)
    if player_id is not None and base_score is not None:
        database.set_score_to_player(player_id, base_score)

    if player_id is not None:

        return jsonify({"id": player_id}), 200
    else:
        return json_error(500, "Error when creating the player")


# TODO Need to be post after
@app.route('/players/update/score', methods=['POST'])
def set_score():
    request_data: dict = request.get_json(force=True, silent=True)
    if request_data is None:
        return json_error(400, "Json is not encoded correctly")

    if "id" not in request_data:
        return json_error(400, "Data in the body need a column \"id\"")
    player_id = request_data["id"]

    if "score" not in request_data:
        return json_error(400, "Data in the body need a column \"score\"")

    player_score = request_data["score"]

    if not database.player_exist(player_id):
        return json_error(400, "The player with the id :" + str(player_id) + "doesn't exist")

    is_ok = database.set_score_to_player(player_id, player_score)
    if not is_ok:
        return json_error(500, "can't set the score")
    else:
        return jsonify({"ok": 0}), 200

# Used only if there is a problem
@app.route('/hardreinit', methods=['GET'])
def reinit_database():
    database.clear_database()

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
