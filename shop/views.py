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
import time
import requests
import json
from .models import *


items_base_url = f"{settings.CLIENT_BASE_URL}shop/items/"
platform_base_url = f"{settings.CLIENT_BASE_URL}shop/item/platform/"


class Items(View):
    def get(self, request, *args, **kwargs):

        platforms = requests.get(f"{platform_base_url}?timestamp={time.time()}")

        items = requests.get(f"{items_base_url}?timestamp={time.time()}")

        template = "shop/games.html"

        context = {
            "page_title": "Shop Items",
            "platforms": platforms.json(),
            "games": items.json(),
        }

        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        game_name = request.POST.get("game_name")
        displayImagePath = request.FILES["displayImagePath"]
        thumbnailImagePath = request.FILES["thumbnailImagePath"]
        bannerImagePath = request.FILES["bannerImagePath"]
        platformId = request.POST.get("platformId")
        numberInStock = request.POST.get("numberInStock")
        price = request.POST.get("price")
        discount_price = request.POST.get("discount_price")
        featured = request.POST.get("featured")

        response_body = {
            "name": game_name,
            "platformId": str(platformId).strip(),
            "numberInStock": numberInStock,
            "price": price,
            "featuredinput": featured,
        }
        if discount_price:
            response_body.update({"discount_price": discount_price})

        response_files = [
            ("displayImagePath", displayImagePath.file),
            ("thumbnailImagePath", thumbnailImagePath.file),
            ("bannerImagePath", bannerImagePath.file),
        ]

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
                "price": price,
                "featured": featured,
            }
        )

        response = requests.post(
            f"{items_base_url}admin_create_item/",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type},
        )
        if response.status_code == 200:
            return redirect("shop:games")
        else:
            return redirect("shop:games")


class ItemDetail(View):
    def get(self, request, item_id, *args, **kwargs):
        the_item = requests.get(f"{items_base_url}{item_id}")

        print(the_item.json())

        template = "shop/sale_items_details.html"

        context = {
            "page_title": "Shop Items",
            "the_game": the_item.json(),
        }

        return render(self.request, template, context)

    def post(self, request, item_id, *args, **kwargs):

        # displayImagePath = request.FILES["displayImagePath"]
        # thumbnailImagePath = request.FILES["thumbnailImagePath"]
        # bannerImagePath = request.FILES["bannerImagePath"]

        the_item_id = request.POST.get("item_id")
        item_name = request.POST.get("item_name")
        numberInStock = request.POST.get("numberInStock")
        price = request.POST.get("price")
        discount_price = request.POST.get("discount_price")
        featured = request.POST.get("featured")

        response_files = []
        response_body = {"id": the_item_id}

        if item_name:
            response_body.update({"name": item_name})
        if numberInStock:
            response_body.update({"numberInStock": numberInStock})
        if price:
            response_body.update({"price": price})

        if discount_price:
            response_body.update({"discount_price": discount_price})
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
            f"{items_base_url}update_shop_item/",
            data=response_body,
            files=response_files,
        )

        if response.status_code == 200:
            print("Item Edited")
            print(response.text)
            return redirect(reverse("shop:item-details", kwargs={"item_id": item_id}))

        else:
            print(response.text)
            print("Error Editing Game")
            return redirect(reverse("shop:item-details", kwargs={"item_id": item_id}))


class Platforms(View):
    def get(self, request, *args, **kwargs):
        platforms = requests.get(f"{platform_base_url}?timestamp={time.time()}")
        template = "shop/platforms.html"
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
        # response = requests.post(f"{platform_base_url}", json=response_data)
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
def shop_orders(request):
    template = "shop/shop_orders.html"
    orders = requests.get(
        f"{settings.CLIENT_BASE_URL}shop/item/order/?timestamp={time.time()}"
    )
    context = {"orders": orders.json()}
    return render(request, template, context)


@login_required
def shop_order_details(request, order_id):
    template = "shop/shop_order_details.html"
    order = requests.get(f"{settings.CLIENT_BASE_URL}shop/item/order/{order_id}")
    context = {"order": order.json()}
    return render(request, template, context)


@login_required
def mark_order_as_delivered(request, order_id):
    data = {"id": order_id}
    order_del = requests.post(
        f"{settings.CLIENT_BASE_URL}shop/item/order/mark_as_delivered/", data=data
    )
    if order_del.status_code == 200:
        return redirect("shop:shop_orders")
    else:
        return redirect("shop:shop_orders")


@login_required
def delete_shop_item(request, item_id):
    data = {"id": item_id}
    item_del = response = requests.post(
        f"{items_base_url}admin_delete_item/",
        data=data,
    )
    if item_del.status_code == 200:
        print(item_del.text)
        print("Item Deleted")
        return redirect("shop:games")
    else:
        print(item_del)
        print("There was a problem")
        return redirect("shop:games")


@login_required
def delete_multiple_shop_items(request):
    data = json.loads(request.body)
    print(data)

    for id in data:
        data = {"id": id}
        requests.post(
            f"{items_base_url}admin_delete_item/",
            data=data,
        )

    return JsonResponse(
        data={"status": "all deleted"},
    )
