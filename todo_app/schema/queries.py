from graphene import ObjectType,List,Field,Int
from todo_app.schema.types import TaskType
from todo_app.models import Task
from graphql_jwt.decorators import login_required

class TodoQuery(ObjectType):
    all_tasks = List(TaskType)
    view_task = Field(TaskType,task_id=Int())
    
    @login_required
    def resolve_all_tasks(root,info):
        print(info.context.user,'user')
        return Task.objects.all()
    
    def resolve_view_task(root,info,task_id):
        return Task.objects.get(id=task_id)