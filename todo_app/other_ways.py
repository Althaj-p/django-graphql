2. DjangoFormMutation

Uses a standard Django Form for validation.
You don’t handle validation manually – it’s inherited from the form.

# todo_app/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "document"]

# todo_app/schema/mutations.py
from graphene_django.forms.mutation import DjangoFormMutation
from todo_app.forms import TaskForm
from .types import TaskType

class TaskFormMutation(DjangoFormMutation):
    task = graphene.Field(TaskType)

    class Meta:
        form_class = TaskForm

    @classmethod
    def perform_mutate(cls, form, info):
        task = form.save()
        return cls(errors=[], task=task)

========================================
3. DjangoModelFormMutation

Shortcut version of DjangoFormMutation.
Automatically generates forms from the model.

# todo_app/schema/mutations.py
from graphene_django.forms.mutation import DjangoModelFormMutation
from todo_app.models import Task
from .types import TaskType

class TaskModelFormMutation(DjangoModelFormMutation):
    task = graphene.Field(TaskType)

    class Meta:
        model = Task
        fields = ("title", "description", "due_date", "document")

    @classmethod
    def perform_mutate(cls, form, info):
        task = form.save()
        return cls(errors=[], task=task)

=================================================
4. Serializer-based Mutation (DRF Serializer)

If you use Django REST Framework (DRF), you can reuse serializers for GraphQL.

# todo_app/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "due_date", "document"]

# todo_app/schema/mutations.py
from graphene import Mutation, Field
from .types import TaskType
from .serializers import TaskSerializer
from todo_app.models import Task

class TaskSerializerMutation(Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        duedate = graphene.Date()
        document = Upload(required=False)

    task = Field(TaskType)
    ok = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        serializer = TaskSerializer(data=kwargs)
        if serializer.is_valid():
            task = serializer.save()
            return cls(task=task, ok=True, message="Task created with serializer")
        return cls(ok=False, message=str(serializer.errors))