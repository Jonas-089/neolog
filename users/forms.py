from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# used to override UserCreationForm to add an email adress to the form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    # specifies with which model the form interacts with (user)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    # specifies with which model the form interacts with (user)
    class Meta:
        model = User
        fields = ['username', 'email']
