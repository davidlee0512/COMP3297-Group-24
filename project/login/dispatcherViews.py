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
from django.core.mail import send_mail, EmailMessage
from heapq import heappush, heappop
from io import BytesIO

class dispatcherOrder(ListView):
    model = Order
    template_name = "dispatcherOrder.html"

    def get_queryset(self):
        #filter out the data
        return super().get_queryset().filter(status = 'Queued for Dispatch', packed = False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #put the pack into render
        context["packs"] = Pack.objects.all()

        return context

def chooseDispatch(request):
    #get the list of selected order
    choosedOrder = request.POST.getlist("orderId[]")

    locations = []

    #create a pack object and save it
    pack = Pack()
    pack.save()

    #put all the location from order into locations[]
    for orderid in choosedOrder:
        order = Order.objects.get(id = orderid)
        order.packed = True
        order.save()
        pack.order.add(order)
        if (order.location.id not in locations):
            locations.append(order.location.id)

    #generate a route
    route = optimalRoute(locations)

    #input the route to the pack
    for i in (range(len(route)-1)):
        itinerary = Distance.objects.get(location1_id = route[i], location2_id = route[i+1])
        pack.itinerary.add(itinerary)

    pack.save()
    
    return HttpResponseRedirect(reverse('dispatcher_order'))
    
def optimalRoute(locations):
    frontier = []
    heappush(frontier, (0, [1]))
    while (frontier):
        node = heappop(frontier)
        remain = [x for x in locations if x not in node[1]]
        print(node)
        print(frontier)
        print(remain)
        if (not isGoal(locations, node)):
            if remain:
                for next in remain:
                    heappush(frontier, (node[0]+distance(node[1][-1] ,next), node[1]+[next]))
            else:
                heappush(frontier, (node[0]+distance(node[1][-1], 1), node[1]+[1]))
        else:
            print (node[1])
            return node[1]

def isGoal(locations, node):
    for location in locations:
        if (location not in node[1]):
            return False
            
    if (1 != node[1][-1]):
        return False

    return True

def distance(fromId, toId):
    distance = Distance.objects.get(location1_id = fromId, location2_id = toId)
    return distance.distance
        
def packDispatch(request):
    #get the pack 
    pack = Pack.objects.get(id = request.POST["packId"])

    #change the status and add the dispatchedTime
    for order in pack.order.all():
        order.status = 'Dispatched'
        order.dispatchedTime = datetime.datetime.now()
        order.save()

        #create pdf
        currentLine = 750
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, currentLine, "OrderID: " + str(order.id))
        currentLine -= 50
        p.drawString(100, currentLine, "Priority: " + str(order.priority))
        currentLine -= 50
        p.drawString(100, currentLine, "Location: " + str(order.location.name))
        currentLine -= 50
        p.drawString(100, currentLine, "Items: ")
        currentLine -= 50

        for item in order.items.all():
            set_ = Order_Item.objects.get(order_id = order.id, item_id = item.id)
            p.drawString(150, currentLine, item.category + ": " + str(set_.quantity))
            currentLine -= 50

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        receivers = User.objects.filter(userType = "clinicManager", clinic = order.location)
        msg = EmailMessage("Your Order is on the way", "", to=[user.email for user in receivers])
        msg.attach('label.pdf', pdf, 'application/pdf')
        msg.content_subtype = "html"
        msg.send()



    #delete the pack
    pack.delete()

    return HttpResponseRedirect(reverse('dispatcher_order'))

def createCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="route.csv"'

    #create a csv writer
    writer = csv.writer(response)

    #get the pack object
    pack = Pack.objects.get(id = request.POST["packId"])

    #add all the location into the writer 
    currentLocation = Location.objects.get(id = 1)
    nextLocation = pack.itinerary.get(location1 = currentLocation).location2
    while (nextLocation.id != 1):
        writer.writerow([nextLocation.name, nextLocation.latitude, nextLocation.longitude, nextLocation.altitude])
        currentLocation = nextLocation
        nextLocation = pack.itinerary.get(location1 = currentLocation).location2

    #add QM in the end 
    source = Location.objects.get(id = 1)
    writer.writerow([source.name, source.latitude, source.longitude, source.altitude])

    return response

def autoPack(request):
    weightLimit = float(request.POST["weightLimit"])
    totalWeight = 0.0
    locations = []
    containerWeight = 2.0

    orders = Order.objects.filter(status = "Queued for Dispatch", packed = False).order_by("id").order_by("-priority").all()

    pack = Pack()
    pack.save()


    for order in orders:
        if (totalWeight + (order.getCombinedWeight() + containerWeight) <= weightLimit):
            totalWeight += (order.getCombinedWeight( + containerWeight))
            pack.order.add(order)
            order.packed = True
            order.save()
            if (order.location.id not in locations):
                locations.append(order.location.id)
        else:
            break
    
    #generate a route
    route = optimalRoute(locations)

    #input the route to the pack
    for i in (range(len(route)-1)):
        itinerary = Distance.objects.get(location1_id = route[i], location2_id = route[i+1])
        pack.itinerary.add(itinerary)

    pack.save()
    
    return HttpResponseRedirect(reverse('dispatcher_order'))
    

        

