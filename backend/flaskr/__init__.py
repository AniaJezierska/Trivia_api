import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random   

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10          

def paginate_questions(request, selection):  
  page = request.args.get('page', 1, type=int)     
  start =  (page - 1) * QUESTIONS_PER_PAGE      
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
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
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      # list of HTTP request types allowed
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      
      return response  

# TODO: Create an endpoint to handle GET requests for all available categories.

  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categoriesDict = {}  

    for category in categories:
        categoriesDict[category.id] = category.type

    if (len(categoriesDict) == 0):
       abort(404)

    return jsonify({
        'success': True,
        'categories': categoriesDict
    })


# TODO: Create an endpoint to handle GET requests for questions, 
#       including pagination (every 10 questions). 
#       This endpoint should return a list of questions, 
#       number of total questions, current category, categories.  

  @app.route('/questions')
  def get_questions(): 
      selection = Question.query.all()
      total_questions = len(selection)
      current_questions = paginate_questions(request, selection)

      categories = Category.query.all()
      categoriesDict = {}

      for category in categories:
          categoriesDict[category.id] = category.type

      if (len(current_questions) == 0):
          abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': total_questions,
          'categories': categoriesDict
      })         


# TODO: Create an endpoint to DELETE question using a question ID. 

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(question_id): 
      
      try:
          question = Question.query.filter_by(id=id).one_or_none()

          if question is None:
            abort(404)

          question.delete()

          return jsonify({
              'success': True,
              'deleted': id
          })

      except:
          abort(422)


# TODO: Create an endpoint to POST a new question, 
#       which will require the question and answer text, 
#       category, and difficulty score.

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()  

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)    

    try: 
        question = Question(question=new_question, 
                            answer=new_answer, 
                            difficulty=new_difficulty, 
                            category=new_category)
        question.insert()

        selection = Question.query.order_by(Question.id).all()

        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'created': question.id,
            'question_created': question.question,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })
        
    except Exception:
      abort(422)    
            
    
# TODO: Create a POST endpoint to get questions based on a search term. 
#       It should return any questions for whom the search term 
#       is a substring of the question. 

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
               
    try:
        selection = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        if (len(selection) == 0):
            abort(404)

        paginated = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all())
        })     
        
    except Exception:
        abort(422)       
     

# TODO: Create a GET endpoint to get questions based on category. 

  @app.route('/categories/<int:id>/questions')
  def questions_by_category(id):
    category = Category.query.filter_by(id=id).one_or_none()

    try:
        selection = Question.query.filter_by(category=category_id).all()

        if category is None:     
          abort(404)  

        paginated = paginate_questions(request, selection)
    
        return jsonify({
            'success': True,   
            'questions': paginated,
            'total_questions': len(Question.query.all()),  
            'current_category': Category.type          
        })

    except Exception:
        abort(422)      
    

# TODO: Create a POST endpoint to get questions to play the quiz. 
#       This endpoint should take category and previous question parameters 
#       and return a random questions within the given category, 
#       if provided, and that is not one of the previous questions. 

  @app.route('/quizzes', methods=['POST'])
  def get_quize():
      body = request.get_json()
      previous_questions = body.get('previous_questions')   
      category = body.get('quiz_category')

      try:
        questions = Question.query.order_by(Question.id)

        if (category['id'] == 0):                                               
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all

        random_question = random.choice(questions)
          
        if len(previous_questions) == len(questions):
          
          return jsonify({       
            'success': True,             
            'question': None
          })              
      
        while random_question.id in previous_questions:
          random_question = random.choice(questions)

        return jsonify({
          'success': True,
          'question': random_question.format()
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

 
  


       
