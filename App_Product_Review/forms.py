from django import forms
from django.core.validators import MinLengthValidator
from .models import Product,Review
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username",
        validators=[MinLengthValidator(8, message="Username must be at least 8 characters long.")]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Username',
            'email': 'Email address',
        }
        help_texts = {
            'username': 'Minimum 8 characters',  # Removes the help text for the username
            'email': None,  # Removes the help text for the email
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput, required=True)
    confirm_new_password = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match!")
        return cleaned_data
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description','brand', 'category', 'price',  'image']


class ReviewForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your review here'}),
        required=True
    )

    class Meta:
        model = Review
        fields = ['description', 'rating']