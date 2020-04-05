import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_categories'], 6)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(['questions'])
        self.assertTrue(data['categories'])

    def test_not_found_questions_beyond_page_range(self):
        res = self.client().get('/questions?page=99999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')
        self.assertTrue(data['error'], 404)

    def test_delete_question(self):
        question_id = 23
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)
        question = Question.query.filter(Question.id ==
                                         question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(question, None)

    def test_delete_question_not_exist(self):
        res = self.client().delete('/questions/99999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'request could not be processed')

    def test_search_questions_results(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'], 2)

    def test_search_questions_no_results(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'kdjfghskdfh'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_questions_by_category_results(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 2)
        self.assertEqual(data['current_category'], 6)

    def test_questions_by_category_no_results(self):
        res = self.client().get('/categories/99999/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_add_question(self):
        res = self.client().post('/questions', json={
            'question': 'What is the largest state east of the Mississippi Riv'
                        'er?',
            'answer': 'Georgia',
            'category': 3,
            'difficulty': 3
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added']['question'], 'What is the largest state'
                                                    ' east of the Mississippi '
                                                    'River?')
        self.assertEqual(data['added']['answer'], 'Georgia')
        self.assertEqual(data['added']['category'], 3)
        self.assertEqual(data['added']['difficulty'], 3)

    def test_add_question_bad_request(self):
        res = self.client().post('/questions', json={
            'question': 'What is the largest state east of the Mississippi Riv'
                        'er?',
            'category': 3,
            'difficulty': 3
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
        self.assertEqual(data['error'], 400)

    def test_add_question_method_not_allowed(self):
        res = self.client().patch('/questions', json={
            'question': 'What is the largest state east of the Mississippi Riv'
                        'er?',
            'answer': 'Georgia',
            'category': 3,
            'difficulty': 3
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertEqual(data['error'], 405)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
