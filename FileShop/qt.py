from PyQt4.QtGui import *
from PyQt4.QtCore import *

from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc_gui.qt.util import WindowModalDialog , Buttons , CancelButton, OkButton
from electrum_ltc.util import *
''' (block_explorer, block_explorer_info, format_time,
                               block_explorer_URL, format_satoshis, PrintError,
                               format_satoshis_plain, NotEnoughFunds,
                               UserCancelled)
'''
from electrum_ltc_gui.qt.util import EnterButton, Buttons, CloseButton
from electrum_ltc_gui.qt.util import OkButton, WindowModalDialog
from functools import partial

from electrum_ltc.transaction import Transaction

import SimpleHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import socket
import SocketServer
from SocketServer     import ThreadingMixIn
import threading
import cgi
import os, sys, posixpath
import datetime
import time
from decimal import Decimal

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import FileShop
from FileShop import *

quest_obj = QObject()
GRowTransaction = None
GFileID = None
GIDTran = None
Tx_res = None
Tx_IOSave = {}
ST4del = []


class GFSHandler(FSHandler):
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID
        global GIDTran
        global Tx_res
        
        FileShop.TLock.acquire()
        GRowTransaction = self.RowTransaction
        GIDTran = self.IDTran
        GFileID = self.FileID
        Tx_res = None
        quest_obj.emit(SIGNAL('FShopServerSig'))
        while Tx_res == None:
            time.sleep(0.1)
        Txres = Tx_res
        FileShop.TLock.release()
        return Txres

class FileServer(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.server = ThreadedHTTPServer(('', 8008), GFSHandler)
        #server = HTTPServer(('', 8008), GFSHandler)
        self.server.serve_forever()
       
    def SStop(self):
        self.server.shutdown()
        self.server.server_close()
        self.quit()

class Plugin(BasePlugin):
    global quest_obj
    Server = None
    def __init__(self, parent, config, name):
        self.DefDddr = 'LLuggsZhhkqyuyXKCjCZjmP6fFX2EgcDaa'
        if FileShop.ReceivAddress == '':
            FileShop.ReceivAddress = self.DefDddr

        BasePlugin.__init__(self, parent, config, name)

        FileShop.NFlPrice = self.config.get('NFlPrice', FileShop.NFlPrice)
        FileShop.NFlTrFee = self.config.get('NFlTrFee', FileShop.NFlTrFee)

        FileShop.FlPrice = self.config.get('FlPrice', FileShop.FlPrice)
        FileShop.FlTrFee = self.config.get('FlTrFee', FileShop.FlTrFee)

        FileShop.OFlPrice = self.config.get('OFlPrice', FileShop.OFlPrice)
        FileShop.OFlTrFee = self.config.get('OFlTrFee', FileShop.OFlTrFee)

        FileShop.MemPoolLimit = self.config.get('MemPoolLimit', FileShop.MemPoolLimit)       
        
        FileShop.ReceivAddress = self.config.get('ReceivAddress', FileShop.ReceivAddress)
        
        self.obj = QObject()
        self.obj.connect(quest_obj, SIGNAL('FShopServerSig'), self.Tx_test)

              
        if(self.Server == None):
            self.Server = FileServer()
            self.Server.start()

    def close(self):
        self.Server.SStop()
        
    @hook
    def load_wallet(self, wallet, window):
        #global ReceivAddress 
        self.window = window
        if FileShop.ReceivAddress == self.DefDddr:
            FileShop.ReceivAddress = wallet.dummy_address()

    @hook
    def init_qt(self, gui):
        for window in gui.windows:
            self.window = window
            if FileShop.ReceivAddress == self.DefDddr:
                FileShop.ReceivAddress = self.window.wallet.dummy_address()
            break

    def requires_settings(self):
        return True

    def settings_widget(self, window):
        return EnterButton( ('Settings'), partial(self.settings_dialog, window))

    def settings_dialog(self, window):

        d = WindowModalDialog(window, ("FileShop settings"))
        d.setMinimumSize(500, 200)

        vbox = QVBoxLayout(d)
        #vbox.addWidget(QLabel( ('New Files')))

        grid = QGridLayout()
        vbox.addLayout(grid)

        grid.addWidget(QLabel('New Files'), 0, 1)
        grid.addWidget(QLabel('older hour Files'), 0, 2)
        grid.addWidget(QLabel('older 24 hour Files'), 0, 3)

        grid.addWidget(QLabel('Price'), 1, 0)

        NFlPrice_e = QLineEdit()
        NFlPrice_e.setText("%s"%FileShop.NFlPrice)
        grid.addWidget(NFlPrice_e, 1, 1)

        FlPrice_e = QLineEdit()
        FlPrice_e.setText("%s"%FileShop.FlPrice)
        grid.addWidget(FlPrice_e, 1, 2)

        OFlPrice_e = QLineEdit()
        OFlPrice_e.setText("%s"%FileShop.OFlPrice)
        grid.addWidget(OFlPrice_e, 1, 3)

        grid.addWidget(QLabel('Fee/Kb'), 2, 0)

        NFlTrFee_e = QLineEdit()
        NFlTrFee_e.setText("%s"%FileShop.NFlTrFee)
        grid.addWidget(NFlTrFee_e, 2, 1)

        FlTrFee_e = QLineEdit()
        FlTrFee_e.setText("%s"%FileShop.FlTrFee)
        grid.addWidget(FlTrFee_e, 2, 2)

        OFlTrFee_e = QLineEdit()
        OFlTrFee_e.setText("%s"%FileShop.OFlTrFee)
        grid.addWidget(OFlTrFee_e, 2, 3)


        grid.addWidget(QLabel('mempool limit'), 3, 1)

        MemPoolLimit_e = QLineEdit()
        MemPoolLimit_e.setText("%s"%FileShop.MemPoolLimit)
        grid.addWidget(MemPoolLimit_e, 3, 2)

        grid1 = QGridLayout()
        vbox.addLayout(grid1)


        grid1.addWidget(QLabel('receiv address'), 5, 0)
        ReceivAddress_e = QLineEdit()
        ReceivAddress_e.setText(FileShop.ReceivAddress)
        grid1.addWidget(ReceivAddress_e, 5, 1)

        grid1.addWidget(QLabel('FileShopPath'), 6, 0)
        FileShopPath_e = QLineEdit()
        FileShopPath_e.setText(FileShop.FileShopPath)
        grid1.addWidget(FileShopPath_e, 6, 1)


        vbox.addStretch()
        vbox.addLayout(Buttons(CloseButton(d), OkButton(d)))

        if not d.exec_():
            return


        FileShop.NFlPrice = float(NFlPrice_e.text())
        self.config.set_key('NFlPrice', FileShop.NFlPrice)

        FileShop.NFlTrFee = float(NFlTrFee_e.text())
        self.config.set_key('NFlTrFee', FileShop.NFlTrFee)


        FileShop.FlPrice = float(FlPrice_e.text())
        self.config.set_key('FlPrice', FileShop.FlPrice)

        FileShop.FlTrFee = float(FlTrFee_e.text())
        self.config.set_key('FlTrFee', FileShop.FlTrFee)


        FileShop.OFlPrice = float(OFlPrice_e.text())
        self.config.set_key('OFlPrice', FileShop.OFlPrice)

        FileShop.OFlTrFee = float(OFlTrFee_e.text())
        self.config.set_key('OFlTrFee', FileShop.OFlTrFee)

        FileShop.MemPoolLimit = float(MemPoolLimit_e.text())
        self.config.set_key('MemPoolLimit', FileShop.MemPoolLimit)

        FileShop.ReceivAddress = str(ReceivAddress_e.text())
        self.config.set_key('ReceivAddress', FileShop.ReceivAddress)
        
        FileShop.FileShopPath = str(FileShopPath_e.text())
        self.config.set_key('FileShopPath', FileShop.FileShopPath)
        

    def Tx_test(self):
        global GRowTransaction
        global GFileID
        global Tx_res
        global GIDTran
        global ST4del
        
        try:
            XTr = Transaction(GRowTransaction)
        except:
            Tx_res = 0
            return
        print('XTr = ',XTr)

        Flv , FLfee , TTime = FileShop.FilePP[GFileID]
        if( Flv + FLfee == 0. ):
            Tx_res = 1
            return
        try:
            amount,fee = Tx_IOSave[GIDTran]
        except:
               
            try:        
                #is_relevant, is_mine, v, fee = self.window.wallet.get_wallet_delta(XTr)
                
                tx_hash, status, label, can_broadcast, can_rbf, amount, fee, height, conf, timestamp, exp_n = self.window.wallet.get_tx_info(XTr)
                if status != u'Signed':
                    Tx_res = 0
                    return

                InputAdrs = {}
                for x in XTr.inputs():
                    InputAdrs[x['address']]=None
                    for x in InputAdrs:
                        InputAdrs[x]=self.window.network.synchronous_get(('blockchain.address.listunspent', [x]))

                fee = 0
                amount = 0

                for x in XTr.inputs():
                    #print(InputAdrs[x['address']] )
                    for y in InputAdrs[x['address']]:
                        if y['tx_hash'] == x['prevout_hash']:
                            fee += int( y['value'])

                for addr, value in XTr.get_outputs():
                    #print('get_outputs=',addr, value , FileShop.ReceivAddress )
                    fee -= value
                    if addr == FileShop.ReceivAddress:
                        amount += value

                if len(ST4del) > 9:
                    del Tx_IOSave[ST4del[0]]
                    del ST4del[0]

                Tx_IOSave[GIDTran] = amount,fee   
                ST4del.append(GIDTran)        

            except:
                Tx_res = 0
                return
             
        #fee = amount - XTr.output_value()
        
        self.window.show_transaction(XTr, u'')
        print("amount, fee =",amount, fee, Flv , FLfee , TTime, len(GRowTransaction) )
        dFlv = abs (Flv * 1e8 - amount )
        dFLfee = abs (FLfee * 1e8  - fee * 1000. / (len(GRowTransaction)/2)  )
        if dFLfee + dFlv < 1000 :
            msg = 'MemPoolLimit'
            if amount >  MemPoolLimit * 1e8 :
                status, msg = None,None
                try:
                    #status, msg =  self.window.network.broadcast(GRowTransaction)
                    print('broadcast_try=',status, msg)
                except:
                    pass            
             
            print('broadcast=',status, msg)
                
            Tx_res = 1
            return       
        
        Tx_res = 0

            
     
