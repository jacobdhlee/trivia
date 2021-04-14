import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(resp):
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        resp.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return resp

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    def pagination_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_questions = [q.format() for q in questions]
        return formatted_questions[start:end]

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

    # should do testing
    @app.route('/questions', methods=['GET', 'POST'])
    def questions():
        if request.method == 'GET':
            return get_questions(request)
        else:
            return post_questions(request)

    def get_questions(request):
        all_questions = Question.query.all()
        formatted_questions = pagination_questions(request, all_questions)
        all_category = Category.query.all()
        formatted_category = {c.id: c.type for c in all_category}

        return jsonify({
            "questions": formatted_questions,
            "total_questions": len(all_questions),
            "categories": formatted_category,
            "current_category": None
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(422)
        else:
            try:
                question.delete()
                return jsonify({"success": True}), 204
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

    def post_questions(request):
        body = request.get_json()
        if body['question'] == '' or body['answer'] == '':
            abort(422)
        else:
            try:
                new_question = Question(
                    question=body['question'],
                    answer=body['answer'],
                    category=body['category'],
                    difficulty=body['difficulty'],
                )
                new_question.insert()
                return jsonify({'success': True}), 201
            except:
                abort(422)

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
    def search_question():
        body = request.get_json()
        search_term = body['searchTerm']
        try:
            questions = Question.query.filter(Question.question.contains(search_term)).all()
            formatted_questions = pagination_questions(request, questions)
            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': None
            })
        except:
            abort(422)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories')
    def get_categories():
        categories = {c.id: c.type for c in Category.query.all()}
        return jsonify({"categories": categories})

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_by_category(category_id):
        questions_by_category = Question.query.filter(Question.category == category_id).all()
        formatted_questions = pagination_questions(request, questions_by_category)
        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(questions_by_category),
            'current_category': None
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        category = body['quiz_category']
        previous_question = body['previous_questions']
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category['id']).all()

        formatted_question = [q.format() for q in questions]
        filtered_question = filter_questions(formatted_question, previous_question)
        if len(filtered_question) == 0:
            return jsonify({'question': None})
        else:
            return jsonify({'question': random.choice(filtered_question)})

    def filter_questions(questions, prev):
        return list(filter(lambda x: (x['id'] not in prev), questions))

    # '''
    # @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422.
    # '''

    return app
