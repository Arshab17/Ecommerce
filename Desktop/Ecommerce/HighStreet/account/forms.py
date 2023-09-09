from django import forms
from .models import CustomUser
class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username','first_name','last_name','email','password','confirm_password']
        
        
