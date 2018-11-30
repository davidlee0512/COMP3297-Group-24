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

class dispatcherOrder(ListView):
    model = Order
    template_name = "dispatcherOrder.html"

    def get_queryset(self):
        return super().get_queryset().filter(status = 'Queued for Dispatch')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["packs"] = Pack.objects.all()

        return context

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