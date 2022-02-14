from django.urls import path
from .views import *

app_name = "members"

urlpatterns = [
    path("all-members/", all_members, name="all-members"),
    path("approve_kyc/<kyc_id>/", approve_kyc, name="approve_kyc"),
    path("approve_ad/<ad_id>/", approve_ad, name="approve_ad"),
]
