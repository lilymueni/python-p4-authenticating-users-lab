#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Resource to clear the session
class ClearSession(Resource):
    def delete(self):
        # Clear all session data
        session.clear()
        return {}, 204

# Resource to list all articles
class IndexArticle(Resource):
    def get(self):
        # Get all articles from the database and return them as a list of dictionaries
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

# Resource to show a single article and manage page views
class ShowArticle(Resource):
    def get(self, id):
        # Initialize page views if not already set
        session['page_views'] = session.get('page_views', 0)
        session['page_views'] += 1

        # Allow up to 3 page views
        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                return article.to_dict(), 200
            else:
                return {'message': 'Article not found'}, 404
        # Return an error if page views exceed the limit
        return {'message': 'Maximum pageview limit reached'}, 401

# Resource to handle user login
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            # Set the user_id in the session
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'message': 'User not found'}, 404

# Resource to handle user logout
class Logout(Resource):
    def delete(self):
        # Remove the user_id from the session
        session.pop('user_id', None)
        return {}, 204

# Resource to check the current session
class CheckSession(Resource):
    def get(self):
        # Get the user_id from the session
        user_id = session.get('user_id')
        if user_id:
            # Fetch the user using the new Session.get() method
            user = db.session.get(User, user_id)
            if user:
                return user.to_dict(), 200
            else:
                return {'message': 'User not found'}, 404
        # Return 401 if there is no user_id in the session
        return {}, 401

# Define the API routes
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
