import flask

blueprint = flask.Blueprint('news_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/news')
def get_news():
    return "Обработчик в news_api"


def main():
    db_session.global_init("db/blogs.sqlite")
    app.register_blueprint(news_api.blueprint)
    app.run()
