from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here
class CustomUser(AbstractUser):
    is_active = models.BooleanField(default=True)
    
    
class UserProfile(models.Model):
    image = models.ImageField(upload_to='profile_image/',null=True,blank=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=20,blank=True)
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100,blank=True)
    city = models.CharField(max_length=10,blank=True)
    state = models.CharField(max_length=10,blank=True)
    pincode = models.CharField(max_length=10,blank=True)
    phone = models.CharField(max_length=12,blank=True)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.full_name}'
    
    def save(self, *args, **kwargs):
        if self.default:
            self.__class__._default_manager.filter(user =self.user,default=True).update(default=False)
        super().save(*args,**kwargs)
    
    