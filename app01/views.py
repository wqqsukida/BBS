from django.shortcuts import render,redirect,HttpResponse
from django.db.models import F
from app01.forms import *
from app01.models import *
import json
import os
from utils.md5 import encrypt
from utils.pagination import Page
import requests
from bs4 import BeautifulSoup

def auth(func):
    def wrapper(request,*args,**kwargs):
        session_dict = request.session.get('is_login')
        if session_dict:
            res = func(request,*args,**kwargs)
            return res
        else:
            return HttpResponse("操作前请先登录！")
    return wrapper



def index(request,*args,**kwargs):
    '''
    主页面函数
    :param request:
    :param args:
    :param kwargs: {new_type_id：}
    :return:
    '''
    if request.method=="GET":
        register_form = RegisterForm()
        login_form = LoginForm()
        publish_form = PublishForm()
        search_str = request.GET.get("search_string", "")
        current_type_id = kwargs.get('new_type_id')
        if current_type_id:current_type_id=int(current_type_id)
        news_type_list = NewsType.objects.all()

        news_list = News.objects.filter(**kwargs).order_by('-ctime') # **kwargs <==> new_type_id = kwargs.get('new_type_id')


        try:
            current_page = int(request.GET.get('page_num'))
        except TypeError:
            current_page = 1
        all_count = news_list.count()
        # page_obj = Page(current_page,all_count,'/hosts.html')
        page_obj = Page(current_page, all_count, request.path_info, search_str)
        news_list = news_list[page_obj.start:page_obj.end]
        page_str = page_obj.page_html()

        print(news_list)

        user_dict = request.session.get('is_login', None)
        print(user_dict)
        if user_dict:
            username = user_dict['user']

        return render(request,"index.html",locals())


def register(request):

    if request.method == "POST":
        response = {'status':True,'data':None,'msg':None}
        form = RegisterForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            pwd = form.cleaned_data.pop("password_confirm")
            pwd = encrypt(pwd)
            obj = UserInfo.objects.create(**form.cleaned_data)
            obj.password = pwd
            obj.save()
        else:
            response['status'] = False
            response['msg'] = form.errors
        return HttpResponse(json.dumps(response))


def login(request):
    if request.method == "POST":
        response = {'status': True, 'data': None, 'msg': None}
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('username')
            # pwd = request.POST.get('password',None)
            # pwd = encrypt(pwd) #md5加密密码字符串
            # if UserInfo.objects.filter(username=user,password=pwd).count() == 1:
            user_id = str(UserInfo.objects.get(username=user).id)
            user_email = UserInfo.objects.get(username=user).email
            user_phone = UserInfo.objects.get(username=user).phone

            request.session['is_login'] = {'user': user,'user_id':user_id,
                                           'user_email':user_email,
                                           'user_phone':user_phone}
            response['data']={}
            # else:
            #     response['status'] = False
            #     response['msg']={'password':['*用户名或者密码错误']}
        else:
            response['status']=False
            response['msg']=form.errors
        print(response)
        return HttpResponse(json.dumps(response))
    # elif request.method == "GET":
    #     user_dict = request.session.get('is_login', None)
    #     if user_dict:
    #         username = user_dict['user']
    #         return render(request,'login.html',locals())
    #     else:
    #         return redirect('/index/')

def logout(request):
    del request.session['is_login'] #删除session
    return redirect('/index/')

@auth
def add_news(request):
    if request.method =="GET":
        url = request.GET.get('get_url',None)
        print("URL:",url)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text
            desc = soup.find('meta', attrs={'name': 'description'}).get('content')
            print('Title:',title)
            print('Description:',desc)
            data = {'title': title, 'desc': desc}
        except:
            data = {'title': '没有正确获取到标题', 'desc': '没有正确获取到内容'}
        return HttpResponse(json.dumps(data))
    if request.method == "POST":
        response = {'status':True,'data':None,'msg':None}
        publish_form = PublishForm(request.POST)
        if publish_form.is_valid():

# {'url': 'http://dig.chouti.com/', 'avatar': 'static\\img\\20141120102935_48465.jpg',
#  'summary': '抽屉新..','title': '抽屉..', 'new_type': '1'}
            news_dict = publish_form.cleaned_data

            user_id = request.session.get('is_login',None).get('user_id')

            news_dict.update({'promulgator_id':user_id})
            print(news_dict)
            News.objects.create(**news_dict)

        else:
            response['status'] = False
            response['msg'] = publish_form.errors

        return HttpResponse(json.dumps(response))

@auth
def upload_img(request):
    obj = request.FILES.get('img_data') # 使用FILES接收POST过来的文件
    data = {'status': True,'path': None}
    if obj:
        img_path = os.path.join('static', 'img', obj.name) # 拼接保存路径

        with open(img_path, mode='wb') as f: # 写入路径
            for chunk in obj.chunks():
                f.write(chunk)
        data['path'] = img_path
    else:
        data['status'] = False
    print('ImgPath:',data['path'])
    return HttpResponse(json.dumps(data))

@auth
def digg(request):
    if request.method == "POST":
        response = {'status': True, 'data': None, 'msg': None}
        new_id = request.POST.get('new_id')
        user_id = request.session.get('is_login', None).get('user_id')
        if not Like.objects.filter(news_id=new_id,user_id=user_id):
            News.objects.filter(id=new_id).update(like_count=F('like_count')+1)
            Like.objects.create(news_id=new_id,user_id=user_id)
            response['msg'] = ''
        else:
            response['msg'] = ''
            response['status'] = False
        print(response)
        return HttpResponse(json.dumps(response))
