import json

from flask import Flask
from flask_restx import Api, Resource, reqparse

from Api.db import db

debug = False

app = Flask(__name__)
# database = db.GameDatabase("..")

api = Api(
    app=app,
    title='BlitzBoard API',
    description="Robust and Reliable api to store player high scores",
    version="0.0.1"
)


@api.route('/new-score', methods=['POST'])
class NewScore(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('player_id', type=str, location='form', required=True)
    parser.add_argument('game_name', type=str, location='form', required=True)
    parser.add_argument('score', type=str, location='form', required=True)

    @api.expect(parser)
    @api.doc(params={
        'player_id': 'UUID of the player making the request',
        'game_name': 'the name of the game',
        'score': 'json formatted score to insert',
    })
    def post(self):
        data = self.parser.parse_args()

        player_id = data["player_id"]
        game_name = data["game_name"]
        score = data["score"]

        if not (game_name and player_id and score):
            return "Invalid request", 400

        return 200


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host="127.0.0.1", threaded=True, port=5000)
