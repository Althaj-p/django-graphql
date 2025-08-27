from graphene_django import DjangoObjectType
from todo_app.models import *

class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = '__all__'