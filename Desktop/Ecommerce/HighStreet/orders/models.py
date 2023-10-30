from django.db import models
from account.models import CustomUser
from store.models import Product,Variation
# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id
    

class Order(models.Model):
    STATUS = (
        ('new','New'),
        ('accepted','Accepted'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
    )
    user = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    payment_tracking = models.CharField(max_length=100,null=True,blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    order_note = models.CharField(max_length=100,blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10,choices=STATUS,default='new')
    ip = models.CharField(max_length=20,blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    def __str__(self):
        return self.first_name
    
    
class OrderProduct(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation,blank=True,null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.title