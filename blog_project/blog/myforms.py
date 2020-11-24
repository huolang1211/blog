from django import forms
from django.forms import widgets
from blog.models import *
from django.core.exceptions import ValidationError

wid_text = widgets.TextInput(attrs={'class': 'form-control'})
wid_date = widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'})
wid_pwd = widgets.PasswordInput(attrs={'class': 'form-control'})
wid_sm = widgets.SelectMultiple(attrs={'class': 'form-control'})
wid_select = widgets.Select(attrs={'class': 'form-control'})
wid_email = widgets.EmailInput(attrs={'class': 'form-control'})


def get_obj(obj_models):
    """
    从数据库取出元素对象
    :param obj_models: 表名
    :return:
    """
    obj_list = obj_models.objects.values()
    p_list = []
    for obj in obj_list:
        item = (obj.get('nid'), obj.get('name'))
        p_list.append(item)
    obj_tuple = tuple(p_list)

    return obj_tuple


class UserForm(forms.Form):
    """用户信息forms组件"""
    user = forms.CharField(
        max_length=32,
        error_messages={'required': '该字段不能为空'},  # 错误信息
        label='用户名',
        widget=wid_text
    )
    pwd = forms.CharField(
        max_length=32,
        error_messages={'required': '该字段不能为空'},  # 错误信息
        label='密码',
        widget=wid_pwd
    )
    re_pwd = forms.CharField(
        max_length=32,
        error_messages={'required': '该字段不能为空'},  # 错误信息
        label='确认密码',
        widget=wid_pwd
    )
    email = forms.EmailField(
        label='邮箱',
        error_messages={'required': '该字段不能为空', 'invalid': '格式错误'},  # 错误信息
        widget=wid_email
    )

    def clean_user(self):
        """
        用户名查重
        :return:
        """
        val = self.cleaned_data.get('user')
        user = UserInfo.objects.filter(username=val).first()  # 在数据库中查找该用户名是否已经存在
        if not user:
            print(user,'user')
            return val

        else:
            raise ValidationError('该用户已注册！')

    def clean(self):
        """
        两次输入的密码是否一致
        :return:
        """
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get(('repwd'))
        if pwd and re_pwd:  # 两次输入都不为空
            if pwd == re_pwd:  # 两次输入是否一致
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致！')
        else:
            return self.cleaned_data



