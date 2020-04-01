import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
curr_category = None


def paginate(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  return questions[start:end]


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = format_categories(categories)
    print('formatted categories', formatted_categories)

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(formatted_categories)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def format_categories(categories):
    cat_dict = {}
    for cat in categories:
      cat_dict[cat.id] = cat.type
    return cat_dict

  @app.route('/questions')
  def getQuestions():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = format_categories(categories)
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'total_questions': len(questions),
      'questions': current_questions,
      'current_category': curr_category,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })

    except:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    if question and answer:
      try:
        new_question = Question(question, answer, int(category), int(difficulty))
        new_question.insert()
        return jsonify({
          'success': True,
          'added': new_question.format()
        })
      except Exception as e:
        print('error', e.args)
        abort(422)
    else:
      abort(400)



  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', '')
    questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
    result_questions = paginate(request, questions)
    return jsonify({
      'success': True,
      'questions': result_questions,
      'total_questions': len(questions)
    })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions],
      'total_questions': len(questions),
      'current_category': category_id
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  
 data: JSON.stringify({
        previous_questions: previousQuestions,
        quiz_category: this.state.quizCategory
        
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/play', methods=['POST'])
  def play_game():
    category_id = 0
    body = request.get_json()
    prev_questions = body.get('previous_questions', [])

    if len(prev_questions) > 4:
      return jsonify({
        'success': True,
        'question': None
      })

    category = body.get('quiz_category', 0)
    if category:
      category_id = int(category['id'])

    if category_id > 1:
      questions = Question.query.filter(Question.category == category_id).all()
    else:
      questions = Question.query.all()

    if len(questions) > len(prev_questions):
      curr_questions = [q for q in questions if q.id not in prev_questions]
      random_question = random.choice(curr_questions)
      return jsonify({
        'success': True,
        'question': random_question.format()
      })
    else:
      return jsonify({
        'success': True,
        'question': None
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }), 405

  @app.errorhandler(422)
  def could_not_be_processed(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'request could not be processed'
    }), 422

  return app

