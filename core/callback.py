#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Ydface'


class Callback:
    def __init__(self):
        self.__callback = {}
        for k in (getattr(self, x) for x in dir(self)):
            if hasattr(k, "method"):
                self.__callback.setdefault(k.method, []).append(k)
            elif hasattr(k, "method_list"):
                for j in k.method_list:
                    self.__callback.setdefault(j, []).append(k)

    ## staticmethod is only used to create a namespace
    @staticmethod
    def callback(method):
        def f(g, m=method):
            g.method = m
            return g
        return f
 
    @staticmethod
    def callback_list(method_list):
        def f(g, ml=method_list):
            g.method_list = ml
            return g
        return f
 
    def dispatch(self, event):
        l = self.__callback[event]
        f = lambda *args, **kargs: \
            map(lambda x: x(*args, **kargs), l)
        return f