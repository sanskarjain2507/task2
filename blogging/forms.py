from django import forms

class UserInfo(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'name':'username','id':'userfield','required':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'name':'password','id':'newpass','required':True}))
    conform_password=forms.CharField(widget=forms.PasswordInput(attrs={'id':'confpass','required':True}))


class BlogInfo(forms.Form):
    image=forms.ImageField()
