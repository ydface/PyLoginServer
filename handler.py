#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Ydface'

from core.callback import Callback

Msg_RequestLogin = 10002


class ServerHandler(Callback):
    @Callback.callback(Msg_RequestLogin)
    def requestLogin(self, params):
        return None

    def run(self, event, params):
        self.dispatch(event)(params)
