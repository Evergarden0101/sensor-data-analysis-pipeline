DROP TABLE IF EXISTS labels;

CREATE TABLE labels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  location_begin INTEGER NOT NULL,
  location_end INTEGER NOT NULL,
  duration  REAL NOT NULL
);