from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import logging
from logging.handlers import RotatingFileHandler

import datetime

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'title': 'test',
              'complete by': '11/17/2018',
              'completed': 'False',
              'completed on': '',
              'created on': '10/25/2018',
              'last_updated': ''}
}

"""Setting up logger"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(
    'file.log', mode='a', maxBytes=5*1024*1024, backupCount=2,
    encoding=None, delay=0)
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        logger.warning("Todo {} doesn't exist".format(todo_id))
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('complete by')
parser.add_argument('completed')

# Todo
# shows a single todo item and lets you delete a todo item


class Todo(Resource):
    """gets a todo item via id """

    @classmethod
    def get(cls, todo_id):
        logger.info('recieved get request')
        abort_if_todo_doesnt_exist(todo_id)
        # insert log
        return TODOS[todo_id]

    """deletes a todo item via id """

    @classmethod
    def delete(cls, todo_id):
        logger.info('recieved delete request')
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        logger.info('deleted {}'.format(todo_id))
        # insert log
        return '', 204

    """updates todos"""

    @classmethod
    def put(cls, todo_id):
        logger.info('recieved update request')
        args = parser.parse_args()
        todo = args.items()
        for k, v in todo:
            TODOS[todo_id][k] = v
        TODOS[todo_id]['last_updated'] = str(datetime.datetime.now())
        todo = {todo_id: TODOS[todo_id]}
        logger.info('updated {}'.format(todo))
        # insert log
        return todo, 200


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):

    @classmethod
    def get(cls):
        return TODOS

    @classmethod
    def add_todo(cls, fields):
        todo = fields
        todo['completed_on'] = None
        todo['created on'] = datetime.datetime.now().isoformat()
        todo['last_updated'] = None
        logger.info('fields: {}'.format(todo))
        return todo

    @classmethod
    def post(cls):
        logger.info('new todo requested')
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        fields = {
            'title': args['title'],
            'complete by': args['complete by'],
            'completed': args['completed']
        }
        TODOS[todo_id] = cls.add_todo(fields)
        logger.info('new Todo {} added'.format(TODOS[id]))
        return TODOS[todo_id], 201


# Actually setup the Api resource routing here


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)
