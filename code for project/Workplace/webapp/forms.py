from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class form_user(UserCreationForm):
    email = forms.EmailField(required=True)

    TYPE_CHOICES = [
        ("client", "Client"),
        ("freelancer", "Freelancer"),
    ]
    typee = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select, required=True)

    img = forms.ImageField(required=True)

    class Meta:
        model = Custom_user
        fields = ("username", "password1", "password2", "email", "typee", "img")


class form_post(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tags.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Post
        fields = ["title", "text", "pay","tags"]


class verify_account_form(forms.ModelForm):
    class Meta:
        model = Custom_user
        fields = ("university_name", "roll_no")


class tag_creation(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ('string',)
