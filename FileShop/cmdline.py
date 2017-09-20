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
    def __init__(self, request, client_address, server ):
        Bnetwork = Network(None)
        #Bnetwork.start()
        #Bnetwork = network
        print('Bnetwork=',Bnetwork)
        FSHandler.__init__(self, request, client_address, server)
        
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID
        global Tx_res
        global Bnetwork
        FileShop.TLock.acquire()
        GRowTransaction = self.RowTransaction
        GFileID = self.FileID
        Tx_res = None
        #quest_obj.emit(SIGNAL('FShopServerSig'))
        #while Tx_res == None:
        #    time.sleep(0.1)
        xxx = Bnetwork.synchronous_get('blockchain.address.listunspent', ['LfKG665Lcs2mLatwDP9zeZKDuVy4whJQUd'])
        print('address.list=', xxx )

        Tx_res = 1
        Txres = Tx_res
        FileShop.TLock.release()
        return Txres

    def list_directory(self, path):
        global Bnetwork
        print('list_directory=', path)
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>File Shop  displaypath</title>\n" )
        f.write("<body>\n<h2>The running <a href=\"https://github.com/mak4444/LTCFileShopPlugin\">Electrum-ltc plugin</a> is needed for downloading</h2>\n")
        f.write('%s\n'%(path))
        Bnetwork = Network(None)
        Bnetwork.start()
        yyy = Bnetwork.synchronous_get(('blockchain.address.listunspent', ['Le9vkf1ZiC8A6wF9HHaEJ28cLD1EiwzPef']))
        Bnetwork.stop()

        print('address.list=', yyy)
        Bnetwork.stop()
        #f.write('address.list=%s'%( Bnetwork.synchronous_get('blockchain.address.listunspent', ['LfKG665Lcs2mLatwDP9zeZKDuVy4whJQUd'])))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


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
    
    