from django.urls import path
from .views import* 

urlpatterns = [
    path('register/',register,name='register'),
    path('activate/<uidb64>/<token>/',activate,name='activate'),
    path('signin/',signin,name='signin'),
    path('signout/',signout,name='signout'),
    path('dashboard/',dashboard,name="dashboard"),
    path('forgot_password/',forgot_password, name='forgot_password'),
    path('resetpassword_validate/<uidb64>/<token>/',resetpassword_validate,name='resetpassword_validate'),
    path('reset_password/',reset_password, name='reset_password'),

]