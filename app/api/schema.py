import strawberry
from api.user_schema import Query as UserQuery, Mutation as UserMutation
from api.store_schema import Query as StoreQuery, Mutation as StoreMutation
from api.store_subscriptions import Subscription as StoreSubscription

@strawberry.type
class Query(UserQuery, StoreQuery):
    pass

@strawberry.type
class Mutation(UserMutation, StoreMutation):
    pass

@strawberry.type
class Subscription(StoreSubscription):
    pass

combined_schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
