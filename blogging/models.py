from django.db import models

class User_data(models.Model):
    username=models.CharField(max_length=200,primary_key=True,default=None)
    password=models.CharField(max_length=300,default=None)

class Blog(models.Model):
    username=models.ForeignKey(User_data,on_delete=models.CASCADE)
    description=models.CharField(max_length=3000,default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    scope=models.CharField(max_length=20,default=None)
    image=models.ImageField(upload_to='blogging/media')