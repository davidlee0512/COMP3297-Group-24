from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, FileResponse
from django.template import loader
from django import template
from django.urls import reverse
from django.views.generic.list import ListView
from easy_pdf.views import PDFTemplateView
from login.models import *
from login import views
from reportlab.pdfgen import canvas
import io, datetime, csv
from django.core.mail import send_mail
from heapq import heappush, heappop
import random, string

class TokenView(ListView):
    model = Token
    template_name = "token.html"

def sendToken(request):
    tokenid = request.POST['tokenid']
    token = Token.objects.get(id = tokenid)

    send_mail(
        'Token for registration',
        "Token: " + token.token + "\n" +
        "You can use this link to registrate :" + "http://25.44.234.76:8000/registration?token=" + token.token + "",
        'davidlee0512@gmail.com',
        [token.email],
        fail_silently=False,
    )
    return HttpResponseRedirect(reverse("token"))

def createToken(request):
    token = Token()
    token.email = request.POST["email"]
    token.userType = request.POST["role"]
    token.token = ''.join(random.choices(string.digits, k=6))
    found = True
    while (found):
        try:
            Token.objects.get(token = token.token)
        except Token.DoesNotExist:
            found = False
            token.token=''.join(random.choices(string.digits, k=6))

    token.save()
    return HttpResponseRedirect(reverse("token"))

def deleteToken(request):
    token = Token.objects.get(id = request.POST['tokenid'])
    token.delete()

    return HttpResponseRedirect(reverse("token"))
