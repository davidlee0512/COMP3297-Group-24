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
import random, string
from django.core.mail import send_mail
from heapq import heappush, heappop
from django.utils.datastructures import MultiValueDictKeyError

#login page
def mainpage(request):
    return render(request, 'login.html', {})

#forget password page
def forgetPassword(request):
    return render(request, 'forgotPassword.html', {})

def forgetPassword_sendtoken(request):
    userId = request.POST["userID"]
    try:
        user_ = User.objects.get(userID = userId)
    except User.DoesNotExist:
        return HttpResponse("No such user")
    forget_password=Forget_password()
    forget_password.user=user_
    forget_password.token=''.join(random.choices(string.digits, k=6))
    found = True
    while (found):
        try:
            Forget_password.objects.get(token = forget_password.token)
        except Forget_password.DoesNotExist:
            found = False
        forget_password.token=''.join(random.choices(string.digits, k=6))
    forget_password.save()
    send_mail(
        'Token for reset password',
        "Use this token to reset your password\n" + forget_password.token + "\n" + 
        "You can also use this link to registrate :" + "http://25.44.234.76:8000/reset_password?token=" + forget_password.token + "",
        'davidlee0512@gmail.com',
        [forget_password.user.email],
        fail_silently=False,
    )  
    return HttpResponse("Token sent")

def resetPassword(request):
    try:
        token = request.GET["token"]
    except MultiValueDictKeyError:
        return render(request, 'resetPassword.html', {})
    return render(request, 'resetPassword.html', {"token": token})

#reset password page
def resetPassword_token(request):
    password = request.POST["password"]
    token = request.POST["token"]
    try:
        forget = Forget_password.objects.get(token = token)
    except Token.DoesNotExist:
        return HttpResponse("No such token")
    forget.user.password = password
    forget.user.save()
    forget.delete()
    return HttpResponse("Password reset")

#registration page
class registration(ListView):
    model = Location
    template_name = "registration.html"

    def get_queryset(self):
        return super().get_queryset().exclude(id = 1)

    def get(self, request):
        try:
            token = request.GET["token"]
        except MultiValueDictKeyError:
            return super().get(request)
        return render(request, "registration.html", {"token": token,"location_list": self.get_queryset() })

#create account by POST
def createAcc(request):
    userId = request.POST["userID"]
    password = request.POST["password"]
    token = request.POST["token"]
    firstName = request.POST["firstName"]
    lastName = request.POST["lastName"]
    location = request.POST["location"]

    try:
        token_ = Token.objects.get(token = token)
    except Token.DoesNotExist:
        return HttpResponse("No such token")

    try:
        user_ = User.objects.get(userID = userId)
    except User.DoesNotExist:
        user = User()
        user.userID = userId
        user.password = password
        user.first_name = firstName
        user.last_name = lastName
        user.email = token_.email
        user.userType = token_.userType
        if (user.userType == "clinicManager"):
            user.clinic = Location.objects.get(id = location)
        else:
            user.clinic = Location.objects.get(id = 1)

        user.save()
        token_.delete()
        return HttpResponse("user created")

    return HttpResponse("Repeated userID")
