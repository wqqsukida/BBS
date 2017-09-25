#!/usr/bin/env python
# -*- coding:utf-8 -*-
#----------------------------------------------
#@version:    ??                               
#@author:   Dylan_wu                                                        
#@software:    PyCharm                  
#@file:    forms.py
#@time:    2017/9/18 23:09
#----------------------------------------------
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from app01 import models
from utils.md5 import encrypt
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class RegisterForm(Form):
    username = fields.CharField(
        required=True,
        error_messages={'required': '*用户名不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'id':'user-name'
                                        })
    )
    email = fields.EmailField(
        required=True,
        error_messages={'required': '*邮箱不能为空', 'invalid': '*邮箱格式错误'},
        widget=widgets.EmailInput(attrs={'class': 'form-control',
                                         'id':'E-mail'})
    )
    phone = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                       'id':'phone-num'})
    )
    password = fields.CharField(
        required=True,
        error_messages={'required': '*密码不能为空'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control',
                                            'id':'pass-word'})
    )
    password_confirm = fields.CharField(
        required=True,
        error_messages={'required': '*密码不能为空'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control',
                                            'id':'confirm-pwd'})
    )

    def clean_username(self):
        value = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=value).count():
            raise ValidationError('用户名已经存在')
        return value

    def clean_phone(self):
        # 去取用户提交的值：可能是错误的，可能是正确
        value = self.cleaned_data.get('phone')
        mobile_re = re.compile(r'^(1[358][0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
        if not mobile_re.match(value):
            raise ValidationError('手机号码格式错误')

        if models.UserInfo.objects.filter(phone=value).count():
            raise ValidationError('手机号码已经存在')
        return value

    def clean(self):
        pwd = self.cleaned_data.get('password')
        pwd_confirm = self.cleaned_data.get('password_confirm')
        if pwd == pwd_confirm:
            return self.cleaned_data
        else:
            from django.core.exceptions import ValidationError
            # self.add_error('password', ValidationError('密码输入不一致'))
            self.add_error('password_confirm', ValidationError('密码输入不一致'))
            return self.cleaned_data

class LoginForm(Form):
    username = fields.CharField(
        required=True,
        error_messages={'required': '*用户名不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'id':'user-name'
                                        })
    )
    password = fields.CharField(
        required=True,
        error_messages={'required': '*密码不能为空'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control',
                                            'id':'pass-word'})
    )

    def clean(self):
        user = self.cleaned_data.get('username')
        pwd = encrypt(self.cleaned_data.get('password','0'))

        if models.UserInfo.objects.filter(username=user,password=pwd).count() == 1:
            return self.cleaned_data
        else :
            self.add_error('password', ValidationError('用户名或密码错误！'))
            return self.cleaned_data

class PublishForm(Form):
    url = fields.CharField(
        required=True,
        error_messages={'required': '*URL不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'id':'url-tag'
                                        })
    )
    title = fields.CharField(
        required=True,
        error_messages={'required': '*标题不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'id':'title-tag'
                                        })
    )
    avatar = fields.CharField(
        required=True,
        error_messages={'required': '*请上传图片'},
        widget=widgets.TextInput(attrs={'style': 'display:none',
                                        'id':'avatar-tag'
                                        })
    )
    summary = fields.CharField(
        required=True,
        error_messages={'required': '*摘要不能为空'},
        widget=widgets.Textarea(attrs={'class': 'form-control',
                                        'rows':'5',
                                        'id':'summary-tag'
                                        })
    )
    new_type_id = fields.ChoiceField(
        choices=[],
        widget=widgets.Select(attrs={'class': 'form-control',
                                     'id':'new-type'
                                     })
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_type_id'].choices = models.NewsType.objects.values_list('id', 'caption')