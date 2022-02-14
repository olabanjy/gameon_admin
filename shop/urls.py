from django.urls import path
from .views import *

from django.contrib.auth.decorators import login_required

app_name = "shop"

urlpatterns = [
    path("items/", login_required(Items.as_view()), name="games"),
    path("platforms/", login_required(Platforms.as_view()), name="platforms"),
    path("orders/", shop_orders, name="shop_orders"),
    path("orders/<order_id>/", mark_order_as_delivered, name="mark_order_as_delivered"),
]
