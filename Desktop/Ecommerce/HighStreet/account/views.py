from django.shortcuts import render,redirect
from .models import CustomUser
from .forms import RegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import messages,auth
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_pass = form.cleaned_data['confirm_password']
            
            if password == confirm_pass:
                user = CustomUser.objects.create_user(
                    username = username,
                    first_name = first_name,
                    last_name = last_name,
                    email = email,
                    password = password,
                    is_active = False
                )
                user.save()
                
                
                #user Activation mail
                
                current_site = get_current_site(request)
                mail_subject = 'Activate your account by verifying your email address'
                message = render_to_string('account/account_activate.html',{
                    'user' : user,
                    'domain' :current_site,
                    'uid' :urlsafe_base64_encode(force_bytes(user.id)),
                    'token' :default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                messages.success(request,'Activation sent to your email')
                
                return redirect('signin')
            messages.error(request,'creadentials not matching')

    else:
        form = RegistrationForm()
            
    context={
        'form': form,
                
        }
    return render(request,'account/register.html',context)            
                

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser._default_manager.get(id = uid)
    except(ValueError, TypeError,OverflowError,CustomUser.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Your account has been activated')
        return redirect('signin')
    else:
        messages.error(request,'invalid activation link')
        return redirect('register')
    

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')   
        password = request.POST.get('password')
        
        user = authenticate(username=email, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            messages.error(request,'invalid credentials')
            return redirect('signin')
    
    return render(request,'account/signin.html')
            
def signout(request):
    auth.logout(request)
    messages.success(request,'logged out')
    return redirect('signin')


def dashboard(request):
    
    return render(request,'account/dashboard.html')

def forgot_password(request):
    if request.method== 'POST':
        email = request.POST.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subject = 'Reset password'
            message = render_to_string('account/reset_password.html',{
                'user' : user,
                'domain' :current_site,
                'uid' :urlsafe_base64_encode(force_bytes(user.id)),
                'token' :default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send() 
            messages.success(request,'Password reset email has been sent to your email')
            return redirect('signin')
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgot_password')
    return render(request,'account/forget_password.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser._default_manager.get(id = uid)
    except(ValueError, TypeError,OverflowError,CustomUser.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'this link has expired!')
        return redirect('signin')
 
def reset_password(request):
    if request.method == 'POST':
        password =request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            uid = request.session.get('uid')
            user = CustomUser.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfully')
            return redirect('signin')
        else:
            messages.error(request,'password not match!')
            return redirect('reset_password')
    return render(request,'account/reset_password_set.html')