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


mamber_base_url = f"{settings.CLIENT_BASE_URL}users"

ts = time.time()


def all_members(request):

    template = "members/all_users.html"

    all_members = requests.get(f"{mamber_base_url}/get_all_users?timestamp={ts}")

    print(all_members.json())

    context = {"all_members": all_members.json()}

    return render(request, template, context)


def get_user_details(request, user_email):

    template = "members/user_detail.html"

    the_res = requests.post(
        f"{mamber_base_url}/get_user_details/", data={"email": user_email}
    )
    print(the_res.json())

    context = {"user": the_res.json()}

    return render(request, template, context)


def approve_kyc(request, kyc_id, user_email):
    the_res = requests.post(f"{mamber_base_url}/approve_kyc/", data={"kyc_id": kyc_id})
    print(the_res.json())
    if the_res.status_code == 200:
        try:
            print(user_email)
            subject, from_email, to = (
                "KYC APPROVED",
                "GameOn <noreply@gameon.com.ng>",
                [user_email],
            )

            html_content = render_to_string(
                "events/kyc_accepted.html",
                {
                    "email": user_email,
                    "doc_type": "Identity Document",
                },
            )
            msg = EmailMessage(subject, html_content, from_email, to)
            msg.content_subtype = "html"
            msg.send()
        except:
            pass

    return redirect("members:all-members")


def approve_ad(request, ad_id, user_email):
    the_res = requests.post(f"{mamber_base_url}/approve_ad/", data={"ad_id": ad_id})
    print(the_res.json())
    if the_res.status_code == 200:
        try:
            print(user_email)
            subject, from_email, to = (
                "KYC APPROVED",
                "GameOn <noreply@gameon.com.ng>",
                [user_email],
            )

            html_content = render_to_string(
                "events/kyc_accepted.html",
                {
                    "email": user_email,
                    "doc_type": "Proof of Address!",
                },
            )
            msg = EmailMessage(subject, html_content, from_email, to)
            msg.content_subtype = "html"
            msg.send()
        except:
            pass

    return redirect("members:all-members")
