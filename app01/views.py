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
            user_id = user_dict['user_id']
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

from utils.response import BaseResponse,LikeResponse
from django.db import transaction

@auth
def digg(request):
    if request.method == "POST":
        response = LikeResponse()
        try:
            new_id = request.POST.get('new_id')
            user_id = request.session.get('is_login', None).get('user_id')
            with transaction.atomic(): # 以事务的方式提交
                if not Like.objects.filter(news_id=new_id,user_id=user_id):
                    News.objects.filter(id=new_id).update(like_count=F('like_count')+1)
                    Like.objects.create(news_id=new_id,user_id=user_id)
                    response.code = 'digg_up'
                else:
                    News.objects.filter(id=new_id).update(like_count=F('like_count') - 1)
                    Like.objects.filter(news_id=new_id, user_id=user_id).delete()
                    response.code = 'digg_down'
        except Exception as e :
            response.msg = str(e)
        else:
            response.status = True

        print(response.get_dict())
        return HttpResponse(json.dumps(response.get_dict()))



def build_comment_data(li):
    dic = {}
    for item in li:
        item['children'] = []
        item['ctime'] = item['ctime'].strftime('%Y-%m-%d %X')
        dic[item['id']] = item

    result = []
    for item in li:
        pid = item['parent_id']
        if pid:
            dic[pid]['children'].append(item)
        else:
            result.append(item)

    return result

def build_comment_tree(com_list):
    """
l = [{'parent_id': None, 'ctime': None, 'id': 1, 'commenter_id__username': '艾泽拉斯国家地理', 'content': '这是最新回复1', 'children': [
    {'parent_id': 1, 'ctime': None, 'id': 3, 'commenter_id__username': 'user02', 'content': '这是最新回复1-1', 'children': [
        {'parent_id': 3, 'ctime': None, 'id': 5, 'commenter_id__username': 'Dylan', 'content': '这是最新回复1-1-1', 'children': []},
        {'parent_id': 3, 'ctime': None, 'id': 6, 'commenter_id__username': 'Elaine', 'content': '这是最新回复1-1-2', 'children': []}]},
    {'parent_id': 1, 'ctime': None, 'id': 4, 'commenter_id__username': 'user03', 'content': '这是最新回复1-2', 'children': []}]},
     {'parent_id': None, 'ctime': None, 'id': 2, 'commenter_id__username': 'user01', 'content': '这是最新回复2', 'children': []}]

    """
    tpl = """
    <ul class="comment-list">
        <li class="comment-reply">
            <div class="comment-R comment-R-top" >
                <a class="name" href="">{0}:</a>
                <span class="p3">{1}</span>
                <span class="into-time into-time-top">发布时间：{2}</span>
                <a class="reply-user" comid={3}>【回复】</a>
            </div>
        </li>
        {4}
    </ul>
    """
    html = ""
    for item in com_list:
        ctime = item['ctime'].strftime('%Y-%m-%d %X')
        if not item['children']:
            html +=tpl.format(item['commenter_id__username'],item['content'],ctime,item['id'],"")
        else:
            html +=tpl.format(item['commenter_id__username'], item['content'],ctime,item['id'], build_comment_tree(item['children']))
    return html

def comment_list(request):
    """
    获取多级评论列表
    :param request:
    :return:
    """
    new_id = request.POST.get('new_id')
    li =  Comment.objects.filter(comment_new_id=new_id).values('id','content','ctime','commenter_id__username','parent_id').order_by('-ctime')
    '''
    li = [{'ctime': None, 'commenter_id__username': '艾泽拉斯国家地理', 'id': 1, 'content': '这是最新回复1', 'parent_id': None},
          {'ctime': None, 'commenter_id__username': 'user01', 'id': 2, 'content': '这是最新回复2', 'parent_id': None},
          {'ctime': None, 'commenter_id__username': 'user02', 'id': 3, 'content': '这是最新回复1-1', 'parent_id': 1},
          {'ctime': None, 'commenter_id__username': 'user03', 'id': 4, 'content': '这是最新回复1-2', 'parent_id': 1},
          {'ctime': None, 'commenter_id__username': 'Dylan', 'id': 5, 'content': '这是最新回复1-1-1', 'parent_id': 3},
          {'ctime': None, 'commenter_id__username': 'Elaine', 'id': 6, 'content': '这是最新回复1-1-2', 'parent_id': 3}]
    '''

    com_list = build_comment_data(li)
    """
    {'user': '银秋良', 'children': [{'user': '型谱', 'children': [{'user': '银秋良', 'children': [], 'parent_id': 3, 'content': '你是流氓', 'id': 5}], 'parent_id': 1, 'content': '你个文盲', 'id': 3}], 'parent_id': None, 'content': '灌我鸟事', 'id': 1}
    {'user': '银秋良', 'children': [{'user': '详解', 'children': [], 'parent_id': 2, 'content': '好羡慕你们这些没脸的人呀', 'id': 4}], 'parent_id': None, 'content': '管我鸟事', 'id': 2}
    """
    # print(com_list)
    # html = build_comment_tree(com_list)
    # return render(request,'index.html',{'comment_html':html})
    return HttpResponse(json.dumps(com_list))

def add_pub(request):
    response = BaseResponse()

    try:

        comment_new_id = request.POST.get('comment_new_id')
        commenter_id = request.POST.get('commenter_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id',None)
        print(comment_new_id,commenter_id,content)
        with transaction.atomic():  # 以事务的方式提交

            News.objects.filter(id=comment_new_id).update(comment_count=F('comment_count') + 1)
            Comment.objects.create(comment_new_id=comment_new_id,
                                   commenter_id=commenter_id,
                                   content=content,
                                   parent_id=parent_id
                                   )

    except Exception as e:
        response.msg = str(e)

    else:
        response.status = True

    print(response.get_dict())
    return HttpResponse(json.dumps(response.get_dict()))