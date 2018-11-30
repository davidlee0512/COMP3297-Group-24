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
    def post(self, request, *args, **kwargs):
        orderid = request.POST["orderId"]
        order=Order.objects.get(id = orderid)
        return render(request, 'warehousePersonalChecklist.html', {'order' : order})

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
