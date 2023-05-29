from marshmallow import Schema, fields
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_pyfile("default_config.py")
app.config.from_envvar("APP_SETTINGS", silent=True)

db = SQLAlchemy(app)


class Note(db.Model):
    __tablename__ = 'note'
    note_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    text = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=func.now())


class NoteSchema(Schema):
    note_id = fields.Integer(dump_only=True)
    title = fields.String()
    text = fields.String()
    data = fields.DateTime()


with app.app_context():
    db.create_all()


@app.route("/notes/")
def index():
    notes = Note.query.all()
    print(notes)
    response = []
    for note in notes:
        response.append({
            "note_id": note.note_id,
            "title": note.title,
            "text": note.text,
            "data": note.data
        })
    print(response)
    return jsonify(response)


@app.route("/notes/<int:note_id>")
def note_by_note_id(note_id):
    note = Note.query.get(note_id)
    return jsonify({
        "note_id": note.note_id,
        "title": note.title,
        "text": note.text,
        "data": note.data
    }), 200


@app.route("/notes", methods=["POST"])
def register():
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
        return jsonify({"error": "already exists"}), 400

    return jsonify({"title": note.title, "text": note.text}), 200


@app.route('/notes/<int:note_id>', methods=["PUT"])
def put(note_id):
    # try:
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
    # except Exception:
    #     return {"message": "error"}, 404


@app.route('/notes/<int:note_id>', methods=["DELETE"])
def delete(note_id):
    try:
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        return f'You have deleted note № {note_id}', 200
    except Exception:
        return {"message": "error"}, 404


if __name__ == "__main__":
    app.run(debug=True)
