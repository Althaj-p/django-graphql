import graphene

import graphql_api.schema
from todo_app.schema.queries import TodoQuery
from todo_app.schema.mutations import TaskMutation


class Query(graphql_api.schema.Query,TodoQuery, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass
    
class Mutation(graphql_api.schema.Mutation,TaskMutation,graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query,mutation=Mutation)