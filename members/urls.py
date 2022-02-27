from django.urls import path
from .views import *

app_name = "members"

urlpatterns = [
    path("all-members/", all_members, name="all-members"),
    path("approve_kyc/<kyc_id>/<user_email>/", approve_kyc, name="approve_kyc"),
    path("approve_ad/<ad_id>/<user_email>/", approve_ad, name="approve_ad"),
    path("get_user_details/<user_email>/", get_user_details, name="get_user_details"),
]
