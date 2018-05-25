from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc.util import *
from electrum_ltc.network import Network
from electrum_ltc.exchange_rate import FxThread


from functools import partial

from electrum_ltc.transaction import Transaction

import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from socketserver     import ThreadingMixIn
import threading
from threading  import *
import cgi
import os, sys, posixpath
import datetime
import time

import FileShop.FileShop as FFS
from FileShop.FileShop import *

Tx_IOSave = {}
ST4del = []


class CmFSHandler(FSHandler):

    def Tx_test(self):
        global GRowTransaction
        global GFileID
        global ST4del
        global Tx_IOSave

        try:
            XTr = Transaction(GRowTransaction)
        except:
            return 0
        #print('XTr = ',XTr)

        Flv , FLfee , TTime = FFS.FilePP[GFileID]
        if( Flv + FLfee == 0. ):
            return 1
        
        try:
            amount,fee = Tx_IOSave[self.IDTran]
        except:

            if not XTr.is_complete():
                return 0
      
            try:        
                #is_relevant, is_mine, v, fee = self.window.wallet.get_wallet_delta(XTr)

                self.netw = Network(None)               
                self.netw.start()
                 
                InputAdrs = {}
                for x in XTr.inputs():
                    InputAdrs[x['address']]=None
                    for x in InputAdrs:
                        InputAdrs[x]=self.netw.synchronous_get(('blockchain.address.listunspent', [x]))

                fee = 0
                amount = 0

                for x in XTr.inputs():
                    print(InputAdrs[x['address']] )
                    for y in InputAdrs[x['address']]:
                        if y['tx_hash'] == x['prevout_hash']:
                            fee += int( y['value'])

                for addr, value in XTr.get_outputs():
                    print('get_outputs=',addr, value , FFS.ReceivAddress )
                    fee -= value
                    if addr == FFS.ReceivAddress:
                        amount += value

                if len(ST4del) > 9:
                    del Tx_IOSave[ST4del[0]]
                    del ST4del[0]

                Tx_IOSave[self.IDTran] = amount,fee   
                ST4del.append(self.IDTran)        

            except:
                return 0
                         
        dFlv = abs (Flv * 1e8 - amount )
        dFLfee = abs (FLfee * 1e8  - fee * 1000. / (len(GRowTransaction)/2)  )
        if dFLfee + dFlv < 1000 :
            msg = 'MemPoolLimit'
            if amount >  MemPoolLimit * 1e8 :
                status, msg = None,None
                try:
                    status, msg =  self.window.network.broadcast(XTr)
                    print('broadcast_try=',status, msg)
                except:
                    pass            
             
            print('broadcast=',status, msg)

            return 1       
        
        return 0
        
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID

        GRowTransaction = self.RowTransaction
        GFileID = self.FileID

        #print('TransactionTst=', GRowTransaction )
        self.netw = None

        Txres = self.Tx_test()
        if self.netw != None:
            self.netw.stop()

        return Txres

class FileServer(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print('FileServer IS RUN')
        network = Network(None)
        network.start()

        self.server = ThreadedHTTPServer(('', 8008), CmFSHandler)
        self.server.serve_forever()

       
class Plugin(BasePlugin):
    Server = None
    print('FS cmdl Plugin')
    def __init__(self, parent, config, name):
        print('FS cmdl Plugin ini')
        
        BasePlugin.__init__(self, parent, config, name)


        FFS.NFlPrice = self.config.get('NFlPrice', FFS.NFlPrice)
        FFS.NFlTrFee = self.config.get('NFlTrFee', FFS.NFlTrFee)
        FFS.NFlTrFee = self.config.get('NFlTrFee', FFS.NFlTrFee)
        FFS.FlPrice = self.config.get('FlPrice',   FFS.FlPrice)
        FFS.FlTrFee = self.config.get('FlTrFee',   FFS.FlTrFee)
        FFS.OFlPrice = self.config.get('OFlPrice', FFS.OFlPrice)
        FFS.OFlTrFee = self.config.get('OFlTrFee', FFS.OFlTrFee)
        FFS.MemPoolLimit = self.config.get('MemPoolLimit',   FFS.MemPoolLimit)       
        FFS.ReceivAddress = self.config.get('ReceivAddress', FFS.ReceivAddress)

        if self.Server == None :
            self.Server = FileServer()
            self.Server.start()

