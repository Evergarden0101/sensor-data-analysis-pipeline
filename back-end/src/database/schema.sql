DROP TABLE IF EXISTS label;

CREATE TABLE label (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start INTEGER NOT NULL,
  end INTEGER NOT NULL
);



/*
Example:
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);


Code to add to db.py:
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


Code to add to __init__.py:
def create_app():
    app = ...
    # existing code omitted

    from . import db
    db.init_app(app)

    return app

Initialize the database: flask --app flaskr init-db

see: https://flask.palletsprojects.com/en/2.3.x/tutorial/database/

*/