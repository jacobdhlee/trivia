import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            "question": "do you want a car?",
            "answer": "Yes",
            "difficulty": 2,
            "category": 3
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get('/questions')
        body = json.loads(res.data)
        status_code = res.status_code
        category = body['categories']

        self.assertEqual(status_code, 200)
        self.assertEqual(len(body['questions']), 10)
        self.assertEqual(body['total_questions'], 28)
        self.assertEqual(category['1'], 'Science')
        self.assertEqual(category['2'], 'Art')
        self.assertEqual(category['3'], 'Geography')
        self.assertEqual(category['4'], 'History')
        self.assertEqual(category['5'], 'Entertainment')
        self.assertEqual(category['6'], 'Sports')

    def test_get_category(self):
        res = self.client().get('/categories')
        body = json.loads(res.data)
        status_code = res.status_code
        category = body['categories']
        self.assertEqual(status_code, 200)
        self.assertEqual(category['1'], 'Science')
        self.assertEqual(category['2'], 'Art')
        self.assertEqual(category['3'], 'Geography')
        self.assertEqual(category['4'], 'History')
        self.assertEqual(category['5'], 'Entertainment')
        self.assertEqual(category['6'], 'Sports')

    def test_post_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

    def test_delete_question(self):
        res = self.client().delete('/questions/32')
        print('data ', res.status_code)
        print('data ', res)
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 32).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'car'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()