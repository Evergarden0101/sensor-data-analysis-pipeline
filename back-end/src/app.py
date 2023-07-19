from flask import Flask, request
import werkzeug
import json
import sqlite3 as sql
from database import db

"""Example of possible structure for posting the label data"""
def create_app():
    app = Flask(__name__)

    db.init_app(app)
    
    # Helper functions and variables
    def insert_label(label):
        DATABASE = ''

        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO BRUX_EVENTS VALUES (?)", (label))


    @app.route("/label-brux", methods=["POST"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def label_brux():
        try:
            try:
                label = request.json
            except werkzeug.exceptions.BadRequest:
                return "Please sent a Json package!", 400
            if label.start > label.end:
                return "Start time cannot be greater than end time!", 400
           
            insert_label(label)
            return "Successfuly inserted into Database", 200
        except Exception:
            return "There is something wrong with your Json or label you have sent! Check format!", 400

    return app

    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)