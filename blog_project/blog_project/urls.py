"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from blog import views
from blog_project import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),  # 登录
    path('logout/', views.logout),  # 退出
    path('get_validCode_img/', views.get_validCode_img),  # 获取随机验证图片
    path('register/', views.register),  # 注册
    path('index/', views.index),  # 首页
    path('digg/', views.digg),  # 点赞
    path('comment/', views.comment),  # 评论
    path('get_comment_tree/', views.get_comment_tree),  # 评论树
    path('cn_backend/', views.cn_backend),  # 后台管理
    path('cn_backend/add_article/', views.add_article),  # 后台添加文章
    path('upload/', views.upload),  # 添加文章时上传图片

    re_path('^$', views.index),  # 首页
    # 个人站点
    re_path(r'^(?P<username>\w+)/$', views.home_site),

    # 个人站点跳转
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),

    # 文章详情
    re_path(r'(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.article_detail),

    # media配置:
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # 后台删除文章
    re_path(r'cn_backend/del_article/(?P<article_id>\d+)/$', views.del_article),

    # 后台修改文章
    re_path(r'cn_backend/change_article/(?P<article_id>\d+)/$', views.change_article),
]
