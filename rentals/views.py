from nis import cat
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
from django.http.response import JsonResponse
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
cat_base_url = f"{settings.CLIENT_BASE_URL}rental/cat/"


def overview(request):

    template = "rentals/index.html"

    context = {"page_title": "Homepage"}

    return render(request, template, context)


class Games(View):
    def get(self, request, *args, **kwargs):

        cats = requests.get(f"{cat_base_url}?timestamp={time.time()}")

        games = requests.get(f"{games_base_url}")
        print(games.json())

        template = "rentals/games.html"

        context = {
            "page_title": "Rental Games",
            "cats": cats.json(),
            "games": games.json(),
        }

        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        game_name = request.POST.get("game_name")
        displayImagePath = request.FILES["displayImagePath"]
        thumbnailImagePath = request.FILES["thumbnailImagePath"]
        bannerImagePath = request.FILES["bannerImagePath"]
        categoryId = request.POST.get("categoryId")
        numberInStock = request.POST.get("numberInStock")
        dailyRentalRate = request.POST.get("dailyRentalRate")
        dailyRentalRate = request.POST.get("dailyRentalRate")
        featured = request.POST.get("featured")

        catId = []
        for id in request.POST.getlist("categoryId"):
            catId.append(id)

        response_body = {
            "name": game_name,
            "catId": catId,
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
                "catId": catId,
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


class GameDetail(View):
    def get(self, request, item_id, *args, **kwargs):
        the_game = requests.get(f"{games_base_url}{item_id}")

        print(the_game.json())

        template = "rentals/rental_game_details.html"

        context = {
            "page_title": "Rental Games",
            "the_game": the_game.json(),
        }

        return render(self.request, template, context)

    def post(self, request, item_id, *args, **kwargs):

        the_item_id = request.POST.get("item_id")
        item_name = request.POST.get("item_name")
        numberInStock = request.POST.get("numberInStock")
        dailyRentalRate = request.POST.get("dailyRentalRate")
        featured = request.POST.get("featured")

        response_files = []
        response_body = {"id": the_item_id}

        if item_name:
            response_body.update({"name": item_name})
        if numberInStock:
            response_body.update({"numberInStock": numberInStock})
        if dailyRentalRate:
            response_body.update({"dailyRentalRate": dailyRentalRate})
        if featured:
            response_body.update({"featured": featured})

        if "displayImagePath" in request.FILES:
            response_files.append(
                ("displayImagePath", request.FILES["displayImagePath"].file)
            )
        if "thumbnailImagePath" in request.FILES:
            response_files.append(
                ("thumbnailImagePath", request.FILES["thumbnailImagePath"].file)
            )
        if "bannerImagePath" in request.FILES:
            response_files.append(
                ("bannerImagePath", request.FILES["bannerImagePath"].file)
            )

        print(response_files)
        print(response_body)

        response = requests.post(
            f"{games_base_url}update_rental_game/",
            data=response_body,
            files=response_files,
        )

        if response.status_code == 200:
            print("Game Edited")
            print(response.text)
            return redirect(
                reverse("rentals:game-details", kwargs={"item_id": item_id})
            )

        else:
            print(response.text)
            print("Error Editing Game")
            return redirect(
                reverse("rentals:game-details", kwargs={"item_id": item_id})
            )


class Platforms(View):
    def get(self, request, *args, **kwargs):
        platforms = requests.get(f"{cat_base_url}?timestamp={time.time()}")
        print(platforms.json())
        template = "rentals/platforms.html"
        context = {"page_title": "Games Categories", "platforms": platforms.json()}
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
            f"{cat_base_url}admin_create_cat/",
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
def rental_order_details(request, que_id):
    template = "rentals/order_details.html"
    que = requests.get(f"{settings.CLIENT_BASE_URL}rental/que/{que_id}")

    context = {"que": que.json()}
    return render(request, template, context)


@login_required
def delete_rental_item(request, item_id):
    data = {"id": item_id}
    item_del = requests.post(
        f"{games_base_url}admin_delete_item/",
        data=data,
    )
    if item_del.status_code == 200:
        print(item_del.text)
        print("Order Delivered")
        return redirect("rentals:games")
    else:
        print(item_del)
        print("There was a problem")
        return redirect("rentals:games")


@login_required
def delete_rental_category(request, item_id):
    data = {"catId": item_id}
    item_del = requests.post(
        f"{cat_base_url}admin_delete_cat/",
        data=data,
    )
    if item_del.status_code == 200:
        print(item_del.text)
        print("Category Delivered")
        return redirect("rentals:platforms")
    else:
        print(item_del)
        print("There was a problem")
        return redirect("rentals:platforms")


@login_required
def delete_multiple_items(request):
    data = json.loads(request.body)
    print(data)

    for id in data:
        data = {"id": id}
        requests.post(
            f"{games_base_url}admin_delete_item/",
            data=data,
        )

    return JsonResponse(
        data={"status": "all deleted"},
    )


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


class Trailers(View):
    def get(self, request, *args, **kwargs):

        platforms = requests.get(f"{platform_base_url}?timestamp={time.time()}")

        trailers = requests.get(f"{settings.CLIENT_BASE_URL}trailers")
        print(trailers.json())

        template = "rentals/trailers.html"

        context = {
            "page_title": "Trailers",
            "platforms": platforms.json(),
            "trailers": trailers.json(),
            "count": len(trailers.json()),
        }

        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        title = request.POST.get("title")
        yt_url = request.POST.get("yt_url")
        desc = request.POST.get("desc")
        trailerBanner = request.FILES["trailerBanner"]
        platformId = request.POST.get("platformId")

        response_body = {
            "name": name,
            "platformId": str(platformId).strip(),
            "yt_url": yt_url,
            "title": title,
        }

        if desc:
            response_body.update({"desc": desc})

        response_files = [("trailerBanner", trailerBanner.file)]

        response = requests.post(
            f"{settings.CLIENT_BASE_URL}trailers/admin_create_trailer/",
            data=response_body,
            files=response_files,
        )

        if response.status_code == 200:
            return redirect("rentals:trailers")
        else:
            return redirect("rentals:trailers")


@login_required
def delete_trailer(request, trailer_id):
    data = {"id": trailer_id}
    trailer_del = requests.post(
        f"{settings.CLIENT_BASE_URL}trailers/admin_delete_trailer/",
        data=data,
    )
    if trailer_del.status_code == 200:
        print(trailer_del.text)
        print("Trailer Deleted")
        return redirect("rentals:trailers")
    else:
        print(trailer_del)
        print("There was a problem")
        return redirect("rentals:trailers")
