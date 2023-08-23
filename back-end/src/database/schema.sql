DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS patients_recordings;
DROP TABLE IF EXISTS sleep_stage_detection;

CREATE TABLE labels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient INTEGER NOT NULL,
  location_begin INTEGER NOT NULL,
  location_end INTEGER NOT NULL,
  duration  REAL NOT NULL
);


CREATE TABLE patients_recordings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  week INTEGER NOT NULL,
  day INTEGER NOT NULL,
  hours INTEGER NOT NULL,
  minutes INTEGER NOT NULL,
  seconds INTEGER NOT NULL,
  recorder TEXT,
  MR REAL NOT NULL,
  ML REAL NOT NULL,
  SU REAL NOT NULL,
  Microphone REAL,
  Eye REAL NOT NULL,
  ECG REAL NOT NULL,
  Pressure REAL
);


CREATE TABLE sleep_stage_detection (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  day INTEGER NOT NULL,
  hours INTEGER NOT NULL,
  minutes INTEGER NOT NULL,
  seconds INTEGER NOT NULL,
  start_id INTEGER NOT NULL,
  end_id INTEGER NOT NULL,
  LF_HF REAL NOT NULL,
  SD REAL NOT NULL,
  stage TEXT,
  y INTEGER NOT NULL,
  x INTEGER NOT NULL
)