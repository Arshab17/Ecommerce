from django.shortcuts import get_object_or_404, render,redirect
from cart.models import Cart,CartItem
from store.models import Product,Variation
from django.http import  HttpResponse
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# def cart_item_grouping(request,product_id):
#     product = Product.objects.get(id=product_id)
#     variation_id = request.Get.get('variation_id')
#     try:
#         cart = Cart.objects.get(cart_id = _cart_id(request))
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(
#         cart_id = _cart_id(request)
#     )
#     try:
#         item = CartItem.objects.get(cart=cart,product=product, variation__id=variation_id)
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(cart_id=_cart_id(request))
#     item =CartItem.objects.create(cart=cart, product=product,quantity=1)
#     item.variation.add(Variation.objects.get(id=variation_id))
#     return redirect('store/cart.html')


def add_cart(request,product_id):
    product = Product.objects.get(id = product_id)
    product_variation = []
    if request.method == 'POST':
       for item in request.POST:
        #    if item == 'csrfmiddlewaretoken':
        #        continue
           key = item
        #    print(key)
           value = request.POST[key]
           print(request.POST[key])
           try:  
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
                # print(variation)
                    
           except:
                pass
            
    
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()
    if cart_item_exist:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        #existing_variations-> database
        #current_variations-> product_variation
        #item_id-> database
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variation.all().order_by('variation_value')
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
      
        # product_variation.reverse()
        print(ex_var_list)
        print(product_variation)
        if product_variation in ex_var_list:
                #increment the quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product,id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product,quantity=1,cart=cart)
            
            if len(product_variation) > 0:
                item.variation.clear()
                    # print(item)
                item.variation.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart, 
        )
        if len(product_variation) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()
    return redirect('cart')
    # return HttpResponse(cart_item.product)

def cart(request):
    tax=0
    total=0
    grand_total=0
    quantity=0
    cart_items = None
    try:
        
        cart = Cart.objects.get(cart_id =_cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart,is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (3*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'tax': tax,
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total':grand_total,
    }
    return render(request,'store/cart.html',context)  

def remove_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    try:
        cart_item =CartItem.objects.get(product=product, cart=cart, id=cart_item_id) 
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
    return redirect('cart') 

def remove_cart_item(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    
    
    