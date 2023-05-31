"""
This is a Flask application that provides an API for managing notes using a SQLite database.

Dependencies:
- marshmallow
- Flask
- flask_sqlalchemy
- SQLAlchemy

Endpoints:
- GET /notes/ : Retrieves all notes
- GET /notes/<note_id> : Retrieves a specific note by its ID
- POST /notes : Creates a new note
- PUT /notes/<note_id> : Updates an existing note
- DELETE /notes/<note_id> : Deletes a note.

Models:
- Note : Represents a note in the database

Schemas:
- NoteSchema : Schema for serializing/deserializing Note objects

"""

from marshmallow import Schema, fields
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config.from_envvar("APP_SETTINGS", silent=True)

db = SQLAlchemy(app)


class Note(db.Model):
    """
    Represents a note in the database.

    Attributes:
        tablename (str): The name of the database table.
        note_id (int): The ID of the note (primary key).
        title (str): The title of the note.
        text (str): The text content of the note.
        data (datetime): The date and time when the note was created (default: current timestamp).
    """
    tablename = 'note'
    note_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    text = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=func.now())


class NoteSchema(Schema):
    """
    Schema for serializing/deserializing Note objects.
    """
    note_id = fields.Integer(dump_only=True)
    title = fields.String()
    text = fields.String()
    data = fields.DateTime()


with app.app_context():
    db.create_all()


@app.route("/notes/")
def index():
    """
    Retrieves all notes.

    Returns:
        response (list): A list of dictionaries representing the notes.
    """
    notes = Note.query.all()
    response = []
    for note in notes:
        response.append({
            "note_id": note.note_id,
            "title": note.title,
            "text": note.text,
            "data": note.data
        })
    return jsonify(response)


@app.route("/notes/<int:note_id>")
def note_by_note_id(note_id):
    """
    Retrieves a specific note by its ID.

    Args:
        note_id (int): The ID of the note to retrieve.

    Returns:
        response (dict): A dictionary representing the note.
        status_code (int): The HTTP status code.
    """
    note = Note.query.get(note_id)
    return jsonify({
        "note_id": note.note_id,
        "title": note.title,
        "text": note.text,
        "data": note.data
    }), 200


@app.route("/notes", methods=["POST"])
def register():
    """
    Creates a new note.

    Returns:
        response (dict): A dictionary containing the title and text of the created note.
        status_code (int): The HTTP status code.
    """
    new_note = request.json
    if not new_note or "text" not in new_note or "title" not in new_note:
        return jsonify({"error": "invalid note ID request"}), 400

    try:
        note = Note(
            title=new_note["title"],
            text=new_note["text"],
        )
        db.session.add(note)
        db.session.commit()
    except IntegrityError:
        return jsonify({"error": "already exists"})


@app.route('/notes/<int:note_id>', methods=["PUT"])
def put(note_id):
    """
    Changes all fields in note by note_id.

    Returns:
        response (dict): A dictionary containing the title and text of the changed note.
        status_code (int): The HTTP status code.
    """
    try:
        note = db.session.query(Note).get(note_id)
        req_json = request.json

        note.text = req_json.get('text')
        note.title = req_json.get('title')

        db.session.add(note)
        db.session.commit()
        return jsonify({
            "note_id": note.note_id,
            "title": note.title,
            "text": note.text,
            "data": note.data}), 204
    except Exception:
        return {"message": "error"}, 404

@app.route('/notes/<int:note_id>', methods=["DELETE"])
def delete(note_id):
    """
    Changes all fields in note by note_id.

    Returns:
        response (str): Result of function: "deleted" or error.
        status_code (int): The HTTP status code.
    """
    try:
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        return f'You have deleted note № {note_id}', 200
    except Exception:
        return {"message": "error"}, 404



if __name__ == "__main__":
    app.run(debug=True)