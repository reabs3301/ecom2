from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
   path('',views.home , name = 'home'),
   path('detail/<int:prod_id>/<int:quantite>/' , views.details , name='detail'),
   path('get/<int:prod_id>/' , views.decrease , name='get'),
   path('search/', views.searching , name='search'),
   path('add/' , views.add , name = 'add'),
   path('pannier/' , views.pannier , name = 'pannier'),
   path('delete_from_pannier/<int:prod_id>/' , views.delete_from_pannier , name='delete_from_pannier'),
   path('paiement/<int:total>/' , views.payment_page , name='paiement'),
   #path('generate_bill/' , views.generate_bill , name='generate_bill')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
