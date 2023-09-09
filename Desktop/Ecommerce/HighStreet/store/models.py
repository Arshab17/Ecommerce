from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from autoslug import AutoSlugField
# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(populate_from='category_name',unique=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args,**kwargs)
        
    def __str__(self):
        return self.category_name
    
class Product(models.Model):
    
    # @staticmethod
    # def get_size_choices():
    #         return(
    #             ('S','small'),
    #             ('M','medium'),
    #             ('L','large'),
    #             ('XL','extra large'),
    #             ('28','28'),
    #             ('30','30'),
    #             ('32','32'),
    #             ('34','34'),
    #             ('36','36'),
    #             ('38','38'),
    #         )
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='images/products/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True,max_length=100)
    
    
    class Meta:
        verbose_name_plural = 'products'   
        ordering = ('-created_at',) 
    
    
    def get_url(self):
        return reverse('product_details', args=[self.category.slug,self.slug])
     
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args,**kwargs)
        
    def __str__(self):
        return self.title
    
class VariationManager(models.Manager):
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)
    
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    
variation_category_choices = (
    ('size','Size'),
    ('color','Color'),
    ('pattern','Pattern'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value