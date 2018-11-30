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

class clinicManagerItem(ListView):
    model = Item
    template_name = "clinicManagerItems.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data from url(done in urls.py)
        id_ = self.request.COOKIES['user']

        #get the object for render
        context["user"] = User.objects.get(id = id_)
        return context

class clinicManagerDescription(ListView):
    model = Item
    template_name = "clinicManagerDescription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data from urls(done in urls.py)
        itemid = self.kwargs['itemid']

        #get the object for render
        context["item"] = Item.objects.get(id = itemid)
        return context
    

class clinicManagerOrder(ListView):
    model = Item
    template_name = "clinicManagerOrder.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data from urls(done in urls.py)
        id_ = self.request.COOKIES['user']

        #get the object for render
        context["user"] = User.objects.get(id = id_)
        context["orders"] = Order.objects.filter(location = context["user"].clinic)

        return context

def recieveOrder(request):
    orderid = request.POST["orderId"]
    order = Order.objects.get(id = orderid)

    order.status = "Delivered"
    order.deliveredTime = datetime.datetime.now()

    order.save()

    return HttpResponseRedirect(reverse('clinic_manager_order'))

def makeOrder(request):
    items = Item.objects.all()
    user = User.objects.get(id = request.POST.get("userid"))

    order = Order()
    order.status = "Queued for Processing"
    order.priority = request.POST["priority"]
    order.location = user.clinic
    order.save()

    totalNo = 0
    for item in items:
        quantity = request.POST.get(str(item.id))
        totalNo += int(quantity)

    if (totalNo == 0):
        order.delete()
        return HttpResponse("please input a valid number")

    for item in items:
        quantity = request.POST.get(str(item.id))

        if (quantity != '0'):
            set_ = Order_Item()
            set_.order_id = order.id
            set_.item_id = item.id
            set_.quantity = quantity
            set_.save()
    
    return HttpResponseRedirect(reverse("clinic_manager_order"))

def deleteOrder(request, orderid):

    #delete the order
    order = Order.objects.get(id = orderid)
    order.delete()

    return HttpResponse('Order deleted')
