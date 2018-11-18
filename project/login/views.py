from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views.generic.list import ListView
from login.models import *
from login import views

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

class warehousePersonalOrder(ListView):
    model = Order
    template_name = "warehousePersonalOrder.html"

    def get_queryset(self):
        return super().get_queryset().filter(status = 'Queued for Processing')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["queue"] = Order.objects.filter(status = 'Queued for Processing')
        context["processing"] = Order.objects.filter(status = 'Processing by Warehouse')

        return context


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

def changeProfile(request, password, email, firstname, lastname):
    #get the user object that need to change profile
    id_ = self.request.COOKIES['user']
    user = User.objects.get(id = id_)

    #update the data base on the input
    user.password = password
    user.email = email
    user.firstname = firstname
    user.lastname = lastname

    #update the database
    user.save()

    return HttpResponse('Change Applied')

def makeOrder(request):
    items = Item.objects.all()
    user = User.objects.get(id = request.POST.get("userid"))

    order = Order()
    order.status = "Queued for Processing"
    order.priority = request.POST["priority"]
    order.location = user.clinic
    order.save()

    for item in items:
        quantity = request.POST.get(str(item.id))

        if (quantity != '0'):
            set_ = Order_Item()
            set_.order_id = order.id
            set_.item_id = item.id
            set_.quantity = quantity
            set_.save()
    
    return HttpResponse('Order successful')




def deleteOrder(request, orderid):

    #delete the order
    order = Order.objects.get(id = orderid)
    order.delete()

    return HttpResponse('Order deleted')

def processOrder(request):
    #get the order object
    orderId = request.POST["orderId"]
    order = Order.objects.get(id = orderId)

    #update the status
    order.status = 'Processing by Warehouse'

    #save the object
    order.save()

    return HttpResponseRedirect(reverse('warehouse_personal_order'))

def pack(request, orderid):
    #get the order object
    order = Order.objects.get(id = orderid)

    #update the status
    order.status = 'Queued for Dispatch'

    #save the object
    order.save()

    return HttpResponseRedirect(reverse('warehouse_personal_order'))

def dispatch(request, orderid):
    #get the order object
    order = Order.objects.get(id = orderid)

    #update the status
    order.status = 'Dispatched'

    #save the object
    order.save()
    return HttpResponse('Dispatched')


    

    




    

    

    

    