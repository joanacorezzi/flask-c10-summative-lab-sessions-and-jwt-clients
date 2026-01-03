# seed.py

from faker import Faker
from app import app
from models import db, User, Note

fake = Faker()


def seed():
    # app_context to use the database safely
    with app.app_context():
        # delete existing rows so we can re-run seed
        Note.query.delete()
        User.query.delete()

        # create a couple users
        user1 = User(username="joana")
        user1.set_password("password123")

        user2 = User(username="alex")
        user2.set_password("password123")

        db.session.add_all([user1, user2])
        db.session.commit()

        # create some notes for each user
        for _ in range(8):
            note = Note(
                title=fake.sentence(nb_words=3),
                content=fake.paragraph(nb_sentences=2),
                user_id=user1.id,
            )
            db.session.add(note)

        for _ in range(5):
            note = Note(
                title=fake.sentence(nb_words=3),
                content=fake.paragraph(nb_sentences=2),
                user_id=user2.id,
            )
            db.session.add(note)

        db.session.commit()
        print("seeded!")


if __name__ == "__main__":
    seed()
