# import graphene
# from graphene_django import DjangoObjectType

# from .models import Category, Ingredient

# class CategoryType(DjangoObjectType):
#     class Meta:
#         model = Category
#         fields = ("id", "name", "ingredients")

# class IngredientType(DjangoObjectType):
#     class Meta:
#         model = Ingredient
#         fields = ("id", "name", "notes", "category")

# class Query(graphene.ObjectType):
#     all_ingredients = graphene.List(IngredientType)
#     category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

#     def resolve_all_ingredients(root, info):
#         # We can easily optimize query count in the resolve method
#         return Ingredient.objects.select_related("category").all()

#     def resolve_category_by_name(root, info, name):
#         try:
#             return Category.objects.get(name=name)
#         except Category.DoesNotExist:
#             return None

# schema = graphene.Schema(query=Query)

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from .models import Category, Ingredient
from django import forms

# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        interfaces = (relay.Node, )
    new_Field = graphene.String()
    def resolve_new_Field(self,info):
        return info.context.user
        
    @classmethod
    def get_queryset(cls,queryset,info):
        if info.context.user.is_anonymous:
            return queryset.filter(name='Milk')
        return queryset


class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        interfaces = (relay.Node, )

class CategoryConnection(relay.Connection):
    class Meta:
        node = CategoryNode

class Query(ObjectType):
    category = relay.Node.Field(CategoryNode)
    # all_categories = DjangoFilterConnectionField(CategoryNode)
    all_categories = relay.ConnectionField(CategoryConnection)
    # questions = relay.ConnectionField(QuestionConnection)

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

    def resolve_all_categories(root,info):
        return Category.objects.all()

# class QuestionConnection(relay.Connection):
#     total_count = graphene.Int()

#     class Meta:
#         node = QuestionType

#     def resolve_total_count(root, info):
#         return len(root.iterable)

# =====================-----------------Mutations------------=============================
# class CategoryMutation(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#     category = graphene.Field(CategoryNode)
#     success = graphene.Boolean()
#     message = graphene.String()

#     # @classmethod
#     # def mutate(cls,root,info,name):
#     #     obj = Category.objects.create(name=name)
#     #     return CategoryMutation(category = obj)
#     @classmethod
#     def mutate(cls, root, info, name):
#         if not name.strip():
#             return CategoryMutation(success=False, message="Name cannot be empty")
#         if Category.objects.filter(name__iexact=name).exists():
#             return CategoryMutation(success=False, message=f"Category {name} already exists")

#         obj = Category.objects.create(name=name)
#         return CategoryMutation(category=obj, success=True, message="Category created")


# from graphene_django.forms.mutation import DjangoFormMutation
    
from graphene_django.forms.mutation import DjangoModelFormMutation

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    # def clean_name(self):
    #     name = self.cleaned_data.get("name", "").strip()
    #     if not name:
    #         raise forms.ValidationError("Name cannot be empty")
    #     if Category.objects.filter(name__iexact=name).exists():
    #         raise forms.ValidationError(f"Category '{name}' already exists")
    #     return name

# class CategoryMutation(DjangoModelFormMutation):
#     class Meta:
#         form_class = CategoryForm

class ErrorType(graphene.ObjectType):
    field = graphene.String()
    messages = graphene.List(graphene.String)

# class CategoryMutation(DjangoModelFormMutation):
#     errors = graphene.List(ErrorType)
#     category = graphene.Field(lambda: CategoryNode)

#     class Meta:
#         form_class = CategoryForm

#     @classmethod
#     def perform_mutate(cls, form, info):
#         if form.is_valid():
#             category = form.save(commit=False)
#             category.save()
#             return cls(category=category, errors=[])
#         else:
#             errors = [
#                 ErrorType(field=field, messages=messages)
#                 for field, messages in form.errors.items()
#             ]
#             return cls(errors=errors, category=None)
class CategoryMutation(DjangoModelFormMutation):
    errors = graphene.List(ErrorType)
    category = graphene.Field(lambda: CategoryNode)

    class Meta:
        form_class = CategoryForm  # ✅ still required to bind input to model fields

    @classmethod
    def perform_mutate(cls, form, info):
        name = form.data.get('name', '').strip()

        # ✅ Custom mutation-level validations
        if not name:
            return cls(
                errors=[ErrorType(field='name', messages=["Name cannot be empty"])],
                category=None,
            )
        if Category.objects.filter(name__iexact=name).exists():
            return cls(
                errors=[ErrorType(field='name', messages=[f"Category '{name}' already exists"])],
                category=None,
            )

        # ✅ Create and return object
        category = form.save(commit=False)
        category.save()
        return cls(category=category, errors=[])


class Mutation(ObjectType):
    create_category = CategoryMutation.Field()