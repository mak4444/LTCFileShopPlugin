from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc.util import *

from functools import partial

from electrum_ltc.transaction import Transaction

import SimpleHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import socket
import SocketServer
from SocketServer     import ThreadingMixIn
import threading
from threading  import *
import cgi
import os, sys, posixpath
import datetime
import time

import FileShop
from FileShop import *



class CmFSHandler(FSHandler):
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID
        global Tx_res
        FileShop.TLock.acquire()
        GRowTransaction = self.RowTransaction
        GFileID = self.FileID
        Tx_res = None
        #quest_obj.emit(SIGNAL('FShopServerSig'))
        #while Tx_res == None:
        #    time.sleep(0.1)
        Tx_res = 1
        Txres = Tx_res
        FileShop.TLock.release()
        return Txres


class FileServer(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print('FileServer IS RUN')
        self.server = ThreadedHTTPServer(('', 8008), CmFSHandler)
        self.server.serve_forever()
       
    def SStop(self):
        print('FileServer IS STOP')
        self.server.shutdown()
        self.server.server_close()
        self.quit()

class FHHandler:
    def stop(self):
        print('FHHandler stop')
        pass

class Plugin(BasePlugin):
    Server = None
    print('FS cmdl Plugin')
    def __init__(self, parent, config, name):
        global FlPrice
        global FlTrFee
        global ReceivAddress
        
        BasePlugin.__init__(self, parent, config, name)

        FileShop.NFlPrice = self.config.get('NFlPrice', FileShop.NFlPrice)
        FileShop.NFlTrFee = self.config.get('NFlTrFee', FileShop.NFlTrFee)

        FileShop.FlPrice = self.config.get('FlPrice', FileShop.FlPrice)
        FileShop.FlTrFee = self.config.get('FlTrFee', FileShop.FlTrFee)

        FileShop.OFlPrice = self.config.get('OFlPrice', FileShop.OFlPrice)
        FileShop.OFlTrFee = self.config.get('OFlTrFee', FileShop.OFlTrFee)

        FileShop.MemPoolLimit = self.config.get('MemPoolLimit', FileShop.MemPoolLimit)       
        
        FileShop.ReceivAddress = self.config.get('ReceivAddress', FileShop.ReceivAddress)
                      
        if(self.Server == None):
            #self.Server = ThreadedHTTPServer(('', 8008), CmFSHandler)
            #self.Server.serve_forever()
            self.Server = FileServer()
            self.Server.start()

           

    #handler = DigitalBitboxCmdLineHandler()
    @hook
    def load_wallet(self, wallet, window):
        print('load_wallet',self, wallet, window)

    def close(self):
        self.Server.SStop()
        #self.server.shutdown()
        #self.server.server_close()
        #self.quit()

    handler = FHHandler()
    
    