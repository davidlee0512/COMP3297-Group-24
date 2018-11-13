"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.mainpage),
    path('forget_password', views.forgetPassword),
    path('registration', views.registration.as_view()),
    path('profile/<str:username>/<str:password>', views.Profile.as_view()),

    path('clinic_manager_item/<int:userid>', views.clinicManagerItem.as_view()),
    path('clinic_manager_description/<int:userid>/<int:itemid>', views.clinicManagerDescription.as_view()),
    path('clinic_manager_order/<int:userid>', views.clinicManagerOrder.as_view()),

    path('warehouse_personal_order/<int:userid>', views.warehousePersonalOrder.as_view()),
    path('warehouse_personal_checklist/<int:userid>/<int:orderid>', views.warehousePersonalChecklist.as_view()),

    path('dispatcher_order/<int:userid>', views.dispatcherOrder.as_view()),

    path('changeInfo/<int:ID>/<str:password>/<str:email>/<str:firstname>/<str:lastname>', views.changeProfile),
    path('makeOrder/<int:userid>/<int:itemid>/<int:quantity>', views.makeOrder),
    path('deleteOrder/<int:userid>/<int:orderid>', views.deleteOrder),
    path('pack/<int:orderid>', views.pack),
    path('dispatch/<int:orderid>', views.dispatch)
]
