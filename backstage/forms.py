from captcha.fields import CaptchaField
from django import forms

FORM_CONTROL = {'class': 'form-control'}


class ManagerLoginForm(forms.Form):
    email = forms.EmailField(label='EMAIL', widget=forms.TextInput(attrs=FORM_CONTROL))
    password = forms.CharField(label='PASSWORD', widget=forms.PasswordInput(attrs=FORM_CONTROL))
    captcha = CaptchaField(label='验证码')

