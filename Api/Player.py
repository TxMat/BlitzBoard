import json


class Player:
    def __init__(self, player_id=None, name=""):
        self.id = player_id
        self.name = name

    def __eq__(self, other):
        return self.id == other.id

    def __bool__(self):
        return self.id is not None

    def __ne__(self, other):
        return self.id != other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
