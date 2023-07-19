from flask import Flask, request
import werkzeug
import os, json
import sqlite3 as sql
from database import db
from flask_cors import CORS

"""Example of possible structure for posting the label data"""
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'labels.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    
    # Helper functions and variables
    def insert_label(label):
        DATABASE = 'instance/labels.sqlite'

        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO labels (location_begin, location_end, duration) VALUES {label}")


    @app.route("/label-brux", methods=["POST"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def label_brux():
        try:
            try:
                label = request.json
                print(label)
            except werkzeug.exceptions.BadRequest:
                return "Please sent a Json package!", 400
            if label["location_begin"] > label["location_end"]:
                return "Start time cannot be greater than end time!", 400
           
            print(tuple(label.values()))
            insert_label(tuple(label.values()))
            return "Successfuly inserted into Database", 200
        except Exception as e:
            return f"{e}", 400

    return app

    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)