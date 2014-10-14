#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Ydface'

import struct


class MsgPack(object):
    HEADER_LENGTH = 14

    def __init__(self, msg_id=0, msg="", **kwargs):
        super(MsgPack, self).__init__()

        self.msgId = msg_id
        self.clientId = kwargs.get("client_id", 0)
        self.playerId = kwargs.get("player_id", 0)
        self.msg = msg
        self.length = self.msg.__len__() + MsgPack.HEADER_LENGTH

    def packMsg(self):
        data = struct.pack('<ih2i', self.length, self.msgId, self.clientId, self.playerId)
        data += self.msg
        return data


class MsgBuff(object):
    def __init__(self):
        super(MsgBuff, self).__init__()
        self.buff = ""

    def receiveData(self, data):
        self.buff += data

    def unpackMsg(self):
        if self.buff.__len__() >= MsgPack.HEADER_LENGTH:
            header = self.buff[:MsgPack.HEADER_LENGTH]
            try:
                (length, msg_id, client_id, pid) = struct.unpack('<ih2i', header)
            except Exception, e:
                return None

            if self.buff.__len__() < length:
                return None

            msgpack = MsgPack(msg_id, self.buff[MsgPack.HEADER_LENGTH:length], client_id=client_id, player_id=pid)
            self.buff = self.buff[length:]
            return msgpack
        else:
            return None



