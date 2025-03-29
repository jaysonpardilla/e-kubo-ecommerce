from django import forms
from .models import     Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields  = ['profile']

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['province', 'municipality', 'street', 'postal_code']

# class UpdateUser(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'phone']


class UpdateUser(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
        }