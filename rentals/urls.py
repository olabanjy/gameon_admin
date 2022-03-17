from django.urls import path
from .views import *

from django.contrib.auth.decorators import login_required

app_name = "rentals"

urlpatterns = [
    # path("", overview, name="home"),
    path("", login_required(Games.as_view()), name="games"),
    path(
        "details/<item_id>/", login_required(GameDetail.as_view()), name="game-details"
    ),
    path("platforms/", login_required(Platforms.as_view()), name="platforms"),
    path("trailers/", login_required(Trailers.as_view()), name="trailers"),
    path("orders/", rental_orders, name="rental_orders"),
    path("que/<que_id>/", mark_que_as_delivered, name="mark_que_as_delivered"),
    path("delete-game/<item_id>/", delete_rental_item, name="delete_rental_item"),
    path("delete_multiple_items/", delete_multiple_items, name="delete_multiple_items"),
    path(
        "delete_trailer/<trailer_id>/",
        delete_multiple_items,
        name="delete_trailer",
    ),
]
