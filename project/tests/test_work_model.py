# project/tests/test_user_model.py
import unittest

from project.server import db
from project.server.models import User, Work, Version
from project.tests.base import BaseTestCase


class TestUserModel(BaseTestCase):

    def test_work_title(self):
        user = User(
            email='test@test.com',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        work = Work(
            user_id=user.id
        )
        db.session.add(work)
        db.session.commit()
        self.assertEqual(work.title, "Untitled")
    
    def test_two_versions(self):
        user = User(
            email='test@test.com',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        work = Work(
            user_id=user.id
        )
        work.title = "Test"
        db.session.add(work)
        db.session.commit()
        work.new_version()
        self.assertEqual(work.newest_version, 2)


if __name__ == '__main__':
    unittest.main()
