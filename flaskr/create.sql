DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS leaderboards;




CREATE TABLE player (
    /* Will be an uuid  */
    id_player INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL
);


CREATE TABLE leaderboards (
  id_player INTEGER PRIMARY KEY,
  score INTEGER NOT NULL,
  FOREIGN KEY (id_player) REFERENCES player(id_player)

);
