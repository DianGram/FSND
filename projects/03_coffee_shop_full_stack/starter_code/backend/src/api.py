import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]

        if not drinks:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except Exception:
        # print('Error:', sys.exc_info())
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]

        if not drinks:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except Exception:
        # print('Error:', sys.exc_info())
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(token):
    body = request.get_json()
    if not body:
        abort(400)
    title = body.get('title', '')
    recipe = body.get('recipe', None)
    if recipe:
        try:
            new_drink = Drink(title=title, recipe=json.dumps(recipe))
            new_drink.insert()
            return jsonify({
                'success': True,
                'drinks': [{'id': new_drink.id,
                            'title': new_drink.title,
                            'recipe': new_drink.recipe
                            }]
            })
        except Exception as e:
            # print('error', e.args)
            abort(422)
    else:
        abort(400)


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def udpate_drink(token, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    data = request.get_json()
    if not data:
        abort(400)
    drink.title = data.get('title', drink.title)
    recipe = data.get('recipe', drink.recipe)
    drink.recipe = json.dumps(recipe)

    try:
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        print('Error:', sys.exc_info())
        abort(422)


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 'Authentication Error',
        "message": error.error['description']
    }), 401
