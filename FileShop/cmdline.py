from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc.util import *
from electrum_ltc.network import Network
from electrum_ltc.exchange_rate import FxThread


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

Bnetwork = None

class CmFSHandler(FSHandler):

    def Tx_test(self):
        global GRowTransaction
        global GFileID
        try:
            XTr = Transaction(GRowTransaction)
        except:
            return 0
        #print('XTr = ',XTr)

        Flv , FLfee , TTime = FileShop.FilePP[GFileID]
        if( Flv + FLfee == 0. ):
            return 1      
        try:        
            #is_relevant, is_mine, v, fee = self.window.wallet.get_wallet_delta(XTr)
            InputAdrs = {}
            for x in XTr.inputs():
                InputAdrs[x['address']]=None

            netw = Network(None)
            netw.start()

            for x in InputAdrs:
                InputAdrs[x]=netw.synchronous_get(('blockchain.address.listunspent', [x]))

            netw.stop()

            fee = 0
            amount = 0

            for x in XTr.inputs():
                print(InputAdrs[x['address']] )
                for y in InputAdrs[x['address']]:
                    if y['tx_hash'] == x['prevout_hash']:
                        fee += int( y['value'])

            amount = 0
            for addr, value in XTr.get_outputs():
                print('get_outputs=',addr, value , FileShop.ReceivAddress )
                fee -= value
                if addr == FileShop.ReceivAddress:
                    amount += value

        except:
            return 0
                         
        #fee = amount - XTr.output_value()
        
        #self.window.show_transaction(XTr, u'')
        print("amount, fee =",amount, fee, Flv , FLfee , TTime, len(GRowTransaction) )
        print("dFlv =",Flv * 10.**8 , FLfee * 10.**8  , fee * 1000. / (len(GRowTransaction)/2)  )
        dFlv = abs (Flv * 10.**8 - amount )
        dFLfee = abs (FLfee * 10.**8  - fee * 1000. / (len(GRowTransaction)/2)  )
        print("dFlv =",dFlv,dFLfee ,Flv * 10.**8 , FLfee * 10.**8  , fee * 1000. / (len(GRowTransaction)/2)  )
        if( dFLfee + dFlv < 1000 ):
            print('Tx_res = 1')
            return 1       
        
        return 0
        
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID

        #FileShop.TLock.acquire()
        GRowTransaction = self.RowTransaction
        GFileID = self.FileID

        #print('TransactionTst=', GRowTransaction )

        Txres = self.Tx_test()
        return Txres
    '''
    def list_directory(self, path):
        global Bnetwork
        print('list_directory=', path)
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>File Shop  displaypath</title>\n" )
        f.write("<body>\n<h2>The running <a href=\"https://github.com/mak4444/LTCFileShopPlugin\">Electrum-ltc plugin</a> is needed for downloading</h2>\n")
        f.write('%s\n'%(path))
        netw = Network(None)
        netw.start()
        yyy = netw.synchronous_get(('blockchain.address.listunspent', ['LLuggsZhhkqyuyXKCjCZjmP6fFX2EgcDaa']))
        f.write('address.list=%s'%(yyy))

        print('address.list=', yyy)
        netw.stop()
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f
    '''

class FileServer(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print('FileServer IS RUN')
        network = Network(None)
        network.start()

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
        print('FS cmdl Plugin ini')
        global FlPrice
        global FlTrFee
        global ReceivAddress
	global Bnetwork
        
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
            self.Server = FileServer()
            self.Server.start()

        '''    
        Bnetwork = Network(config)
        Bnetwork.start()
        #self.fx = FxThread(config, Bnetwork)
        #Bnetwork.add_jobs([self.fx])
        nettt = Bnetwork.synchronous_get(('blockchain.address.listunspent', ['Le9vkf1ZiC8A6wF9HHaEJ28cLD1EiwzPef']))
        print('address.list=', nettt )
        #Bnetwork.stop()
        '''
    
    def close(self):
        self.Server.SStop()
        #self.server.shutdown()
        #self.server.server_close()
        #self.quit()

    handler = FHHandler()
    
    