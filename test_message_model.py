"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        user1 = User.signup("user1", "user1@gmail.com", "password", None)
        user1.id = 1

        db.session.commit()

        user1 = User.query.get(user1.id)

        self.user1 = user1

        self.client = app.test_client()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_message_model(self):
        """Does basic model work?"""
        
        message = Message(text="testing 1 2...", user_id=1)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(self.user1.messages[0].text, "testing 1 2...")


    def test_message_likes(self):
        message = Message(text="testing, testing", user_id=1)

        user2 = User.signup("user2", "user2@gmail.com", "password", None)
        user2.id = 2
        db.session.add_all([message, user2])
        db.session.commit()

        user2.likes.append(message)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == 2).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, message.id)
