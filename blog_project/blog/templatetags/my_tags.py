from django import template
from django.db.models import Count
from blog.models import *
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag("classification.html")
def get_classification_style(username):
    """
    获取分类样式
    :param username:
    :return:
    """

    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog  # 站点信息

    # 每一个后的表模型.objects.values("pk").annotate(聚合函数(关联表__统计字段)).values("表模型的所有字段以及统计字段")
    # 查询当前站点的每一个分类名称以及对应的文章数
    category_count = Category.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list(
        'title', 'c')

    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_count = Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list('title', 'c')

    # 查询当前站点每一个年月的名称以及对应的文章数

    date_list = Article.objects.filter(user=user).annotate(month=TruncMonth('create_time')).values('month').annotate(
        c=Count('nid')).values_list('month', 'c')

    return {'user': user, 'blog': blog, 'category_count': category_count, 'tag_count': tag_count,
            'date_list': date_list}
