from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(choices=[
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant Owner'),
        ('grocery', 'Grocery Owner'),
        ('driver', 'Driver'),
    ], required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                  'phone', 'role', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class': 'input-premium'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'input-premium'
    }))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'profile_pic')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-premium'}),
            'last_name': forms.TextInput(attrs={'class': 'input-premium'}),
            'email': forms.EmailInput(attrs={'class': 'input-premium'}),
            'phone': forms.TextInput(attrs={'class': 'input-premium'}),
            'address': forms.Textarea(attrs={'class': 'input-premium', 'rows': 3}),
        }