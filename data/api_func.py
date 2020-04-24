from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session, users, login_class, registration, redefine_roles, news, \
    translater, chatsform, settings_db, forum_db, settings_db, settings, forum, \
    answer_on_question, ask_question


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    new = session.query(forum_db.Forum).get(news_id)
    if not new:
        abort(404, message=f"Question {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        new = session.query(forum_db.Forum).get(news_id)
        return jsonify({'forum': new.to_dict(
            only=('id', 'title', 'question', 'theme', 'answers', 'user_id', 'date'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        new = session.query(forum_db.Forum).get(news_id)
        session.delete(new)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('question', required=True)
parser.add_argument('theme', required=True)
parser.add_argument('answers', required=True)
parser.add_argument('user_id', required=True)
parser.add_argument('date', required=True)


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        new = session.query(forum_db.Forum).all()
        return jsonify({'forum': [item.to_dict(
            only=('id', 'title', 'question', 'theme', 'answers', 'user_id', 'date')) for item in
            new]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        new = forum_db.Forum(
            id=args['id'],
            title=args['title'],
            question=args['question'],
            theme=args['theme'],
            answers=args['answers'],
            user_id=args['user_id'],
            date=args['date']
        )
        session.add(new)
        session.commit()
        return jsonify({'success': 'OK'})
