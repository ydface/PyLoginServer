#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Ydface'

import sys
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from twisted.internet import reactor
from core.datapack import *
import proto.account_role_pb2
import core.myglobal
import core.dbpool
import MySQLdb

class CmdProtocol(LineReceiver):

    delimiter = '\n'

    def __init__(self):
        self.client_ip = None

    def connectionMade(self):
        self._buffer = MsgBuff()
        self.client_ip = self.transport.getPeer().host
        log.msg("Client connection from %s" % self.client_ip)
        if len(self.factory.clients) >= self.factory.clients_max:
            log.msg("Too many connections. bye !")
            self.client_ip = None
            self.transport.loseConnection()
        else:
            self.factory.clients.append(self.client_ip)
            log.msg("Current client number is %d" % len(self.factory.clients))

    def connectionLost(self, reason):
        log.msg('Lost client connection.  Reason: %s' % reason)
        if self.client_ip:
            self.factory.clients.remove(self.client_ip)
            log.msg("Current client number is %d" % len(self.factory.clients))

    def dataReceived(self, data):
        self._buffer.receiveData(data)
        while True:
            msg = self._buffer.unpackMsg()
            if not msg:
                break
            if msg.msgId == 3:
                rmsg = MsgPack(4)
                data = rmsg.packMsg()
                self.transport.write(data)
            elif msg.msgId == 10002:
                login_proto = proto.account_role_pb2.login_proto()
                login_proto.ParseFromString(msg.msg)
                uname = login_proto.account_name
                upwd = login_proto.account_pwd
                log.msg("User: %s request login with password: %s" % (uname, upwd))

                with core.dbpool.ConnHelper.getConn() as conn:
                    #print conn
                    if not conn:
                        break
                    cur = conn.cursor()
                    cur.execute("select password, feiwan_id from feiwan_account where username='%s'" % uname)
                    true_pwd = cur.fetchone()
                    cur.close()

                    rproto = proto.account_role_pb2.login_res_proto()
                    if not true_pwd:
                        rproto.error_id = 4
                        log.msg("User: %s login failed, user no found" % uname)
                    else:
                        if true_pwd[0] == upwd:
                            rproto.error_id = 3
                            rproto.hoyo_id = true_pwd[1]
                            log.msg("User: %s login succeed" % uname)
                        else:
                            rproto.error_id = 5
                            log.msg("User: %s login failed, input password: %s not match: %s" % (uname, upwd, true_pwd[0]))
                    rmsg = rproto.SerializeToString()
                    msgpack = MsgPack(10002,rmsg, client_id=msg.clientId)
                    msgdata = msgpack.packMsg()
                    self.transport.write(msgdata)





class ServerPool(ServerFactory):

    protocol = CmdProtocol

    def __init__(self, clients_max=500):
        self.clients_max = clients_max
        self.clients = []


def start():
    log.startLogging(sys.stdout)
    reactor.listenTCP(10000, ServerPool())
    log.msg("Login server start...")
    reactor.run()