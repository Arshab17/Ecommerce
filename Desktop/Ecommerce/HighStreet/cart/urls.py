from django.urls import path
from .views import*
urlpatterns = [
     path('',cart,name='cart'),
     path('add_cart/<int:product_id>',add_cart,name='add_cart'),
     path('remove_cart/<int:product_id>/<int:cart_item_id>/',remove_cart,name='remove_cart'),
     path('remove_cart_items/<int:product_id>/<int:cart_item_id>/',remove_cart_item,name='remove_cart_items'),
     path('checkout/',checkout,name='checkout')
     # path('add_cart_item/<int:product_id>/',cart_item_grouping,name="item_add")
]
 