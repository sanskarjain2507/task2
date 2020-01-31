from django.shortcuts import render
from .forms import UserInfo,BlogInfo
from .models import User_data,Blog
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from cryptography.fernet import Fernet
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import base64,traceback
import random


#this method defines encryption method used for password storage
def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

#this method decode the password retrived from database for verification
def decrypt(txt):
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None



# This method render user to login page(or starting page of this site)
def login_page(request):
    return render(request,'blogging/login.html')


#This method is called whenever request to register user is made
def register_user(request):
    form=UserInfo(request.POST)
    #next few lines defines code for generating simple arithmatic captcha
    num1=random.randint(0,10)
    num2=random.randint(0,10)
    num=num2
    if num2>num1:
        num2=num1
        num1=num

    oprs=['+','-','*']
    opr=random.choice(oprs)
    captcha=str(num1)+opr+str(num2)
    result=eval(captcha)
    param={'form':form,'result':result,'captcha':captcha}
    return render(request,'blogging/registration.html',param)



#This method validates whether theusername is present in databse or not through AJAX calls
def validate_username(request):
    username = request.POST.get('username',None)

    data = {
        'is_taken': User_data.objects.filter(username=username).exists()

    }
    return JsonResponse(data)

#This method is called to store data in the database
@csrf_exempt
def register_success(request):
    if request.method == 'POST':
        form=UserInfo(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            en_pass=encrypt(password)
            user=User_data(username=username,password=en_pass)
            user.save()
            User.objects.create_user(username=username,password=password)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            param={'username':username}
            return render(request,'blogging/homepage.html',param)
        else:
            return HttpResponse('Invalid form details ')

#this method check and validate user on login
@csrf_exempt
def on_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    isUser = User_data.objects.filter(username=username).exists() #checking if user exist or not
    if isUser != False:
            users = User_data.objects.all()
            for u in users:
                if u.username == username:

                    if decrypt(u.password) == password:
                        user = authenticate(request, username=username, password=password)  #authenticating user here
                        if user == None:
                            User.objects.create_user(username=username, password=password)  #if user is not logged in before then logging in the user
                            user = authenticate(request, username=username, password=password)
                        if user is not None:
                            request.session['logged_user'] = username
                            login(request, user)
                        if(Blog.objects.filter(username=username).exists()):
                            userblogs=Blog.objects.filter(username=username).order_by('-timestamp')    #extracting blogs of users and ordering then in decreasing order of timestamp
                            params = {'username': username,'blogs':userblogs,'has_blogs':'yes'}
                            return render(request, 'blogging/homepage.html', params)
                        else:
                            params = {'username': username,'has_blogs': 'no'}
                            return render(request, 'blogging/homepage.html', params)
                    else:
                        return render(request, 'blogging/login.html', {'pass_error': 'Incorrect Password'})  #in case of wrong password user is directed back to login page with a error message

    else:
        return render(request,'blogging/login.html', {'user_error': 'Invalid Username'}) #in case of wrong username user is directed back to login page with a error message

#This method is used to redirct user to fill form to register a blog
@login_required()
def create_blog(request):
    username=request.GET.get('username')
    form=BlogInfo(request.POST)
    param={'username':username,'form':form}
    return render(request,'blogging/blog_registration.html',param)


#This method will submit the blog and save it in database
@login_required()
@csrf_exempt
def submit_blog(request):
    username=request.POST.get('username')
    description=request.POST.get('description')
    scope=request.POST.get('scope') #scope define whether blog is public or private
    form=BlogInfo(request.POST,request.FILES)
    user=User_data.objects.filter(username=username)[0]
    if form.is_valid():
        image=form.cleaned_data['image']
    blog=Blog(description=description,image=image,scope=scope)
    blog.username=user
    blog.save()
    user_blogs=Blog.objects.filter(username=username).order_by('-timestamp')
    param={'username':username,'blogs':user_blogs,'has_blogs':'yes'}
    return render(request,'blogging/homepage.html',param)  #After submitting user will be directed back in homepage

#This method defines the functionality of homepage
@csrf_exempt
@login_required()
def homepage(request):
    username=request.GET.get('username')
    if (Blog.objects.filter(username=username).exists()):
        userblogs = Blog.objects.filter(username=username).order_by('-timestamp')
        params = {'username': username, 'blogs': userblogs, 'has_blogs': 'yes'}
        return render(request, 'blogging/homepage.html', params)
    else:
        params = {'username': username, 'has_blogs': 'no'}
        return render(request, 'blogging/homepage.html', params)

# This method is called whenever a user make search for another user
@login_required()
def user_search(request):
    username=request.GET.get('username')
    search_user=request.GET.get('srch')
    if User_data.objects.filter(username=search_user).exists(): #if user exits then his public blogs will be shown if he had any
        if (Blog.objects.filter(username=search_user).exists()):
            userblogs = Blog.objects.filter(username=search_user,scope='public').order_by('-timestamp')
            params = {'username': username, 'blogs': userblogs, 'has_blogs': 'yes','guest_username':search_user}
            return render(request, 'blogging/guest_blogs.html', params)
        else:
            params = {'username': username, 'has_blogs': 'no'}
            return render(request, 'blogging/guest_blogs.html', params)
    else:
        params={'username':username,'user':'absent'}
        return render(request, 'blogging/guest_blogs.html', params) # in case of invalid username user is marked absent

#This method log out a user
@login_required()
def user_logout(request):
        logout(request)
        username = request.GET.get('username')
        print(username)
        User.objects.get(username=username).delete()
        return render(request, 'blogging/login.html')
