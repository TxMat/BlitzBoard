import json

import peewee
from flask import Flask, jsonify
from flask_restx import Api, Resource, reqparse
from playhouse.sqlite_ext import JSONField

app = Flask(__name__)

api = Api(
    app=app,
    title='BlitzBoard API',
    description="Robust and Reliable api to store player high scores",
    version="0.0.1"
)

db = peewee.SqliteDatabase('db/db.sqlite', check_same_thread=False)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Config(BaseModel):
    template = JSONField()
    weight_list = JSONField(null=True)


class Game(BaseModel):
    id = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField()
    config = peewee.ForeignKeyField(Config, backref='games')


class Player(BaseModel):
    id = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField()


class PlayerGame(BaseModel):
    player = peewee.ForeignKeyField(Player)
    game = peewee.ForeignKeyField(Game)


class Score(BaseModel):
    player = peewee.ForeignKeyField(Player, backref='scores')
    game = peewee.ForeignKeyField(Game, backref='scores')
    score = JSONField()


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

    @api.response(200, 'Player scores fetched')
    @api.response(404, 'Player does not exist')
    def get(self, player_id):
        try:
            player = Player.get(Player.id == player_id)
        except peewee.DoesNotExist:
            return "Player does not exist", 404

        scores = Score.select().where(Score.player == player)
        scores_dic_array = []
        for score in scores:
            scores_dic_array.append(score.to_dic())
        return jsonify(scores_dic_array)

    @api.response(200, 'Player scores deleted')
    @api.response(404, 'Player does not exist')
    def delete(self, player_id):
        try:
            Score.delete().where(Score.player == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 404

        return "Player scores deleted", 200


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
        try:
            Player.delete().where(Player.id == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 404

        return "Player deleted", 200

    @api.expect(parser)
    @api.response(200, 'Player updated')
    @api.response(404, 'Player does not exist')
    @api.response(400, 'Invalid request')
    def patch(self, player_id):
        data = self.parser.parse_args()
        name = data["name"]
        if not (name and player_id):
            return "Invalid request", 400

        try:
            Player.update(name=name).where(Player.id == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 404

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
    @api.response(200, 'Game created')
    @api.response(409, 'Game already exists')
    @api.response(400, 'Invalid request')
    def post(self):
        data = self.parser.parse_args()

        game_id = data["id"]
        name = data["name"]
        config = data["config"]

        if not (name and config and game_id):
            return "Invalid request", 400

        # check if game already exists if not create it
        try:
            config = Config.create(template=config)
            Game.create(id=game_id, name=name, config=config)
        except peewee.IntegrityError:
            return "Game already exists", 409

        return "Game created", 200

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
        try:
            Game.delete().where(Game.id == gameid).execute()
        except peewee.IntegrityError:
            return "Game does not exist", 404

        return "Game deleted", 200

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

        try:
            Game.update(name=name, config=config).where(Game.id == gameid).execute()
        except peewee.IntegrityError:
            return "Game does not exist", 404

        return "Game updated", 200


@api.route('/games/<string:gameid>/scores', methods=['GET', 'POST', 'DELETE'])
class Scores(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('player_id', type=str, location='form', required=True)
    parser.add_argument('score', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'player_id': 'UUID of the player making the request',
        'score': 'json formatted score to insert',
    })
    @api.response(200, 'Score added')
    @api.response(400, 'Invalid request')
    @api.response(404, 'Player or game does not exist')
    def post(self, gameid):
        data = self.parser.parse_args()

        player_id = data["player_id"]
        try:
            score = json.loads(data["score"])
        except json.decoder.JSONDecodeError:
            return "Invalid score", 400

        if not (gameid and player_id and score):
            return "Invalid request", 400

        # check if player and game exist
        try:
            game = Game.get(id=gameid)
            player = Player.get(id=player_id)
        except peewee.DoesNotExist:
            return "Player or game does not exist", 404

        # check if given score has the same json keys as the config
        config = json.loads(game.config.template)
        if not all(key in config for key in score):
            return "Invalid score", 400

        # check if player has already played the game
        # if not add the player to the game
        try:
            PlayerGame.get(player=player, game=game)
        except peewee.DoesNotExist:
            PlayerGame.create(player=player, game=game)

        # fetch player scores for the given game if any
        try:
            # using the config template compare the current score with the previous score
            # if the current score is better update the score
            player_score = Score.get(player=player, game=game)
            for key in json.loads(game.config.template):
                if score[key] > player_score.score[key]:
                    player_score.score = score
                    player_score.save()
        except peewee.DoesNotExist:
            Score.create(player=player, game=game, score=score)

        return 200

    @api.response(200, 'Score fetched')
    @api.response(404, 'Game does not exist')
    def get(self, gameid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 404

        # fetch all scores for the given game
        scores = Score.select().where(Score.game == game)

        # sort the scores by the score value
        scores = sorted(scores, key=lambda s: s.score, reverse=True)

        # create a list of dictionaries with the player name and score
        scores_dic_array = []
        for score in scores:
            scores_dic_array.append({
                "name": score.player.name,
                "score": score.score
            })

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

        return "Scores deleted", 200


@api.route('/<string:gameid>/<string:playerid>/score', methods=['GET', 'DELETE'])
class PlayerScore(Resource):

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

        return score.score

    @api.response(200, 'Score deleted')
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

        return "Score deleted", 200


if __name__ == '__main__':
    # Create the database
    db.create_tables([Game, Player, Score, Config, PlayerGame])
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host="127.0.0.1", threaded=True, port=5000)
