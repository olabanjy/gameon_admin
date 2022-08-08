from django.urls import path
from .views import *

app_name = "vendors"

urlpatterns = [
    path("all-vendors/", all_vendors, name="all-vendors"),
    path("approve_kyc/<kyc_id>/", approve_kyc, name="approve_kyc"),
    path("get_user_details/<user_email>/", get_vendor_details, name="get_user_details"),
    path("vendor-items/", Items.as_view(), name="vendor-items"),
    path("details/<item_id>/", ItemDetail.as_view(), name="item-details"),
    path("rental-vendor-items/", RentalGame.as_view(), name="rental-vendor-items"),
    path(
        "rental-details/<item_id>/",
        RentalGameDetail.as_view(),
        name="rental-item-details",
    ),
    path("approve-item/<item_id>/", approve_item, name="approve-item"),
    path("reject-item/<item_id>/", reject_item, name="reject-item"),
    path(
        "approve-rental-item/<item_id>/",
        approve_rental_item,
        name="approve-rental-item",
    ),
    path(
        "reject-rental-item/<item_id>/", reject_rental_item, name="reject-rental-item"
    ),
]
