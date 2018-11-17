from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.views.generic.list import ListView
from login.models import *

# Create your views here.

#login page
def mainpage(request):
    return render(request, 'login.html', {})

#forget password page
def forgetPassword(request):
    return render(request, 'forgotPassword.html', {})

#registration page
class registration(ListView):
    model = Location
    template_name = "registration.html"

    def get_queryset(self):
        return super().get_queryset().exclude(id = 1)

#profile page
class Profile(ListView):
    model = User
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data form urls(done in urls.py)
        username = self.kwargs['username'] 
        password = self.kwargs['password']

        #get the user data from database base of username
        user = User.objects.get(userID = username)

        #check the page if the username and password is correct
        if (user.password == password):
            context['correct'] = True
        else:
            context['correct'] = False

        #put the data from the database to the page for render the page
        context["user"] = user
        return context

    

class clinicManagerItem(ListView):
    model = Item
    template_name = "clinicManagerItems.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data from url(done in urls.py)
        id_ = self.kwargs['userid']

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
        userid = self.kwargs['userid']

        #get the object for render
        context["item"] = Item.objects.get(id = itemid)
        context["user"] = User.objects.get(id = userid)
        return context
    

class clinicManagerOrder(ListView):
    model = Item
    template_name = "clinicManagerOrder.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get the data from urls(done in urls.py)
        id_ = self.kwargs['userid']

        #get the object for render
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

        #get the data from urls(done in urls.py)
        orderid = self.kwargs['orderid']

        #get the object for render
        context["order"] = Order.objects.get(id = orderid)
        return context

class dispatcherOrder(ListView):
    model = Order
    template_name = "dispatcherOrder.html"

    def get_queryset(self):
        return super().get_queryset().filter(status = 'Queued for Dispatch')

def changeProfile(request, ID, password, email, firstname, lastname):
    #get the user object that need to change profile
    user = User.objects.get(id = ID)

    #update the data base on the input
    user.password = password
    user.email = email
    user.firstname = firstname
    user.lastname = lastname

    #update the database
    user.save()

    return HttpResponse('Change Applied')

def makeOrder(request, userid, itemid, quantity):
    #get the object that for make a new order
    item = Item.objects.get(id = itemid)
    user = User.objects.get(id = userid)

    #create a new order object
    order = Order()
    order.status = "Queued for Processing"
    order.location = user.clinic
    order.combined_weights = item.shipping_weight * quantity
    order.priority = 10

    #save the order to database
    order.save()

    #create a Order_Item object (intermediate object)
    set_ = Order_Item()
    set_.order_id = order.id
    set_.item_id = item.id
    set_.quantities = quantity

    #save the Order_Item object
    set_.save()

    return HttpResponse('Order successful')

def deleteOrder(request, userid, orderid):

    #delete the order
    order = Order.objects.get(id = orderid)
    order.delete()

    return HttpResponse('Order deleted')

def pack(request, orderid):
    #get the order object
    order = Order.objects.get(id = orderid)

    #update the status
    order.status = 'Queued for Dispatch'

    #save the object
    order.save()

    return HttpResponse('Packed')

def dispatch(request, orderid):
    #get the order object
    order = Order.objects.get(id = orderid)

    #update the status
    order.status = 'Dispatched'

    #save the object
    order.save()
    return HttpResponse('Dispatched')


    

    




    

    

    

    