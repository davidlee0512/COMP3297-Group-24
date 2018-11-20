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

def recieveOrder(request):
    orderid = request.POST["orderId"]
    order = Order.objects.get(id = orderid)

    order.status = "Delivered"
    order.deliveredTime = datetime.datetime.now()

    order.save()

    return HttpResponseRedirect(reverse('clinic_manager_order'))

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["packs"] = Pack.objects.all()

        return context
        

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

def processOrder(request):
    #get the order object
    orderId = request.POST["orderId"]
    order = Order.objects.get(id = orderId)

    #update the status
    order.status = 'Processing by Warehouse'

    #save the object
    order.save()

    return HttpResponseRedirect(reverse('warehouse_personal_order'))

def pack(request):
    #get the order object
    orderId = request.POST["orderId"]
    order = Order.objects.get(id = orderId)

    #update the status
    order.status = 'Queued for Dispatch'

    #save the object
    order.save()

    return HttpResponseRedirect(reverse('warehouse_personal_order'))

def chooseDispatch(request):
    choosedOrder = request.POST.getlist("orderId[]")
    locations = []
    pack = Pack()
    pack.save()
    for orderid in choosedOrder:
        order = Order.objects.get(id = orderid)
        pack.order.add(order)
        if (order.location.id not in locations):
            locations.append(order.location.id)

    route = optimalRoute(locations)

    route.append(1)

    for i in (range(len(route)-1)):
        itinerary = Distance.objects.get(location1_id = route[i], location2_id = route[i+1])
        pack.itinerary.add(itinerary)

    pack.save()
    
    return HttpResponse(route)
    
def optimalRoute(locations):
    frontier = []
    heappush(frontier, (0, [1]))
    while (frontier):
        node = heappop(frontier)
        remain = [x for x in locations if x not in node[1]]
        if remain:
            for next in remain:
                heappush(frontier, (node[0]+distance(node[1][-1],next), node[1]+[next]))
        else:
            return node[1]

def distance(fromId, toId):
    distance = Distance.objects.get(location1_id = fromId, location2_id = toId)
    return distance.distance




"""def autoPack(request):
    #can be change
    maximumweight = 10.0

    lowOrder = Order.objects.filter(priority = 1)
    medimumOrder = Order.objects.filter(priority = 2)
    highOrder = Order.objects.filter(priority = 3)

    highTotalWeight = 0.0
    for order in highOrder.all():
        highTotalWeight += order.getCombinedWeight()

    if (highTotalWeight > maximumweight):
        orders = highOrder.all().order_by(location_id)
        totalWeight = 0.0
        packedOrder = []
        totalLocation = []

        #get as much as possible before exceed teh maximum weight of the drone
        for order in orders:
            orderWeight = order.getCombinedWeight()
            if ((totalWeight + orderWeight) > maximumweight):
                break
            else:
                totalWeight += orderWeight
                packedOrder.append(order)

        pack = Pack()

        for order in packedOrder:
            pack.order.add(order)
            #get all the location
            if (totalLocation.count(order.location.id) == 0):
                totalLocation.append(order.location.id)

        frontier = []
        heappush(frontier, (0, [1]))
        while (frontier):
            node = heappop(frontier)

        return 

    medimumTotalWeight = 0.0
    for order in medimumOrder.all():
        lowTotamedimumTotalWeightlWeight += order.getCombinedWeight()

    if ((highTotalWeight + medimumTotalWeight) > maximumweight):

        return

    lowTotalWeight = 0.0
    for order in lowOrder.all():
        lowTotalWeight += order.getCombinedWeight()

    if ((lowTotalWeight + medimumTotalWeight + highTotalWeight) > maximumweight):
        orders = lowOrder.all().order_by(location_id)
        for order in orders:

        return
    
    else:
         return"""

    

def printPDF(request):
    #get the order object
    orderId = request.POST["orderId"]
    order = Order.objects.get(id = orderId)

    currentLine = 750
    

    # Create a file-like buffer to receive PDF data.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="label' + str(order.id) + '.pdf"'

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(response)

    p.drawString(100, currentLine, "OrderID: " + str(order.id))
    currentLine -= 50
    p.drawString(100, currentLine, "Priority: " + str(order.priority))
    currentLine -= 50
    p.drawString(100, currentLine, "Location: " + str(order.location.name))
    currentLine -= 50
    p.drawString(100, currentLine, "Items: ")
    currentLine -= 50
    #drawing each item
    for item in order.items.all():
        set_ = Order_Item.objects.get(order_id = order.id, item_id = item.id)
        p.drawString(150, currentLine, item.category + ": " + str(set_.quantity))
        currentLine -= 50

    p.showPage()
    p.save()
    return response

def createCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="route.csv"'

    writer = csv.writer(response)
    pack = Pack.objects.get(id = request.POST["packId"])

    currentLocation = Location.objects.get(id = 1)
    nextLocation = pack.itinerary.get(location1 = currentLocation).location2
    while (nextLocation.id != 1):
        writer.writerow([nextLocation.name, nextLocation.latitude, nextLocation.longitude, nextLocation.altitude])
        currentLocation = nextLocation
        nextLocation = pack.itinerary.get(location1 = currentLocation).location2


    source = Location.objects.get(id = 1)
    writer.writerow([source.name, source.latitude, source.longitude, source.altitude])

    return response

def packDispatch(request):
    pack = Pack.objects.get(id = request.POST["packId"])

    for order in pack.order.all():
        order.status = 'Dispatched'
        order.dispatchedTime = datetime.datetime.now()
        order.save()

    pack.delete()
    return HttpResponseRedirect(reverse('dispatcher_order'))

def dispatch(request, orderid):
    #get the order object
    order = Order.objects.get(id = orderid)

    #update the status
    order.status = 'Dispatched'
    order.dispatchedTime = datetime.datetime.now()

    #save the object
    order.save()
    return HttpResponseRedirect(reverse('dispatcher_order'))

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



    

    




    

    

    

    