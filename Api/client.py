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
    weight_list = JSONField()


class Game(BaseModel):
    id = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField()
    config = peewee.ForeignKeyField(Config, backref='games')


class Player(BaseModel):
    id = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField()
    games = peewee.ManyToManyField(Game, backref='players')


class Score(BaseModel):
    player = peewee.ForeignKeyField(Player, backref='scores')
    game = peewee.ForeignKeyField(Game, backref='scores')
    score = JSONField()


@api.route('/players', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
class Players(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=str, location='form', required=True)
    parser.add_argument('name', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'id': 'UUID of the player',
        'name': 'Name of the player',
    })
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
            return "Player already exists", 201

        return "Player created", 200

    def get(self):
        players = Player.select()
        players_dic_array = []
        for player in players:
            players_dic_array.append(player.to_dic())
        return jsonify(players_dic_array)

    def delete(self):
        data = self.parser.parse_args()
        player_id = data["id"]
        if not player_id:
            return "Invalid request", 400

        try:
            Player.delete().where(Player.id == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 400

        return "Player deleted", 200

    def update(self):
        data = self.parser.parse_args()
        player_id = data["id"]
        name = data["name"]
        if not (name and player_id):
            return "Invalid request", 400

        try:
            Player.update(name=name).where(Player.id == player_id).execute()
        except peewee.IntegrityError:
            return "Player does not exist", 400

        return "Player updated", 200


@api.route('/players/<string:player_id>/scores', methods=['GET'])
class PlayerScores(Resource):
    def get(self, player_id):
        scores = Score.select().where(Score.player == player_id)
        scores_dic_array = []
        for score in scores:
            scores_dic_array.append(score.to_dic())
        return jsonify(scores_dic_array)


@api.route('/games', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
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
    def post(self):
        data = self.parser.parse_args()

        game_id = data["id"]
        name = data["name"]
        config = data["config"]

        if not (name and config and game_id):
            return "Invalid request", 400

        # check if game already exists if not create it
        try:
            config = Config.create(config=config)
            Game.create(id=game_id, name=name, config=config)
        except peewee.IntegrityError:
            return "Game already exists", 400

        return 200

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

    def delete(self):
        data = self.parser.parse_args()
        game_id = data["id"]
        if not game_id:
            return "Invalid request", 400

        try:
            Game.delete().where(Game.id == game_id).execute()
        except peewee.IntegrityError:
            return "Game does not exist", 400

        return "Game deleted", 200

    def update(self):
        data = self.parser.parse_args()
        game_id = data["id"]
        name = data["name"]
        config = data["config"]
        if not (name and config and game_id):
            return "Invalid request", 400

        try:
            Game.update(name=name, config=config).where(Game.id == game_id).execute()
        except peewee.IntegrityError:
            return "Game does not exist", 400

        return "Game updated", 200


@api.route('/games/<string:gameid>/scores', methods=['GET', 'POST'])
class Scores(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('player_id', type=str, location='form', required=True)
    parser.add_argument('score', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'player_id': 'UUID of the player making the request',
        'score': 'json formatted score to insert',
    })
    def post(self, gameid):
        data = self.parser.parse_args()

        player_id = data["player_id"]
        score = data["score"]

        if not (gameid and player_id and score):
            return "Invalid request", 400

        # check if player and game exist
        try:
            game = Game.get(id=gameid)
            player = Player.get(id=player_id)
        except peewee.DoesNotExist:
            return "Player or game does not exist", 400

        # check if given score has the same json keys as the config
        config = game.config.template
        if not all(key in config for key in score):
            return "Invalid score", 400

        # check if player has already played the game
        # if not add the player to the game
        if player not in game.players:
            game.players.add(player)
            game.save()

        # fetch player scores for the given game if any
        try:
            player_score = Score.get(player=player, game=game)
            player_score.score = score
            player_score.save()
        except peewee.DoesNotExist:
            Score.create(player=player, game=game, score=score)
            return 200

        # using the config template compare the current score with the previous score
        # if the current score is better update the score
        for key in game.config.template:
            if score[key] > player_score.score[key]:
                player_score.score = score
                player_score.save()

        return 200

    def get(self, gameid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 400

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


@api.route('/game/<string:gameid>/<string:playerid>/score', methods=['GET'])
class PlayerScore(Resource):
    def get(self, gameid, playerid):
        # check if game exists
        try:
            game = Game.get(id=gameid)
        except peewee.DoesNotExist:
            return "Game does not exist", 400

        # check if player exists
        try:
            player = Player.get(id=playerid)
        except peewee.DoesNotExist:
            return "Player does not exist", 400

        # fetch the score for the given player and game
        try:
            score = Score.get(player=player, game=game)
        except peewee.DoesNotExist:
            return "Score does not exist", 400

        return score.score


if __name__ == '__main__':
    # Create the database
    db.create_tables([Game, Player, Score, Config])
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host="127.0.0.1", threaded=True, port=5000)
