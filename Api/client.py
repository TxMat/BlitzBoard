import json

import peewee
from flask import Flask, jsonify
from flask_restx import Api, Resource, reqparse, fields
from playhouse.sqlite_ext import JSONField

app = Flask(__name__)

api = Api(
    app=app,
    title='BlitzBoard API',
    description="Robust and Reliable api to store player high scores",
    version="0.0.1"
)


class Database:
    def __init__(self):
        self.db = peewee.SqliteDatabase('blitzboard.db')
        self.db.connect()

    def create_db(self):
        self.db.create_tables([Config, Game, Player, PlayerGame, Score])

    def delete_db(self):
        self.db.drop_tables([Config, Game, Player, PlayerGame, Score])

    def close(self):
        self.db.close()


Database = Database()
db = Database.db


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Config(BaseModel):
    template = JSONField()
    keep_lower_scores = peewee.BooleanField(default=False)


class Game(BaseModel):
    id = peewee.IntegerField(primary_key=True, unique=True)
    name = peewee.CharField()
    config = peewee.ForeignKeyField(Config, backref='games')

    def to_dic(self):
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config.template
        }

    def to_dic_without_config(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Player(BaseModel):
    id = peewee.IntegerField(primary_key=True, unique=True)
    name = peewee.CharField()

    def to_dic(self):
        return {
            "id": self.id,
            "name": self.name
        }


class PlayerGame(BaseModel):
    player = peewee.ForeignKeyField(Player)
    game = peewee.ForeignKeyField(Game)


class Score(BaseModel):
    player = peewee.ForeignKeyField(Player, backref='scores')
    game = peewee.ForeignKeyField(Game, backref='scores')
    json_score = JSONField()
    hidden_score = peewee.IntegerField()


Database.create_db()


@api.route('/players', methods=['GET', 'POST'])
class Players(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=str, location='form', required=True)
    parser.add_argument('name', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'id': 'UUID of the player',
        'name': 'Name of the player',
    })
    @api.response(201, 'Player created')
    @api.response(409, 'Player already exists')
    @api.response(400, 'Invalid request')
    def post(self):
        data = self.parser.parse_args()

        player_id = data["id"]
        name = data["name"]

        if not (name and player_id):
            return "Invalid request", 400

        # check if player already exists if not create it
        try:
            Player.create(id=player_id, name=name)
        except peewee.IntegrityError:
            return "Player already exists", 409

        return "Player created", 201

    def get(self):
        players = Player.select()
        players_dic_array = []
        for player in players:
            players_dic_array.append(player.to_dic())
        return jsonify(players_dic_array)


@api.route('/players/<string:player_id>/scores', methods=['GET', 'DELETE'])
class PlayerScores(Resource):

    @api.response(200, 'Player scores fetched', fields.String(example={
        "template_key_1": "template_value_1",
        "template_key_2": "template_value_2",
    }))
    @api.response(404, 'Player does not exist')
    def get(self, player_id):
        try:
            player = Player.get(Player.id == player_id)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        scores = Score.select().where(Score.player == player)
        scores_dic_array = []
        for score in scores:
            current_score = score.game.to_dic_without_config()
            current_score["data"] = score.json_score
            scores_dic_array.append(current_score)

        return jsonify(scores_dic_array)

    @api.response(200, 'Player scores deleted')
    @api.response(404, 'Player does not exist')
    def delete(self, player_id):
        try:
            Score.delete().where(Score.player == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 404

        return "Player scores deleted", 204


@api.route('/players/<string:player_id>', methods=['GET', 'DELETE', 'PATCH'])
class PlayerId(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, location='form', required=True)

    @api.response(200, 'Player fetched')
    @api.response(404, 'Player does not exist')
    def get(self, player_id):
        try:
            player = Player.get(Player.id == player_id)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        return jsonify(player.to_dic())

    @api.expect(parser)
    @api.response(200, 'Player deleted')
    @api.response(404, 'Player does not exist')
    def delete(self, player_id):
        # check if player exists
        try:
            player = Player.get(Player.id == player_id)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        # delete player
        player.delete_instance()

        return "Player deleted", 204

    @api.expect(parser)
    @api.response(200, 'Player updated')
    @api.response(404, 'Player does not exist')
    @api.response(400, 'Invalid request')
    def patch(self, player_id):
        data = self.parser.parse_args()
        name = data["name"]
        if not (name and player_id):
            return "Invalid request", 400

        # check if player exists
        try:
            player = Player.get(Player.id == player_id)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        # update player
        player.name = name
        player.save()

        return "Player updated", 200


@api.route('/games', methods=['GET', 'POST'])
class Games(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=str, location='form', required=True)
    parser.add_argument('name', type=str, location='form', required=True)
    parser.add_argument('config', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'id': 'UUID of the game',
        'name': 'Name of the game',
        'config': 'json formatted config for the game',
    })
    @api.response(201, 'Game created')
    @api.response(409, 'Game already exists')
    @api.response(400, 'Invalid request')
    def post(self):
        data = self.parser.parse_args()

        game_id = data["id"]
        name = data["name"]
        config = data["config"]

        if not (name and config and game_id):
            return "Invalid request", 400

        # check if config is valid json
        try:
            config = json.loads(config)
        except ValueError:
            return "Invalid config, not valid json", 400

        if "template" not in config:
            return "Invalid config, no template", 400

        # check if name and weight are in template
        for key in config["template"]:
            if "weight" not in config["template"][key]:
                return "Invalid config, name or weight not in template item", 400

        keep_lower_score = config["keep_lower_score"] if "keep_lower_score" in config else False

        # check if template is valid
        # sum all weights and check if they are 1
        sum_weights = 0
        for key in config["template"]:
            sum_weights += config["template"][key]["weight"]

        if sum_weights != 1:
            return "Invalid config, sum of weights is not 1", 400

        # check if game already exists if not create it
        try:
            config = Config.create(template=config, keep_lower_score=keep_lower_score)
            Game.create(id=game_id, name=name, config=config)
        except peewee.IntegrityError:
            return "Game already exists", 409

        return "Game created", 201

    @api.response(200, 'Games fetched')
    def get(self):
        games = Game.select()
        games_dic_array = []
        for game in games:
            games_dic_array.append({
                "id": game.id,
                "name": game.name,
                "config": game.config.template
            })
        return games_dic_array


@api.route('/games/<string:gameid>', methods=['GET', 'DELETE', 'PATCH'])
class GameId(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, location='form', required=True)
    parser.add_argument('config', type=str, location='form', required=True)

    @api.response(200, 'Game fetched')
    @api.response(404, 'Game does not exist')
    def get(self, gameid):
        try:
            game = Game.get(Game.id == gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        return jsonify(game.to_dic())

    @api.response(200, 'Game deleted')
    @api.response(404, 'Game does not exist')
    def delete(self, gameid):

        # check if game exists
        try:
            game = Game.get(Game.id == gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # delete game
        game.delete_instance()

        return "Game deleted", 204

    @api.expect(parser)
    @api.response(200, 'Game updated')
    @api.response(400, 'Invalid request')
    @api.response(404, 'Game does not exist')
    def patch(self, gameid):
        data = self.parser.parse_args()
        name = data["name"]
        config = data["config"]
        if not (name and config and gameid):
            return "Invalid request", 400

        # check if game exists
        try:
            game = Game.get(Game.id == gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # update game
        if game.name != name:
            game.name = name
        if game.config.template != config:
            game.config.template = config
            game.config.save()
        game.save()

        return "Game updated", 200


@api.route('/games/<string:gameid>/scores', methods=['GET', 'DELETE'])
class Scores(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('player_id', type=str, location='form', required=True)
    parser.add_argument('score', type=str, location='form', required=True)

    @api.response(200, 'Score fetched')
    @api.response(404, 'Game does not exist')
    def get(self, gameid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # fetch all scores for the given game
        scores = Score.select().where(Score.game == game).order_by(Score.hidden_score.desc())

        # sort the scores by the score value
        # scores = sorted(scores, key=lambda s: s.score, reverse=True)

        # create a list of dictionaries with the player name and score
        scores_dic_array = []
        rank = 1
        for score in scores:
            scores_dic_array.append({
                "name": score.player.name,
                "score": score.json_score,
                "rank": rank
            })
            rank += 1

        return scores_dic_array

    @api.response(200, 'Scores deleted')
    @api.response(404, 'Game does not exist')
    def delete(self, gameid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # delete all scores for the given game
        Score.delete().where(Score.game == game).execute()

        return "Scores deleted", 204


@api.route('/games/<string:gameid>/scores/<string:playerid>', methods=['GET', 'POST', 'DELETE'])
class PlayerScore(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('score', type=str, location='form', required=True)

    @api.response(200, 'Score fetched')
    @api.response(404, 'Game, Player or Score does not exist')
    def get(self, gameid, playerid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # check if player exists
        try:
            player = Player.get(id=playerid)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        # fetch the score for the given player and game
        try:
            score = Score.get(player=player, game=game)
        except peewee.DoesNotExist:
            return "No scores found", 404

        player_rank = Score.select().where(Score.game == game, Score.hidden_score > score.hidden_score).count() + 1

        return jsonify({
            "name": score.player.name,
            "score": score.json_score,
            "rank": player_rank
        })

    @api.expect(parser)
    @api.doc(params={
        'score': 'json formatted score to insert',
    })
    @api.response(201, 'Score added')
    @api.response(400, 'Invalid request')
    @api.response(404, 'Player or game does not exist')
    def post(self, gameid, playerid):
        data = self.parser.parse_args()

        try:
            score = json.loads(data["score"])
        except json.decoder.JSONDecodeError:
            return "Invalid score, must be json", 400

        if not (gameid and playerid and score):
            return "Invalid request", 400

        # check if player and game exist
        try:
            game = Game.get(id=gameid)
            player = Player.get(id=playerid)
        except peewee.DoesNotExist:
            return "Player or game does not exist", 404

        # check if given score has the same json keys as the config
        score_config = game.config.template["template"]
        if not all(key in score_config for key in score):
            return "Invalid score, must have the same keys as the config", 400

        # check if player has already played the game
        # if not add the player to the game
        try:
            PlayerGame.get(player=player, game=game)
        except peewee.DoesNotExist:
            PlayerGame.create(player=player, game=game)

        # calculate hidden score usding the config weights and the given score
        hidden_score = 0
        for key in score:
            if score_config[key]["weight"] == 0:
                continue
            if score_config[key]["type"] == "int":
                hidden_score += int(score[key]) * float(score_config[key]["weight"])
            elif score_config[key]["type"] == "float":
                hidden_score += float(score[key]) * float(score_config[key]["weight"])

        # fetch player scores for the given game if any
        if "keep_worse_scores" not in score_config:
            try:
                # using the config template compare the current score with the previous score
                # if the current score is better update the score
                player_score = Score.get(player=player, game=game)
                if hidden_score > player_score.hidden_score:
                    player_score.json_score = score
                    player_score.hidden_score = hidden_score
                    player_score.save()
                    return "Score updated", 200
            except peewee.DoesNotExist:
                Score.create(player=player, game=game, json_score=score, hidden_score=hidden_score)
                return "Score added", 201
        else:
            Score.create(player=player, game=game, json_score=score, hidden_score=hidden_score)
            return "Score added", 201

    @api.response(204, 'Score deleted')
    @api.response(404, 'Game, Player or Score does not exist')
    def delete(self, gameid, playerid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # check if player exists
        try:
            player = Player.get(id=playerid)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        # fetch the score for the given player and game
        try:
            score = Score.get(player=player, game=game)
            score.delete_instance()
        except peewee.DoesNotExist:
            return "No scores found", 404

        return "Score deleted", 204


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host="127.0.0.1", threaded=True, port=5000)
