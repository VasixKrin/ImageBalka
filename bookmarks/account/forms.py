from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat Password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email'].lower()
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use')
        return data

    def clean_username(self):
        data = self.cleaned_data['username'].lower()
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Username already in use')
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        data = self.cleaned_data['email'].lower()
        qs = User.objects.exclude(
            id=self.instance.id
        ).filter(
            email=data
        )
        if qs.exists():
            raise forms.ValidationError('Email already in use')
        return data

    def clean_username(self):
        data = self.cleaned_data['username'].lower()
        qs = User.objects.exclude(
            id=self.instance.id
        ).filter(
            username=data
        )
        if qs.exists():
            raise forms.ValidationError('Username already in use')
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
