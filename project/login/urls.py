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
from django.conf import settings
from django.conf.urls.static import static
from . import adminViews, dispatcherViews, warehousePersonalViews, clinicManagerViews, profileViews, loginViews

urlpatterns = [
    path('', loginViews.mainpage),
    path('forget_password', loginViews.forgetPassword),
    path('forget_password_token', loginViews.forgetPassword_sendtoken),
    path('reset_password', loginViews.resetPassword),
    path('reset_password_token', loginViews.resetPassword_token),
    path('registration', loginViews.registration.as_view()),
    path("createAcc", loginViews.createAcc),
    
    path('profile', profileViews.Profile.as_view()),
    path('changeInfo', profileViews.changeProfile),

    path('clinic_manager_item', clinicManagerViews.clinicManagerItem.as_view()),
    path('clinic_manager_description/<int:itemid>', clinicManagerViews.clinicManagerDescription.as_view()),
    path('clinic_manager_order', clinicManagerViews.clinicManagerOrder.as_view(), name = 'clinic_manager_order'),
    path('recieveOrder', clinicManagerViews.recieveOrder),
    path('makeOrder', clinicManagerViews.makeOrder),
    path('deleteOrder/<int:orderid>', clinicManagerViews.deleteOrder),

    path('warehouse_personal_order', warehousePersonalViews.warehousePersonalOrder.as_view(), name = 'warehouse_personal_order'),
    path('warehouse_personal_checklist', warehousePersonalViews.warehousePersonalChecklist.as_view()),
    path('processOrder', warehousePersonalViews.processOrder),
    path('pack', warehousePersonalViews.pack),
    path('printPDF', warehousePersonalViews.printPDF),

    path('dispatcher_order', dispatcherViews.dispatcherOrder.as_view(), name = 'dispatcher_order'),
    path('chooseDispatch', dispatcherViews.chooseDispatch),
    path('dispatch/<int:orderid>', dispatcherViews.dispatch),
    path('packDispatch', dispatcherViews.packDispatch),
    path('createCSV', dispatcherViews.createCSV),
    path('autopack', dispatcherViews.autoPack),

    path('token', adminViews.TokenView.as_view()),
    path('sendToken', adminViews.sendToken),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
