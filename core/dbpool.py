#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Ydface'


import MySQLdb
from twisted.python import log
import myglobal


class ConnHelper(object):
    def __init__(self):
        super(ConnHelper, self).__init__()

        self.conn = None

    def __enter__(self):
        self.conn = myglobal.dbpool.getConn()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            myglobal.dbpool.releaseConn(self.conn)
        self.conn = None

    @staticmethod
    def getConn():
        return ConnHelper()


class DBPool(object):
    def __init__(self,size=10):
        super(DBPool, self).__init__()
        self._conns = []
        self.maxConn = size

        for i in range(0,self.maxConn):
            self.initDBConn()
        log.msg("This is %d connector in db pool" % len(self._conns))

    def initDBConn(self):
        try:
            conn=MySQLdb.connect(host='115.182.10.206',user='root',passwd='haoyou@beijing',db='feiwan_account',port=3306)
            self._conns.append(conn)
        except MySQLdb.Error, e:
            log.msg("Mysql error [%d : %s]" % (e.args[0], e.args[1]))

    def getConn(self):
        conn = None
        if not self._conns:
            self.initDBConn()
        if self._conns:
            conn = self._conns[0]
            del self._conns[0]
            log.msg("This is %d connector in db pool" % len(self._conns))
        return conn

    def releaseConn(self, conn):
        if not (conn in self._conns) and (len(self._conns) < self.maxConn):
            self._conns.append(conn)
            log.msg("This is %d connector in db pool" % len(self._conns))
        else:
            conn.close()