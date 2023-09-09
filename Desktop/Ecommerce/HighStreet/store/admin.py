from django.contrib import admin
from .models import Category,Product,Variation
from django.forms import inlineformset_factory



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name','parent','is_active','created_at','slug')
    list_filter = ('category_name','is_active')
    search_fields = ('category_name',)
    ordering = ('category_name',)
    list_editable = ('is_active',)
    # prepopulated_fields = {'slug':('category_name',)}

    
class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1
    
VariationInlineFormset = inlineformset_factory(Product,Variation,fields=('variation_category','variation_value','is_active'),extra=1)


class ProductAdmin(admin.ModelAdmin):
    inlines = [VariationInline]
    list_display = ('title','price','stock','description','category','image','is_active','slug')
    prepopulated_fields = {'slug':('title',)}
    
admin.site.register(Product,ProductAdmin)     