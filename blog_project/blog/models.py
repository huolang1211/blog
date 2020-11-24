from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class UserInfo(AbstractUser):
    """用户信息表"""

    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)  # 手机号，最多11位，可以为空
    email = models.EmailField()
    avatar = models.FileField(upload_to='avatars/', default='/avatars/default.png')  # 头像，文件路径，初始文件
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)  # 创建时间，自动添加当前时间

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)  # 与Blog表一对一，关联字段为nid

    def __str__(self):
        return self.username


class Blog(models.Model):
    """博客信息表（站点表）"""

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=64)

    def __str__(self):
        return self.title


class Category(models.Model):
    """博客个人文章分类表"""

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to=Blog, to_field='nid', on_delete=models.CASCADE)  # 多对一关联Blog

    def __str__(self):
        return self.title


class Tag(models.Model):
    """博客个人文章标签表"""

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to=Blog, to_field='nid', on_delete=models.CASCADE)  # 多对一关联Blog

    def __str__(self):
        return self.title


class Article(models.Model):
    """博客个人文章表"""

    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=64)
    desc = models.CharField(verbose_name='文章描述', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)  # 创建时间，自动添加当前时间
    content = models.TextField()  # 文章内容

    user = models.ForeignKey(verbose_name='作者', to=UserInfo, to_field='nid', on_delete=models.CASCADE)  # 多对一关联UserInfo
    category = models.ForeignKey(verbose_name='文章分类', to=Category, to_field='nid', null=True,
                                 on_delete=models.CASCADE)  # 多对一关联Category

    tags = models.ManyToManyField(  # 与文章标签表Tag建立多对多关系
        to='Tag',
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    comment_count = models.IntegerField(default=0)  # 文章评论数
    up_count = models.IntegerField(default=0)  # 文章点赞数
    down_count = models.IntegerField(default=0)  # 文章反对数

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    """博客个人文章与标签关联表"""

    nid = models.AutoField(primary_key=True)

    article = models.ForeignKey(verbose_name='文章', to=Article, to_field='nid', on_delete=models.CASCADE)  # 关联Article
    tag = models.ForeignKey(verbose_name='标签', to=Tag, to_field='nid', on_delete=models.CASCADE)  # 关联Tag

    class Meta:
        """联合唯一"""
        unique_together = [
            ('article', 'tag')
        ]

    def __str__(self):
        return self.article.title + '___' + self.tag.title


class ArticleUpDown(models.Model):
    """博客个人文章点赞表
            哪个用户对哪篇文章进行点赞操作
    """

    nid = models.AutoField(primary_key=True)
    is_up = models.BooleanField(default=True)  # 是否点赞

    user = models.ForeignKey(verbose_name='点赞者', to=UserInfo, to_field='nid', on_delete=models.CASCADE)  # 多对一关联UserInfo
    article = models.ForeignKey(verbose_name='文章', to=Article, to_field='nid', on_delete=models.CASCADE)  # 多对一关联Article

    class Meta:
        """联合唯一"""
        unique_together = [
            ('article', 'user')
        ]


class Comment(models.Model):
    """评论表"""

    nid = models.AutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)  # 是否点赞
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)  # 创建时间，自动添加当前时间

    user = models.ForeignKey(verbose_name='评论者', to=UserInfo, to_field='nid', on_delete=models.CASCADE)  # 多对一关联UserInfo
    article = models.ForeignKey(verbose_name='评论文章', to=Article, to_field='nid',
                                on_delete=models.CASCADE)  # 多对一关联Article
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)  # 自关联

    def __str__(self):
        return self.content
