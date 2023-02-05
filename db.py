import os
import sqlite3


class Player:
    def __init__(self, id: int, name: str, score: int | None):
        self.id = id
        self.name = name
        self.score = score

    def to_dic(self):
        return {"id": self.id, "name": self.name, "score": self.score}


class BaseDatabase:
    def __init__(self, path: str = "."):
        self.__db_path = path + "/database.db"
        self.__sql_path = path + "/create.sql"
        if not os.path.isfile(self.__db_path):
            self.__initialize_database()
        self.connection = sqlite3.connect(self.__db_path, check_same_thread=False)

    def __initialize_database(self):
        connection = sqlite3.connect(self.__db_path, check_same_thread=False)

        with open(self.__sql_path) as f:
            connection.executescript(f.read())

        connection.commit()
        connection.close()

    def clear_database(self):
        self.__initialize_database()

    def __del__(self):
        self.connection.close()

    def query(self, request: str, values: list = ()) -> list:
        rep = self.connection.execute(request, values)
        return rep.fetchall()

    def execute(self, request: str, values: list = ()) -> bool:
        rep = self.connection.execute(request, values)
        self.connection.commit()
        return rep.fetchone()


class GameDatabase(BaseDatabase):
    def __init__(self, path: str):
        super().__init__(path)

    # Players management

    # Create a player and an other inside the leaderboards
    def create_player(self, name: str) -> int | None:
        users_number = self.query("SELECT * from player", ())
        user_id = len(users_number) + 1
        self.execute("INSERT INTO player(id_player,name) VALUES(?,?)", (user_id, name))

        self.execute("INSERT INTO leaderboards(id_player,score) VALUES(?,?)",
                     (user_id, 0))
        player_created = self.get_player(user_id) is not None
        return user_id if player_created else None

    def get_player(self, id_player: int) -> Player:
        user = self.query(
            "SELECT p.id_player, p.name, l.score from player p, leaderboards l where p.id_player=? and l.id_player = "
            "p.id_player", (id_player,))
        if len(user) >= 1:
            current_user = user[0]
            return Player(current_user[0], current_user[1], current_user[2])
        else:
            return None

    def get_players(self) -> list[Player]:
        users_obj = list()
        users = self.query(
            "SELECT p.id_player, p.name, l.score from player p, leaderboards l where l.id_player = p.id_player")
        for user in users:
            users_obj.append(Player(user[0], user[1], user[2]))
        return users_obj

    def player_exist(self, id_player: int) -> bool:
        return self.get_player(id_player) is not None

    def remove_player(self, id_player: int) -> bool:
        remove_from_leaderboards = self.execute("DELETE FROM leaderboards WHERE id_player =?", (id_player,))
        remove_from_player = self.execute("DELETE FROM player WHERE id_player =?", (id_player,))
        return remove_from_leaderboards and remove_from_player

    def remove_all_players(self):
        return self.execute("DELETE FROM leaderboards", ())

    # Leaderboards management
    def set_score_to_player(self, player_id: int, score: int) -> bool:
        user_exist = len(self.query("SELECT * FROM player WHERE id_player=?", (player_id,))) == 1
        if not user_exist:
            print("User not exist in player table")
            return False

        user_in_leaderboards = len(self.query("SELECT * FROM leaderboards WHERE id_player=?", (player_id,))) == 1
        if user_in_leaderboards:
            self.execute("UPDATE leaderboards SET score = ? WHERE id_player=?;", (score, player_id))
        else:
            self.execute("INSERT INTO leaderboards VALUES(?,?)", (player_id, score))
        scores = self.query("SELECT * from leaderboards WHERE id_player=?", (player_id,))
        return len(scores) == 1

