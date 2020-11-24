from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from django.db import transaction
from bs4 import BeautifulSoup
import json, os
from blog_project import settings
from blog.utils import valid_code
from blog.models import *
from blog.myforms import *


# Create your views here.


def login(request):
    # 基于用户认证组件实现
    if request.method == 'POST':
        # post请求
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')  # 拿到用户输入的随机验证码
        valid_code_str = request.session.get('valid_code_str')  # 拿到保存在cookie里的验证码
        data = {'user': None, 'msg': None}
        # 拿到数据与数据库的auth_user表进行比对
        if valid_code.upper() == valid_code_str.upper():  # 判断验证码是否通过
            user = auth.authenticate(username=user, password=pwd)  # 利用用户认证组件校验
            if user:
                auth.login(request, user)  # request.user == 当前登录对象
                data['user'] = user.username
            else:
                data['msg'] = '账号或密码错误！'
        else:
            data['msg'] = '验证码错误！'
        return JsonResponse(data)

    return render(request, 'login.html')


def get_validCode_img(request):
    """
    生成随机图片验证码
    :param request:
    :return:
    """

    data = valid_code.get_valid_code_img(request)
    return HttpResponse(data)


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    auth.logout(request)  # 基于用户认证组件实现注销
    return redirect('/login/')


def register(request):
    """
    注册
        get请求：响应注册页面
        post请求：校验字段，响应字典
    :param request:
    :return:
    """

    if request.is_ajax():  # 是否是ajax请求
        form = UserForm(request.POST)
        response = {'usre': None, 'msg': None}
        if form.is_valid():
            response['user'] = form.cleaned_data.get('user')
            # 生成一条用户纪录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')  # 获取文件对象
            extra = {}
            if avatar_obj:  # 如果有头像
                extra['avatar'] = avatar_obj
            # 创建用户对象
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            print('msg', form.errors)
            response['msg'] = form.errors  # 返回错误信息
        return JsonResponse(response)

    form = UserForm()  # 利用forms组件渲染标签
    return render(request, 'register.html', {'form': form})


def index(request):
    """
    首页
    :param request:
    :return:
    """
    article_list = Article.objects.all()  # 文章列表
    return render(request, 'index.html', {'article_list': article_list})


def home_site(request, username, **kwargs):
    """
    个人站点页
    :param username:用户名
    :param kwargs:剩余数据，有则为跳转页面
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()  # 当前用户
    if not user:  # 判断用户（站点）是否存在
        return render(request, 'not_found.html')
    blog = user.blog
    article_list = Article.objects.filter(user=user)  # 文章列表

    if kwargs:  # 判断是否是跳转
        condition = kwargs.get('condition')  # 跳转方式
        param = kwargs.get('param')  # 参数

        if condition == 'tag':  # 标签
            article_list = article_list.filter(tags__title=param)
        elif condition == 'category':  # 分类
            article_list = article_list.filter(category__title=param)
        else:
            year, month = param.split('-')  # 归档
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    return render(request, 'home_site.html', {'username': username, 'article_list': article_list, 'blog': blog})


def article_detail(request, username, article_id):
    """
    文章详情
    :param request:
    :param username: 登录用户
    :param article_id: 文章id
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog  # 博客
    article_obj = Article.objects.filter(pk=article_id).first()  # 文章
    comment_list = Comment.objects.filter(article_id=article_id)  # 评论
    return render(request, 'article_detail.html', {
        'article_obj': article_obj, 'username': username, 'blog': blog, 'comment_list': comment_list
    })


def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """
    article_id = request.POST.get('article_id')  # 文章id
    is_up = json.loads(request.POST.get('is_up'))  # 是否是点赞
    user_id = request.user.pk
    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()  # 检测该用户是否对该文章操作过
    response = {'state': True}
    if not obj:  # 没有操作过
        ArticleUpDown.objects.create(is_up=is_up, user_id=user_id, article_id=article_id)  # 生成点赞纪录
        if is_up:  # 判断是否是点赞
            Article.objects.update(up_count=F('up_count') + 1)  # 文章点赞数+1
        else:
            Article.objects.update(down_count=F('down_count') + 1)  # 文章反对数+1
    else:
        response['state'] = False
        response['handled'] = obj.is_up  # 将该用户之前的操作发送给客户端

    return JsonResponse(response)


def comment(request):
    """
    评论
    :param request:
    :return:
    """

    content = request.POST.get('content')  # 内容
    article_id = request.POST.get('article_id')  # 文章id
    parent_comment_id = request.POST.get('parent_comment_id')  # 父评论
    user_id = request.user.pk
    article_obj = Article.objects.filter(pk=article_id).first()
    # 事务操作，同进同退
    with transaction.atomic():
        Comment.objects.create(  # 生成评论对象
            content=content,
            article_id=article_id,
            parent_comment_id=parent_comment_id,
            user_id=user_id,
        )
        Article.objects.filter(nid=article_id).update(comment_count=F('comment_count') + 1)  # 文章评论数+1
    response = {}

    response['content'] = content
    response['username'] = request.user.username

    return JsonResponse(response)


def get_comment_tree(request):
    """
    评论树
    :param request:
    :return:
    """
    article_id = request.GET.get('article_id')
    response = list(Comment.objects.filter(article_id=article_id).order_by('pk').values(
        'pk', 'content', 'parent_comment_id'
    ))  # 获取评论列表，进行分组，只取三个字段
    return JsonResponse(response, safe=False)  # 传非字典数据要加safe=False


@login_required
def cn_backend(request):
    """
    后台管理
    :param request:
    :return:
    """
    user = request.user
    article_list = Article.objects.filter(user_id=user.nid).all()
    return render(request, 'backend/cn_backend.html', {'article_list': article_list})


def get_soup(content):
    """
    使用BeautifulSoup进行过滤和提取文本
    :param content:内容
    :return:
    """
    soup = BeautifulSoup(content, 'html.parser')
    # 防止xss攻击,过滤script标签
    for tag in soup.find_all():
        if tag.name == 'script':
            tag.decompose()

    # 构建摘要数据,获取标签字符串的文本前150个符号
    desc = soup.text[0:150] + '...'
    return {'soup': soup, 'desc': desc}


@login_required
def add_article(request):
    """
    后台添加文章
    :param request:
    :return:
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        dic = get_soup(content)  # 数据通过BeautifulSoup进行处理
        Article.objects.create(title=title, content=str(dic.get('soup')), desc=dic.get('desc'), user=request.user)
        return redirect('/cn_backend/')
    return render(request, 'backend/add_article.html')


def upload(request):
    """
    添加文章时上传文件
    :param request:
    :return:
    """
    img_obj = request.FILES.get('upload_img')  # 上传的文件对象
    path = os.path.join(settings.MEDIA_ROOT, 'add_article_img', img_obj.name)  # 拼接路径
    with open(path, 'wb')as f:  # 将文件进行保存
        for line in img_obj:
            f.write(line)
    response = {
        'error': 0,
        'url': '/media/add_article_img/%s' % img_obj.name,
    }  # 返回固定格式
    return HttpResponse(json.dumps(response))


@login_required
def del_article(request, article_id):
    """
    后台删除文章
    :param request:
    :param article_id: 文章id
    :return:
    """
    article_obj = Article.objects.filter(pk=article_id).first()
    article_obj.tags.clear()  # 解除和tag的多对多关系
    article_obj.delete()  # 删除文章对象
    return redirect('/cn_backend/')


@login_required
def change_article(request, article_id):
    """
    后台修改文章
    :param request:
    :param article_id: 文章id
    :return:
    """
    article_obj = Article.objects.filter(pk=article_id).first()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        dic = get_soup(content)  # 数据通过BeautifulSoup进行处理
        Article.objects.filter(pk=article_id).update(title=title, content=str(dic.get('soup')), desc=dic.get('desc'))
        return redirect('/cn_backend/')
    return render(request, 'backend/change_article.html', {'arctile_obj': article_obj})
