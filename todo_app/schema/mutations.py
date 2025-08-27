from todo_app.models import Task
import graphene
from .queries import TaskType
import graphql_jwt
from graphene_file_upload.scalars import Upload

class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        duedate = graphene.Date(required=True)
        document = Upload(required=False)

    task = graphene.Field(TaskType)
    ok = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, title, duedate, description=None,document=None):
        try:
            if not title.strip():
                return CreateTask(ok=False, message="Title cannot be empty.", task=None)

            task = Task.objects.create(
                title=title,
                description=description,
                due_date=duedate,
                document=document
            )
            return CreateTask(task=task, ok=True, message="Task created successfully.")
        except Exception as e:
            return CreateTask(ok=False, message=f"Error: {str(e)}", task=None)

class UpdateTask(graphene.Mutation):
    class Arguments:
        task_id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        duedate = graphene.Date()
    
    task = graphene.Field(TaskType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(root,info,task_id,title=None,description=None,duedate=None):
        task = Task.objects.get(id=task_id)
        if title:
            task.title = title
        if description:
            task.description = description
        if duedate:
            task.duedate = duedate
        task.save()
        return UpdateTask(task=task,ok=True,message="Task Updated Successfully")

class DeleteTask(graphene.Mutation):
    class Arguments:
        task_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(root,info,task_id):
        task = Task.objects.get(id=task_id).delete()
        return DeleteTask(ok=True,message="Task Deleted Successfully")



class TaskMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    deletetask = DeleteTask.Field()
    #Auth Mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()