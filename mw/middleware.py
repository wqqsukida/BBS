#!/usr/bin/env python
# -*- coding:utf-8 -*-
#----------------------------------------------
#@version:    ??                               
#@author:   Dylan_wu                                                        
#@software:    PyCharm                  
#@file:    middleware.py
#@time:    2017/9/19 13:58
#----------------------------------------------
from django.shortcuts import HttpResponse,redirect

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class AuthMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        print('m1.process_request')

    def process_response(self,request, response):
        print('m1.prcess_response')
        return response