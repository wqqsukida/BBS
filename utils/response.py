#!/usr/bin/env python
# -*- coding:utf-8 -*-
#----------------------------------------------
#@version:    ??                               
#@author:   Dylan_wu                                                        
#@software:    PyCharm                  
#@file:    response.py
#@time:    2017/9/25 13:00
#----------------------------------------------

class BaseResponse(object):
    def __init__(self):
        self.status = False
        self.data = None
        self.msg = None

    def get_dict(self):
        return self.__dict__


class LikeResponse(BaseResponse):
    def __init__(self):
        self.code = 0
        super(LikeResponse,self).__init__()