import graphene
from graphene_django.debug import DjangoDebug

import users.schema
import aggregator.schema


class Query(users.schema.Query, aggregator.schema.Query):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    debug = graphene.Field(DjangoDebug, name='_debug')

    
class Mutation(users.schema.Mutation, aggregator.schema.Mutation, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    debug = graphene.Field(DjangoDebug, name='_debug')


schema = graphene.Schema(query=Query, mutation=Mutation, types=[])
