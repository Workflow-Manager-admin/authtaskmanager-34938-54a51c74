from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..models import db, Task
from .auth import token_required
from marshmallow import Schema, fields

blp = Blueprint(
    "Tasks",
    __name__,
    url_prefix="/tasks",
    description="Task management routes"
)


class TaskSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String()
    completed = fields.Boolean()
    user_id = fields.Integer(dump_only=True)


class TaskUpdateSchema(Schema):
    title = fields.String()
    description = fields.String()
    completed = fields.Boolean()


# PUBLIC_INTERFACE
@blp.route("/")
class TaskList(MethodView):
    """Retrieve list of tasks, or create a new task (for the authenticated user)."""
    @blp.response(200, TaskSchema(many=True))
    @token_required
    def get(current_user, self):
        """Get the authenticated user's tasks."""
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return tasks

    @blp.arguments(TaskSchema)
    @blp.response(201, TaskSchema)
    @token_required
    def post(current_user, self, task_data):
        """Create a task for the authenticated user."""
        task = Task(
            title=task_data["title"],
            description=task_data.get("description", ""),
            user_id=current_user.id,
            completed=task_data.get("completed", False)
        )
        db.session.add(task)
        db.session.commit()
        return task


# PUBLIC_INTERFACE
@blp.route("/<int:task_id>")
class TaskDetail(MethodView):
    """Retrieve, update, or delete an individual task by id."""
    @blp.response(200, TaskSchema)
    @token_required
    def get(current_user, self, task_id):
        """Get a specific user's task."""
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Task not found.")
        return task

    @blp.arguments(TaskUpdateSchema)
    @blp.response(200, TaskSchema)
    @token_required
    def put(current_user, self, task_data, task_id):
        """Edit a user's task."""
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Task not found.")
        if "title" in task_data:
            task.title = task_data["title"]
        if "description" in task_data:
            task.description = task_data["description"]
        if "completed" in task_data:
            task.completed = task_data["completed"]
        db.session.commit()
        return task

    @blp.response(204)
    @token_required
    def delete(current_user, self, task_id):
        """Delete a user's task."""
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Task not found.")
        db.session.delete(task)
        db.session.commit()
        return ""


# PUBLIC_INTERFACE
@blp.route("/<int:task_id>/complete")
class TaskComplete(MethodView):
    """Mark a task as completed."""
    @blp.response(200, TaskSchema)
    @token_required
    def post(current_user, self, task_id):
        """Mark a user's task as completed."""
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            abort(404, message="Task not found.")
        task.completed = True
        db.session.commit()
        return task
