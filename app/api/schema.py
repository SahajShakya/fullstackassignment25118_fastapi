import strawberry
from app.api.user_schema import Query as UserQuery, Mutation as UserMutation
from app.api.store_schema import Query as StoreQuery, Mutation as StoreMutation
from app.api.widget_schema import WidgetQuery, WidgetMutation
from app.api.store_subscriptions import Subscription as StoreSubscription

@strawberry.type
class Query(UserQuery, StoreQuery, WidgetQuery):
    pass

@strawberry.type
class Mutation(UserMutation, StoreMutation, WidgetMutation):
    pass

@strawberry.type
class Subscription(StoreSubscription):
    pass

combined_schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
