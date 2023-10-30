from django.shortcuts import render,redirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from store.models import Product
import datetime
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.

#razorpay payment function
@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        razorpay_order_id = data.get('razorpay_order_id')
        print(razorpay_order_id)
        payment_id = data.get('razorpay_payment_id')
        try:
            print('in try block')
            order = Order.objects.get(payment_tracking = razorpay_order_id)
            print(order.payment_tracking)
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
            payment = client.payment.fetch(payment_id)
            
            
            print(payment)
            if payment['status'] == 'captured':
                payment_obj = Payment.objects.create(
                    payment_id = payment['id'],
                    payment_method = 'Razorpay',
                    amount_paid = order.order_total,
                    status = 'success',
                    user = request.user,
            
                )
                order.is_ordered = True
                order.save()
                 # Move the cart items to order product table
                cart_items = CartItem.objects.filter(user = request.user)
                print(cart_items)
                for item in cart_items:
                    order_product=OrderProduct()
                    order_product.order=order
                    order_product.payment=payment_obj
                    order_product.user=item.user
                    order_product.product=item.product
                    order_product.quantity=item.quantity
                    order_product.product_price=item.product.price
                    order_product.ordered=True
                    order_product.save()
                    

                    # Handle variations (assuming Variation is a ManyToManyField)
                    for variation in item.variation.all():
                        order_product.variation.add(variation)
                    order_product.save()    
                    
                    # Reduce the quatity of the sold products
                    product = Product.objects.get(id = item.product.id)
                    product.stock -= item.quantity
                    product.save()
                    # clear cart
                    user = request.user
                    user.cartitem_set.all().delete()
                    
                    # send order received email to customer
                    mail_subject = 'Thank You! Your Order has been received'
                    message = render_to_string('order/order_received_email.html',{
                    'user' : request.user,
                    'order':order,
                })
                    to_email = request.user.email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.send()
                    # send order number and transaction id back to sendData method via jsonResponse method 
                    data ={
                        'order_number':order.order_number,
                        'transID':payment_obj.payment_id,
                    }
                return JsonResponse(data)
            else:
                return JsonResponse({'message':'payment failed'})
        except Order.DoesNotExist:
            return JsonResponse({'message':'invalid order'})
        except Exception as e:
            return JsonResponse({'message':'server error ,please try again'})

#paypal payment function
# def payments(request):
#     body = json.loads(request.body)
#     order = Order.objects.get(user= request.user,is_ordered=False,order_number=body['orderID'])
#     print(body)
#     payment = Payment(
#         user = request.user,
#         payment_id = body['transID'],
#         payment_method = body['payment_method'],
#         amount_paid = order.order_total,
#         status = body['status'],
#     )
#     payment.save()
#     order.payment = payment
#     order.is_ordered = True
#     order.save()
#     # Move the cart items to order product table
#     cart_items = CartItem.objects.filter(user = request.user)
#     for item in cart_items:
#         orderproduct = OrderProduct()
#         orderproduct.order_id = order.id
#         orderproduct.payment = payment
#         orderproduct.user_id = request.user.id
#         orderproduct.product_id = item.product_id
#         orderproduct.quantity = item.quantity
#         orderproduct.product_price = item.product.price
#         orderproduct.ordered = True 
#         orderproduct.save()
    # Reduce the quatity of the sold products
    
    # clear cart
    
    # send order received email to customer
    
    # send order number and transaction id back to sendData method via jsonResponse method 
    return render(request,'order/payments.html')



@csrf_exempt
def place_order(request,total=0,quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('home')
    
    total =0
    quantity = 0
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity) 
        quantity += cart_item.quantity
    tax = (3*total)/100
    grand_total = total + tax
        
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.pincode = form.cleaned_data['pincode']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            print(order_number)
            data.save()
            
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment_data = {
                'amount': int(grand_total * 100),
                'currency': 'INR',
                'receipt':order_number,
                'payment_capture':'1'
            }
            orderData = client.order.create(data=payment_data)
            print(orderData)
            order_status = orderData['status']
            if order_status == 'created':
                payment_obj = Payment.objects.create(
                    payment_id = orderData['id'],
                    payment_method = 'Razorpay',
                    amount_paid = grand_total,
                    status = 'pending',
                    user = request.user,
            
                )
            data.payment = payment_obj
            data.payment_tracking = orderData['id']
        
            data.save()
            # return JsonResponse({'order_id':orderData['id']})
            
            order = Order.objects.get(user = current_user,is_ordered =False,order_number=order_number)
            # grand_total = str(grand_total)
            context ={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'total_amount':int(order.order_total *100),
                'orderData':orderData
            }
            return render(request,'order/payments.html',context)
        

    else:
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)

        # return redirect('checkout')
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id = order.id)
        
        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity
            
        payment = Payment.objects.get(payment_id = transID)
        context ={
            'order':order,
            'order_products':order_products,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal
        }
        return render(request,'order/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist) :
        return redirect('home')