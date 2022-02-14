from django.urls import path
from .views import *

from django.contrib.auth.decorators import login_required

app_name = "rentals"

urlpatterns = [
    # path("", overview, name="home"),
    path("", login_required(Games.as_view()), name="games"),
    path("platforms/", login_required(Platforms.as_view()), name="platforms"),
    path("orders/", rental_orders, name="rental_orders"),
    path("que/<que_id>/", mark_que_as_delivered, name="mark_que_as_delivered"),
]
