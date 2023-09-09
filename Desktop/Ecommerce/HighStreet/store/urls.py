from django.urls import path
from.views import *
urlpatterns = [
    path('',home,name='home'),
    path('store/<slug:category_slug>/',stores,name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>',product_details,name='product_details'),

]