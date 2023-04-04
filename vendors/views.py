from multiprocessing import context
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
from datetime import datetime


vendor_base_url = f"{settings.VENDOR_BASE_URL}api/v1/vendors"

ts = time.time()


def all_vendors(request):

    template = "vendors/all_vendors.html"

    all_vendors = requests.get(f"{vendor_base_url}/get_all_users/?timestamp={ts}")

    print(all_vendors.json())

    context = {"all_vendors": all_vendors.json()}

    return render(request, template, context)


def get_vendor_details(request, user_email):

    template = "vendors/vendor_details.html"

    the_res = requests.post(
        f"{vendor_base_url}/get_user_details/", data={"email": user_email}
    )
    print(the_res.json())

    context = {"user": the_res.json()}

    return render(request, template, context)


def approve_kyc(request, kyc_id):
    the_res = requests.post(f"{vendor_base_url}/approve_kyc/", data={"kyc_id": kyc_id})
    print(the_res.json())
    if the_res.status_code == 200:
        print("KYC approved")
    return redirect("vendors:all-vendors")


class Items(View):
    def get(self, request, *args, **kwargs):
        curr_date = datetime.now()

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/shop/items/"

        items = requests.get(f"{items_base_url}get_list/?timestamp={curr_date}")
        print(items.json())

        template = "vendors/vendor_items.html"

        context = {
            "page_title": "Approve Vendor Items",
            "items": items.json(),
        }

        return render(self.request, template, context)


class ItemDetail(View):
    def get(self, request, item_id, *args, **kwargs):

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/shop/items/"
        the_item = requests.get(f"{items_base_url}{item_id}")

        print(the_item.json())

        template = "vendors/vendor_item_details.html"

        context = {
            "page_title": "Vendor Item Details",
            "the_game": the_item.json(),
        }

        return render(self.request, template, context)


# @login_required
def approve_item(request, item_id):

    try:
        # first get the item
        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/shop/items/"
        the_item = requests.get(f"{items_base_url}{item_id}").json()
        print("the_item", the_item)
        # create new item to client end
        client_items_base_url = f"{settings.CLIENT_BASE_URL}shop/items/"
        # admin_vendor_create_item
        sendBody = {
            "name": the_item["name"],
            "catName": the_item["cat"],
            "numberInStock": the_item["numberInStock"],
            "price": the_item["price"],
            "vendor_code": the_item["vendor"]["vendor_code"],
            # "vendor_long": the_item["vendor"]["addressObject"]["long"],
            # "vendor_lat": the_item["vendor"]["addressObject"]["lat"],
            "displayImagePath": the_item["displayImagePath"],
            "bannerImagePath": the_item["bannerImagePath"],
            "thumbnailImagePath": the_item["thumbnailImagePath"],
        }
        if the_item["discount_price"]:
            sendBody.update({"discount_price": the_item["discount_price"]})

        if the_item["desc"]:
            sendBody.update({"desc": the_item["desc"]})

        if (
            the_item["vendor"]["addressObject"]["long"]
            and the_item["vendor"]["addressObject"]["long"] != None
        ):
            sendBody.update(
                {"vendor_long": the_item["vendor"]["addressObject"]["long"]}
            )

        if (
            the_item["vendor"]["addressObject"]["lat"]
            and the_item["vendor"]["addressObject"]["lat"] != None
        ):
            sendBody.update({"vendor_lat": the_item["vendor"]["addressObject"]["lat"]})

        if the_item["vendor"]["shop_name"] == None:
            sendBody.update(
                {
                    "vendor": f"{the_item['vendor']['first_name']}{the_item['vendor']['last_name']}"
                }
            )
        else:
            sendBody.update({"vendor": the_item["vendor"]["shop_name"]})

        print(sendBody)

        sendResponse = requests.post(
            f"{client_items_base_url}admin_vendor_create_item/",
            data=sendBody,
        )
        if sendResponse.status_code == 200:
            approval_data = {"id": item_id}
            item_approval = requests.post(
                f"{items_base_url}approve_item/",
                data=approval_data,
            )
            print(item_approval)
            return redirect("vendors:vendor-items")
        else:
            print("there was a problem")
            return redirect("vendors:vendor-items")

    except Exception as e:
        print(e)
        return redirect("vendors:vendor-items")


# @login_required
def reject_item(request, item_id):
    try:
        reject_data = {"id": item_id}

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/shop/items/"
        item_rejection = requests.post(
            f"{items_base_url}reject_item/",
            data=reject_data,
        )
        if item_rejection.status_code == 200:
            print("item removed")
            return redirect("vendors:vendor-items")
        else:
            print("there was a problem")
            return redirect("vendors:vendor-items")

    except Exception as e:
        print(e)
        return redirect("vendors:vendor-items")


class RentalGame(View):
    def get(self, request, *args, **kwargs):

        curr_date = datetime.now()

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/rental/items/"

        items = requests.get(f"{items_base_url}get_list/?timestamp={curr_date}")

        template = "vendors/rental_vendor_items.html"

        context = {
            "page_title": "Approve Vendor Rental Games",
            "items": items.json(),
        }

        return render(self.request, template, context)


class RentalGameDetail(View):
    def get(self, request, item_id, *args, **kwargs):

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/rental/items/"
        the_item = requests.get(f"{items_base_url}{item_id}")

        # print(the_item.json())

        template = "vendors/rental_vendor_item_details.html"

        context = {
            "page_title": "Vendor Rental Item Details",
            "the_game": the_item.json(),
        }

        return render(self.request, template, context)


# @login_required
def approve_rental_item(request, item_id):

    try:
        # first get the item
        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/rental/items/"
        the_item = requests.get(f"{items_base_url}{item_id}").json()
        # print("the_item", the_item)
        # create new item to client end
        client_items_base_url = f"{settings.CLIENT_BASE_URL}rental/items/"
        # admin_vendor_create_item
        sendBody = {
            "name": the_item["name"],
            "catName": the_item["cat"],
            "numberInStock": the_item["numberInStock"],
            "dailyRentalRate": the_item["dailyRentalRate"],
            "vendor_code": the_item["vendor"]["vendor_code"],
            "displayImagePath": the_item["displayImagePath"],
            "bannerImagePath": the_item["bannerImagePath"],
            "thumbnailImagePath": the_item["thumbnailImagePath"],
        }

        if the_item["desc"]:
            sendBody.update({"desc": the_item["desc"]})

        if the_item["vendor"]["shop_name"] == None:
            sendBody.update(
                {
                    "vendor": f"{the_item['vendor']['first_name']}{the_item['vendor']['last_name']}"
                }
            )
        else:
            sendBody.update({"vendor": the_item["vendor"]["shop_name"]})

        if (
            the_item["vendor"]["addressObject"]["long"]
            and the_item["vendor"]["addressObject"]["long"] != None
        ):
            sendBody.update(
                {"vendor_long": the_item["vendor"]["addressObject"]["long"]}
            )

        if (
            the_item["vendor"]["addressObject"]["lat"]
            and the_item["vendor"]["addressObject"]["lat"] != None
        ):
            sendBody.update({"vendor_lat": the_item["vendor"]["addressObject"]["lat"]})

        print("sendbody here ", sendBody)

        sendResponse = requests.post(
            f"{client_items_base_url}admin_vendor_create_item/",
            data=sendBody,
        )
        if sendResponse.status_code == 200:
            approval_data = {"id": item_id}
            item_approval = requests.post(
                f"{items_base_url}approve_item/",
                data=approval_data,
            )
            print(item_approval)
            return redirect("vendors:rental-vendor-items")
        else:
            print("there was a problem")
            return redirect("vendors:rental-vendor-items")

    except Exception as e:
        print(e)
        return redirect("vendors:rental-vendor-items")


# @login_required
def reject_rental_item(request, item_id):
    try:
        reject_data = {"id": item_id}

        items_base_url = f"{settings.VENDOR_BASE_URL}api/v1/rental/items/"
        item_rejection = requests.post(
            f"{items_base_url}reject_item/",
            data=reject_data,
        )
        if item_rejection.status_code == 200:
            print("item removed")
            return redirect("vendors:rental-vendor-items")
        else:
            print("there was a problem")
            return redirect("vendors:rental-vendor-items")

    except Exception as e:
        print(e)
        return redirect("vendors:rental-vendor-items")
