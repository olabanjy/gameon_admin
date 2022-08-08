from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("rentals.urls", namespace="rentals")),
    path("shop/", include("shop.urls", namespace="shop")),
    path("members/", include("members.urls", namespace="members")),
    path("vendors/", include("vendors.urls", namespace="vendors")),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
