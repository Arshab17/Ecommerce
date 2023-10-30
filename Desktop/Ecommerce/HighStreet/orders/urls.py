from django.urls import path
from.views import*
urlpatterns = [
    path('place_order/',place_order,name='place_order'),
    # path('payments/',payments,name='payments'),
    path('handle-payment/',handle_payment,name='handle_payment'),
    path('order_complete/',order_complete,name="order_complete")
]