from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
   path('',views.welcome , name = 'welcome'),
   path('home/',views.home_view , name = 'home'),
   path('disconnect/',views.disconnect_view , name = 'disconnect'),
   path('login_page/', views.login_page_view, name='login_page'),
   path('signup_page/', views.signup_page_view, name='signup_page'),
   path('login/', views.login_view, name='login'),
   path('signup/', views.signup_view, name='signup'),

   path('detail/<int:prod_id>/<str:type>/' , views.details_view , name='detail'),
   path('bid_page_view/<int:prod_id>/' , views.auction_page_view , name='auction_page'),
   path('bid_view/', views.bid_view , name='bid'),
   path('add_to_panier_view/<int:prod_id>/' , views.add_to_pannier_view , name='add_to_pannier'),
   path('search/', views.searching , name='search'),
   path('add_view/' , views.add_view , name = 'add'),
   path('add_page_view/' , views.add_page_view , name = 'add_page'),
   path('pannier_page/' , views.pannier_page_view , name = 'pannier_page'),
   path('delete_from_pannier/<int:prod_id>/' , views.delete_from_pannier , name='delete_from_pannier'),
   path('paiement/<int:total>/' , views.payment_page , name='paiement'),
   #path('generate_bill/' , views.generate_bill , name='generate_bill')

   path('print/', views.print_view, name='print'),
   
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
