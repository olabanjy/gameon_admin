from django import template
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Sum
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.encoding import force_bytes
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import time
import json
from .models import *


games_base_url = f"{settings.CLIENT_BASE_URL}rental/items/"
platform_base_url = f"{settings.CLIENT_BASE_URL}rental/platform/"


def overview(request):

    template = "rentals/index.html"

    context = {"page_title": "Homepage"}

    return render(request, template, context)


class Games(View):
    def get(self, request, *args, **kwargs):

        platforms = requests.get(f"{platform_base_url}?timestamp={time.time()}")

        games = requests.get(f"{games_base_url}")
        print(games.json())

        template = "rentals/games.html"

        context = {
            "page_title": "Rental Games",
            "platforms": platforms.json(),
            "games": games.json(),
        }

        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        game_name = request.POST.get("game_name")
        displayImagePath = request.FILES["displayImagePath"]
        thumbnailImagePath = request.FILES["thumbnailImagePath"]
        bannerImagePath = request.FILES["bannerImagePath"]
        platformId = request.POST.get("platformId")
        numberInStock = request.POST.get("numberInStock")
        dailyRentalRate = request.POST.get("dailyRentalRate")
        dailyRentalRate = request.POST.get("dailyRentalRate")
        featured = request.POST.get("featured")

        response_body = {
            "name": game_name,
            "platformId": str(platformId).strip(),
            "numberInStock": numberInStock,
            "dailyRentalRate": dailyRentalRate,
            "featuredinput": featured,
        }

        response_files = [
            ("displayImagePath", displayImagePath.file),
            ("thumbnailImagePath", thumbnailImagePath.file),
            ("bannerImagePath", bannerImagePath.file),
        ]
        print(response_files)

        test_url = "http://httpbin.org/post"

        multipart_data = MultipartEncoder(
            fields={
                "displayImagePath": (
                    displayImagePath.name,
                    displayImagePath.file,
                    "image/jpeg",
                ),
                "thumbnailImagePath": (
                    thumbnailImagePath.name,
                    thumbnailImagePath.file,
                    "image/jpeg",
                ),
                "bannerImagePath": (
                    bannerImagePath.name,
                    bannerImagePath.file,
                    "image/jpeg",
                ),
                # plain text fields
                "name": game_name,
                "platformId": str(platformId).strip(),
                "numberInStock": numberInStock,
                "dailyRentalRate": dailyRentalRate,
                "featured": featured,
            }
        )

        response = requests.post(
            f"{games_base_url}admin_create_item/",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
        )
        if response.status_code == 200:
            print("Platform added")
            print(response.text)
            return redirect("rentals:games")
        else:
            print(response.text)
            print("Error Adding platform")
            return redirect("rentals:games")


class Platforms(View):
    def get(self, request, *args, **kwargs):
        platforms = requests.get(f"{platform_base_url}?timestamp={time.time()}")
        template = "rentals/platforms.html"
        context = {"page_title": "Games Platforms", "platforms": platforms.json()}
        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        platform_name = request.POST.get("platform_name")
        platform_slug = request.POST.get("platform_slug")
        iconImagePath = request.FILES["iconImagePath"]
        response_data = {"name": platform_name, "slug": platform_slug}
        response_files = {"iconImagePath": iconImagePath.file}
        multipart_data = MultipartEncoder(
            fields={
                "iconImagePath": (iconImagePath.name, iconImagePath.file, "image/jpeg"),
                "name": platform_name,
                "slug": platform_slug,
            }
        )
        response = requests.post(
            f"{platform_base_url}admin_create_plat/",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
        )
        if response.status_code == 200:
            return redirect("rentals:platforms")
        else:
            return redirect("rentals:platforms")


@login_required
def rental_orders(request):
    template = "rentals/rental_orders.html"
    que = requests.get(f"{settings.CLIENT_BASE_URL}rental/que/?timestamp={time.time()}")
    context = {"ques": que.json()}
    return render(request, template, context)


@login_required
def mark_que_as_delivered(request, que_id):
    data = {"id": que_id}
    que_del = requests.post(
        f"{settings.CLIENT_BASE_URL}rental/que/mark_as_delivered/", data=data
    )
    if que_del.status_code == 200:
        print(que_del.text)
        print("Order Delivered")
        return redirect("rentals:rental_orders")
    else:
        print(que_del)
        print("There was a problem")
        return redirect("rentals:rental_orders")