from flask import Flask

from flask_restful import Resource,Api ,reqparse,abort ,fields, marshal_with

from flask_sqlalchemy import SQLAlchemy


app =Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


class ToDOModel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String)
    summary = db.Column(db.String)

# todos = {
#     1: {"task": "Task1", "summary" : "Task1 Summary"},
#     2: {"task": "Task2", "summary" : "Task2 Summary"},
#     3: {"task": "Task3", "summary" : "Task3 Summary"}
# }

#body of the request has to be contianing task,and summary only and we want to make sure the format is
#always like the abvoe (in json fromat, and task and summary keys ) i.e we want flask to know the data we r sending to server
# so we need to parse the data , for that we need reqparse

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task",type=str, help = 'Task is required', required = True)
task_post_args.add_argument("summary",type=str, help = 'Summary is required', required = True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task",type=str)
task_put_args.add_argument("summary",type=str)

#without this fileds we will get a error
# <title>TypeError: Object of type ToDOModel is not JSON serializable // Werkzeug Debugger</title>
# so whever data we r  retruning from the db , it has to be serialisable i.e in dict format how does api will come to know means we annotate the fucntin
# with marshal
resource_fields = {
   'id': fields.Integer,
    'task' : fields.String,
    'summary' : fields.String,

}

class ToDo(Resource):

    @marshal_with(resource_fields) #--->wihtoug this the error is

    # TypeError: Object of type ToDOModel is not JSON serializable in the console and hte below error is in Postman

    # < title > TypeError: Object of type ToDOModel is not JSON serializable // Werkzeug Debugger < / title >
    def get(self,todo_id):
        # this is the code with the "todos dict" not database
        # return todos[todo_id]
        task = ToDOModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404,message="could not find the task with that id")
        else:
            return task

    @marshal_with(resource_fields)
    def post(self,todo_id):
        # this is the code with the "todos dict" ,i.e without the  database
        # args = task_post_args.parse_args()
        # if todo_id in todos:
        #     abort(409,"Task id already exists")
        # else:
        #     todos[todo_id] = {"task":args["task"],"summary":args["summary"]}
        # return todos
        args = task_post_args.parse_args()
        task = ToDOModel.query.filter_by(id = todo_id).first()
        if task:
            abort(409,message="task id already exists")
        else:
            todo = ToDOModel(id=todo_id,task=args['task'],summary=args['summary'])
            db.session.add(todo)
            db.session.commit()
            return todo, 201

    @marshal_with(resource_fields)
    def put(self,todo_id):
        args = task_put_args.parse_args()
        # this is the code with the "todos dict" i.e without database
        # if todo_id not in todos:
        #     abort(404,message= "Task does not exist,cant update")
        # # if todo_id in todos:
        # #     todos[todo_id] = {"task":args["task"],"summary":args["summary"]}
        # if args["task"]:
        #     todos[todo_id]["task"] = args["task"]
        # if args["summary"]:
        #     todos[todo_id]["summary"] = args["summary"]
        # return todos[todo_id]

        task = ToDOModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(409, message = "task with the respective is is not present")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task

    def delete(self,todo_id):

        # this is the code with the "todos dict" i.e without database
        # if todo_id in todos:
        #     deleted = todos.pop(todo_id,None)
        # return deleted
        task = ToDOModel.query.filter_by(id=todo_id).first()
        print(task)
        if not task:
            print("in fi block")
            abort(409,message = "resprective task id record does not exist")
        else:
            print("else block")
            db.session.delete(task)
            db.session.commit()
            return 'ToDoDeleted'

class ToDoList(Resource):

    # approach1 with marshall
    # @marshal_with(resource_fields)
    # def get(self):
    #     # this is the code with the "todos dict" not database
    #     # return todos
    #     tasks = ToDOModel.query.all()
    #     return tasks

    #approach 2

    def get(self):
        tasks = ToDOModel.query.all()
        todo = {}
        for task in tasks:
            todo[task.id] = {"task": task.task , "summary":task.summary}
        return todo

api.add_resource(ToDo,"/todos/<int:todo_id>")
api.add_resource(ToDoList,"/todos")#entire data it will be retrieving to the user

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)