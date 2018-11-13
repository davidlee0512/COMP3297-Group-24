from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.views.generic.list import ListView
from login.models import *

# Create your views here.
def mainpage(request):
    return render(request, 'login.html', {})

def forgetPassword(request):
    return render(request, 'forgotPassword.html', {})

class registration(ListView):
    model = Location
    template_name = "registration.html"

    def get_queryset(self):
        return super().get_queryset().exclude(id = 1)

class Profile(ListView):
    model = User
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        password = self.kwargs['password']
        user = User.objects.get(userID = username)
        if (user.password == password):
            context['correct'] = True
        else:
            context['correct'] = False
        context["user"] = user
        return context

    

class clinicManagerItem(ListView):
    model = Item
    template_name = "clinicManagerItems.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_ = self.kwargs['userid']
        context["user"] = User.objects.get(id = id_)
        return context

class clinicManagerDescription(ListView):
    model = Item
    template_name = "clinicManagerDescription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itemid = self.kwargs['itemid']
        userid = self.kwargs['userid']
        context["item"] = Item.objects.get(id = itemid)
        context["user"] = User.objects.get(id = userid)
        return context
    

class clinicManagerOrder(ListView):
    model = Item
    template_name = "clinicManagerOrder.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_ = self.kwargs['userid']
        context["user"] = User.objects.get(id = id_)
        context["orders"] = Order.objects.filter(location = context["user"].clinic)
        return context

class warehousePersonalOrder(ListView):
    model = Order
    template_name = "warehousePersonalOrder.html"

    def get_queryset(self):
        return super().get_queryset().filter(status = 'Queued for Processing')

class warehousePersonalChecklist(ListView):
    model = Order
    template_name = "warehousePersonalChecklist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orderid = self.kwargs['orderid']
        context["order"] = Order.objects.get(id = orderid)
        return context

class dispatcherOrder(ListView):
    model = Order
    template_name = "dispatcherOrder.html"

    def get_queryset(self):
        return super().get_queryset().filter(status = 'Queued for Dispatch')

def changeProfile(request, ID, password, email, firstname, lastname):
    user = User.objects.get(id = ID)
    user.password = password
    user.email = email
    user.firstname = firstname
    user.lastname = lastname
    user.save()
    return HttpResponse('Change Applied')

def makeOrder(request, userid, itemid, quantity):
    item = Item.objects.get(id = itemid)
    user = User.objects.get(id = userid)
    order = Order()
    order.status = "Queued for Processing"
    order.location = user.clinic
    order.combined_weights = item.shipping_weight * quantity
    order.priority = 10
    order.save()
    set_ = Order_Item()
    set_.order_id = order.id
    set_.item_id = item.id
    set_.quantities = quantity
    set_.save()
    return HttpResponse('Order successful')

def deleteOrder(request, userid, orderid):
    order = Order.objects.get(id = orderid)
    order.delete()
    return HttpResponse('Order deleted')

def pack(request, orderid):
    order = Order.objects.get(id = orderid)
    order.status = 'Queued for Dispatch'
    order.save()
    return HttpResponse('Packed')

def dispatch(request, orderid):
    order = Order.objects.get(id = orderid)
    order.status = 'Dispatched'
    order.save()
    return HttpResponse('Dispatched')


    

    




    

    

    

    