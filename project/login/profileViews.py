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

#profile page
class Profile(ListView):
    model = User
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the user data from database base on cookies
        user = User.objects.get(id = self.request.COOKIES['user'])

        #put the data from the database to the page for render the page
        context["user"] = user
        return context

    def post(self, request, *args, **kwargs):
        username = request.POST['userID']
        password = request.POST['password']

        #get the user data from database base of username
        user = User.objects.get(userID = username)

        #password checking
        if (user.password == password):
            #correct 
            output = render(request, 'profile.html', {'user' : user})
            
            output.set_cookie('user', user.id)

            return output
        else:
            #incorrect
            return HttpResponse('Worng userID or password')

#change profile
def changeProfile(request):
    #get the user object that need to change profile
    id_ = request.COOKIES['user']
    user = User.objects.get(id = id_)

    #update the data base on the input
    user.password = request.POST["password"]
    user.email = request.POST["email"]
    user.firstname = request.POST["firstname"]
    user.lastname = request.POST["lastname"]

    #update the database
    user.save()

    return HttpResponse('Change Applied')
