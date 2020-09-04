import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_results(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in questions]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

# TODO: Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

# TODO: Use the after_request decorator to set Access-Control-Allow

    @app.after_request
    def after_request(response):
        # list of http request header values the server will allow
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        # list of HTTP request types allowed
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # TODO: Create an endpoint to handle GET requests for questions,
    #       including pagination (every 10 questions).
    #       This endpoint should return a list of questions,
    #       number of total questions, current category, categories.

    @app.route('/questions')
    def all_questions():
        questions = Question.query.order_by(Question.id).all()
        results = paginate_results(request, questions)

        if len(results) == 0:
            abort(404)

        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'questions': results,
            'total_questions': len(Question.query.all()),
            'categories': formatted_categories,
            'current_category': None
        })

    # TODO: Create an endpoint to handle GET requests
    # for all available categories.

    @app.route('/categories')
    def all_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(categories)
        })

    # TODO: Create an endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).first()
        try:
            question.delete()

            return jsonify({
                'success': True,
                'id': question_id
            })

        except Exception:
            abort(422)

    # TODO: Create an endpoint to POST a new question,
    #       which will require the question and answer text,
    #       category, and difficulty score.

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json(request)
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')
        if (new_question == '' or new_answer == '' or
            new_category == '' or
                new_difficulty == ''):
            abort(400)
        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id
            })
        except Exception:
            abort(422)

    # TODO: Create a POST endpoint to get questions based on a search term.
    #       It should return any questions for whom the search term
    #       is a substring of the question.
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('search_term', None)

        questions_results = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()

        search_question = [question.format()
            for question in  questions_results]

        return jsonify({
            'success': True,
            'questions': search_question,
            'current_category': None
        })

    # TODO: Create a GET endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def getByCategory(category_id):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]
        if formatted_questions is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })

    # TODO: Create a POST endpoint to get questions to play the quiz.
    #       This endpoint should take category and previous question parameters
    #       and return a random questions within the given category,
    #       if provided, and that is not one of the previous questions.

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        previous_questions = body['previous_questions']
        category = body['quiz_category']

        body = request.get_json()
        previous_questions = body['previous_questions']
        category = body['quiz_category']
        category_id = len(previous_questions)

        if category_id is None:
            abort(404)

        try:
            questions = Question.query
            if category != 0:
                questions = Question.query.filter(
                    Question.category == category)
            else:
                questions = questions.all()
            next_question = questions[category_id]
            if category_id == questions:
                return jsonify({
                    'success': True,
                    'question': None,
                })

            while next_question in previous_questions:
                random_question = questions[category_id]

            return jsonify({
                'success': True,
                'question': next_question.format(),
            })

        except:
            abort(422)

    # TODO: Create error handlers for all expected errors
    #       including 404 and 422.
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
            }), 400

    return app