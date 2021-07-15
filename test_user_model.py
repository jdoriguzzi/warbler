"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup("user1", "user1@gmail.com", "password", None)
        user1.id = 1

        user2 = User.signup("user2", "user2@gmail.com", "password", None)
        user2.id = 2

        db.session.commit()

        user1 = User.query.get(user1.id)
        user2 = User.query.get(user2.id)

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # User should be following no other users
        self.assertEqual(len(u.messages), 0)

    #test repr

    # test following functions

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    # test signup valid/invalid

    def test_signup(self):
        user = User.signup("user3", "user3@gmail.com", "password", None)
        id = 3
        user.id = id
        db.session.commit()

        user1 = User.query.get(id)
        self.assertIsNotNone(user1)
        self.assertEqual(user1.username, "user3")
        self.assertEqual(user1.email, "user3@gmail.com")
        self.assertNotEqual(user1.password, "password")

    def test_invalid_signup(self):
        user = User.signup(None, "test@test.com", "password", None)
        user.id = 4
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    # test authenticate

    def test_authenticate(self):
        user = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("wrongname", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "wrongpass"))

    


    