DROP TABLE IF EXISTS result;

CREATE TABLE result (
  filename TEXT PRIMARY KEY,
  severity INTEGER NOT NULL,
  probability INTEGER NOT NULL
);

CREATE TABLE user (
  username TEXT PRIMARY KEY,
  password TEXT NOT NULL
);