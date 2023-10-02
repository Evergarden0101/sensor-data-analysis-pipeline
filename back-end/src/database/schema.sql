DROP TABLE IF EXISTS confirmed_labels;
DROP TABLE IF EXISTS predicted_labels;
DROP TABLE IF EXISTS bite_records;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS patients_recordings;
DROP TABLE IF EXISTS sleep_stage_detection;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS sensors;


CREATE TABLE models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  accuracy DECIMAL(6,3) NOT NULL,
  model_name TEXT,
  model_path TEXT
);


CREATE TABLE bite_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  week INTEGER NOT NULL,
  night_id INTEGER NOT NULL,
  recorder TEXT,
  bite_begin INTEGER NOT NULL,
  bite_end INTEGER NOT NULL,
  duration DECIMAL(7,3) NOT NULL,
  peakMR DECIMAL(11,6),
  peakML DECIMAL(11,6),
  avgMR DECIMAL(11,6),
  avgML DECIMAL(11,6)
);


CREATE TABLE confirmed_labels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  week INTEGER NOT NULL,
  night_id INTEGER NOT NULL,
  recorder TEXT,
  label_id INTEGER NOT NULL,
  location_begin DECIMAL(11,3) NOT NULL,
  location_end DECIMAL(11,3) NOT NULL,
  peakMR DECIMAL(11,6),
  peakML DECIMAL(11,6),
  avgMR DECIMAL(11,6),
  avgML DECIMAL(11,6),
  corrected BOOLEAN NOT NULL
  -- duration  REAL NOT NULL
);


CREATE TABLE predicted_labels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  week INTEGER NOT NULL,
  night_id INTEGER NOT NULL,
  recorder TEXT,
  label_id INTEGER NOT NULL,
  location_begin DECIMAL(11,3) NOT NULL,
  location_end DECIMAL(11,3) NOT NULL,
  peakMR DECIMAL(11,6),
  peakML DECIMAL(11,6),
  avgMR DECIMAL(11,6),
  avgML DECIMAL(11,6)
  -- duration  REAL NOT NULL
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
  week INTEGER NOT NULL,
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
  x INTEGER NOT NULL,
  selected BOOLEAN NOT NULL
);

CREATE TABLE settings (
  id INTEGER PRIMARY KEY,
  study_type TEXT NOT NULL,
  activity TEXT NOT NULL,
  original_sampling INTEGER NOT NULL,
  REM_sampling INTEGER NOT NULL,
  NREM_sampling INTEGER NOT NULL,
  dataset_format TEXT NOT NULL,
  filtered BOOLEAN NOT NULL,
  normalized BOOLEAN NOT NULL
);

CREATE TABLE sensors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,
  name TEXT NOT NULL
);