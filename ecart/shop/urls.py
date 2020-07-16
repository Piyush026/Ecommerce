from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name="ShopHome"),
    path('table/', views.view_info, name='table'),
    path('contact/', views.contact, name="contactus"),
    path('about/', views.about, name="aboutus"),
    path('tracker/', views.tracker, name="tracker"),
    path('product/<int:myid>', views.productView, name="productView"),
    path('search/', views.search, name="search"),
    path('checkout/', views.checkout, name="checkout"),
    path('handlerequest/', views.handlerequest, name="handlerequest"),
]
