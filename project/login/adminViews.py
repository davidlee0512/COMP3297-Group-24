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

class TokenView(ListView):
    model = Token
    template_name = "token.html"

def sendToken(request):
    tokenid = request.POST['tokenid']
    token = Token.objects.get(id = tokenid)

    send_mail(
        'Token',
        token.token,
        'davidlee0512@gmail.com',
        [token.email],
        fail_silently=False,
    )
    return HttpResponse("sent")
