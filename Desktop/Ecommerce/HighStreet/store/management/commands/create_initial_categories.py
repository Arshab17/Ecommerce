from django.core.management.base import BaseCommand
from store.models import Category

class Command(BaseCommand):
    help = 'Create intial parent categories'
    
    def handle(self,*args,**options):
        womens = Category.objects.create(category_name = 'Womens')
        women_clothing = Category.objects.create(category_name="Women's Clothing",parent=womens)
        womens_tops = Category.objects.create(category_name='Women Tops', parent=women_clothing)
        women_bottoms = Category.objects.create(category_name='Women Bottoms', parent=women_clothing)
        
        mens = Category.objects.create(category_name='mens')
        men_clothing = Category.objects.create(category_name="Men's Clothing",parent = mens)
        mens_tops = Category.objects.create(category_name="Men Tops", parent=men_clothing)
        mens_bottoms = Category.objects.create(category_name="Men Bottoms", parent=men_clothing)
        
        self.stdout.write(self.style.SUCCESS('Successfully created initial categories'))
