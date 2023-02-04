import os

from flask import Flask, render_template, jsonify, abort, request
from . import db


def json_error(error_code: int, error_message: str):
    return jsonify({
        "error_core": error_code,
        "error_message": error_message
    }), error_code


def create_app(test_config=None):
    # create and configure the app
    database = db.GameDatabase("./flaskr/")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello/<username>')
    def hello(username):
        return render_template("uwu.html", name=username)

    @app.route('/players/all', methods=['GET'])
    def get_players():
        players = database.get_players()
        players_dic_array = []
        for player in players:
            players_dic_array.append(player.to_dic())
        return jsonify(players_dic_array)

    @app.route('/players/byId/<id>', methods=['GET'])
    def get_player(id):
        player = database.get_player(id)
        if player is not None:
            return jsonify(player.to_dic())
        else:
            return

            # TODO Need to be post after

    @app.route('/players/create/', methods=['POST'])
    def create_player():
        request_data: dict = request.get_json(force=True, silent=True)
        if request_data is None:
            return json_error(400, "Json is not encoded correctly")
        if "name" not in request_data:
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
        return jsonify({"ok": is_ok}), 200

    return app
