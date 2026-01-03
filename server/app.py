# app.py

from flask_cors import CORS
from flask import Flask, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, bcrypt, User, Note

app = Flask(__name__)

# allow the frontend to send cookies (sessions) to the backend
CORS(app, supports_credentials=True)

# cookie settings for local development
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

# needed for sessions
app.config["SECRET_KEY"] = "super-secret-key"

# sqlite keeps it simple for labs
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)

migrate = Migrate(app, db)
api = Api(app)

# helper: get logged in user
def get_current_user():
    """
    session["user_id"] is set after login/signup.
    If there's no user_id in the session, user is not logged in.
    """
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.query.get(user_id)


# AUTH ROUTES
class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "username and password are required"}, 400

        # check if username already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            return {"error": "username already taken"}, 400

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # log in immediately
        session["user_id"] = user.id

        return {"id": user.id, "username": user.username}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "username and password are required"}, 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return {"error": "invalid username or password"}, 401

        session["user_id"] = user.id
        return {"id": user.id, "username": user.username}, 200


class Logout(Resource):
    def delete(self):
        # remove user from session
        session.pop("user_id", None)
        return {"message": "logged out"}, 200


class CheckSession(Resource):
    def get(self):
        user = get_current_user()
        if not user:
            return {"error": "unauthorized"}, 401
        return {"id": user.id, "username": user.username}, 200


# NOTES ROUTES 
class Notes(Resource):
    def get(self):
        user = get_current_user()
        if not user:
            return {"error": "unauthorized"}, 401

        # pagination 
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        pagination = Note.query.filter_by(user_id=user.id).paginate(
            page=page, per_page=per_page
        )

        notes_data = []
        for note in pagination.items:
            notes_data.append(
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "user_id": note.user_id,
                }
            )

        return {
            "notes": notes_data,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        user = get_current_user()
        if not user:
            return {"error": "unauthorized"}, 401

        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return {"error": "title and content are required"}, 400

        note = Note(title=title, content=content, user_id=user.id)

        db.session.add(note)
        db.session.commit()

        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id,
        }, 201


class NoteById(Resource):
    def patch(self, id):
        user = get_current_user()
        if not user:
            return {"error": "unauthorized"}, 401

        note = Note.query.get(id)
        if not note:
            return {"error": "note not found"}, 404

        # security check
        if note.user_id != user.id:
            return {"error": "forbidden"}, 403

        data = request.get_json()

        if "title" in data:
            note.title = data["title"]
        if "content" in data:
            note.content = data["content"]

        db.session.commit()

        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id,
        }, 200

    def delete(self, id):
        user = get_current_user()
        if not user:
            return {"error": "unauthorized"}, 401

        note = Note.query.get(id)
        if not note:
            return {"error": "note not found"}, 404

        # security check
        if note.user_id != user.id:
            return {"error": "forbidden"}, 403

        db.session.delete(note)
        db.session.commit()

        return {"message": "note deleted"}, 200


# route registration
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

api.add_resource(Notes, "/notes")
api.add_resource(NoteById, "/notes/<int:id>")


if __name__ == "__main__":
    app.run(debug=True)
