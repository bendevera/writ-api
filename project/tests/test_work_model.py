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
        self.assertEqual(work.versions[0].data['title'], "")
    
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
        work.versions[0].data['title'] = "Test"
        db.session.add(work)
        db.session.commit()
        new_version = work.new_version()
        self.assertEqual(work.versions[0].data['title'], new_version.data['title'])
        self.assertEqual(work.newest_version, 2, new_version.number)


if __name__ == '__main__':
    unittest.main()
