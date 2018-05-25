from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QGridLayout, QLabel, QVBoxLayout, QLineEdit)

from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc_gui.qt.util import WindowModalDialog , Buttons , CancelButton, OkButton
from electrum_ltc.util import *
from electrum_ltc_gui.qt.util import EnterButton, Buttons, CloseButton
from electrum_ltc_gui.qt.util import OkButton, WindowModalDialog
from functools import partial

from electrum_ltc.transaction import Transaction

import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from socketserver     import ThreadingMixIn
from http import HTTPStatus


import threading
import cgi
import os, sys, posixpath
import datetime
import time
from decimal import Decimal


import FileShop.FileShop as FFS
from FileShop.FileShop import *


GRowTransaction = None
GFileID = None
GIDTran = None
Tx_res = None
Tx_IOSave = {}
ST4del = []


class QFShopObject(QObject):
    FShop_signal = pyqtSignal()

quest_obj = pyqtSignal()


class GFSHandler(FSHandler):
    def TransactionTst(self):
        global quest_obj
        global GRowTransaction
        global GFileID
        global GIDTran
        global Tx_res
        
        FFS.TLock.acquire()
        GRowTransaction = self.RowTransaction
        GIDTran = self.IDTran
        GFileID = self.FileID
        Tx_res = None
        quest_obj.FShop_signal.emit()

        while Tx_res == None:
            time.sleep(0.1)
        Txres = Tx_res
        FFS.TLock.release()
        return Txres

class FileServer(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.server = ThreadedHTTPServer(('', 8008), GFSHandler)
        self.server.serve_forever()
       
    def SStop(self):
        self.server.shutdown()
        self.server.server_close()
        self.quit()


class Plugin(BasePlugin):
    Server = None

    def __init__(self, parent, config, name):
        global quest_obj
        self.DefDddr = 'LLuggsZhhkqyuyXKCjCZjmP6fFX2EgcDaa'
        if FFS.ReceivAddress == '':
            FFS.ReceivAddress = self.DefDddr

        BasePlugin.__init__(self, parent, config, name)

        FFS.NFlPrice = self.config.get('NFlPrice', FFS.NFlPrice)
        FFS.NFlTrFee = self.config.get('NFlTrFee', FFS.NFlTrFee)
        FFS.NFlTrFee = self.config.get('NFlTrFee', FFS.NFlTrFee)
        FFS.FlPrice = self.config.get('FlPrice',   FFS.FlPrice)
        FFS.FlTrFee = self.config.get('FlTrFee',   FFS.FlTrFee)
        FFS.OFlPrice = self.config.get('OFlPrice', FFS.OFlPrice)
        FFS.OFlTrFee = self.config.get('OFlTrFee', FFS.OFlTrFee)
        FFS.MemPoolLimit = self.config.get('MemPoolFFS.Limit', FFS.MemPoolLimit)       
        FFS.ReceivAddress = self.config.get('ReceivFFS.Address', FFS.ReceivAddress)
        
        quest_obj = QFShopObject()
        quest_obj.FShop_signal.connect(self.Tx_test)
              
        if(self.Server == None):
            self.Server = FileServer()
            self.Server.start()

    def close(self):
        self.Server.SStop()
        
    @hook
    def load_wallet(self, wallet, window):
        self.window = window
        if FFS.ReceivAddress == self.DefDddr:
            FFS.ReceivAddress = wallet.dummy_address()

    @hook
    def init_qt(self, gui):
        for window in gui.windows:
            self.window = window
            if FFS.ReceivAddress == self.DefDddr:
                FFS.ReceivAddress = self.window.wallet.dummy_address()
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
        NFlPrice_e.setText("%s"%FFS.NFlPrice)
        grid.addWidget(NFlPrice_e, 1, 1)

        FlPrice_e = QLineEdit()
        FlPrice_e.setText("%s"%FFS.FlPrice)
        grid.addWidget(FlPrice_e, 1, 2)

        OFlPrice_e = QLineEdit()
        OFlPrice_e.setText("%s"%FFS.OFlPrice)
        grid.addWidget(OFlPrice_e, 1, 3)

        grid.addWidget(QLabel('Fee/Kb'), 2, 0)

        NFlTrFee_e = QLineEdit()
        NFlTrFee_e.setText("%s"%FFS.NFlTrFee)
        grid.addWidget(NFlTrFee_e, 2, 1)

        FlTrFee_e = QLineEdit()
        FlTrFee_e.setText("%s"%FFS.FlTrFee)
        grid.addWidget(FlTrFee_e, 2, 2)

        OFlTrFee_e = QLineEdit()
        OFlTrFee_e.setText("%s"%FFS.OFlTrFee)
        grid.addWidget(OFlTrFee_e, 2, 3)


        grid.addWidget(QLabel('mempool limit'), 3, 1)

        MemPoolLimit_e = QLineEdit()
        MemPoolLimit_e.setText("%s"%FFS.MemPoolLimit)
        grid.addWidget(MemPoolLimit_e, 3, 2)

        grid1 = QGridLayout()
        vbox.addLayout(grid1)


        grid1.addWidget(QLabel('receiv address'), 5, 0)
        ReceivAddress_e = QLineEdit()
        ReceivAddress_e.setText(FFS.ReceivAddress)
        grid1.addWidget(ReceivAddress_e, 5, 1)

        grid1.addWidget(QLabel('FileShopPath'), 6, 0)
        FileShopPath_e = QLineEdit()
        FileShopPath_e.setText(FFS.FileShopPath)
        grid1.addWidget(FileShopPath_e, 6, 1)


        vbox.addStretch()
        vbox.addLayout(Buttons(CloseButton(d), OkButton(d)))

        if not d.exec_():
            return


        FFS.NFlPrice = float(NFlPrice_e.text())
        self.config.set_key('NFlPrice', FFS.NFlPrice)

        FFS.NFlTrFee = float(NFlTrFee_e.text())
        self.config.set_key('NFlTrFee', FFS.NFlTrFee)


        FFS.FlPrice = float(FlPrice_e.text())
        self.config.set_key('FlPrice', FFS.FlPrice)

        FFS.FlTrFee = float(FlTrFee_e.text())
        self.config.set_key('FlTrFee', FFS.FlTrFee)


        FFS.OFlPrice = float(OFlPrice_e.text())
        self.config.set_key('OFlPrice', FFS.OFlPrice)

        FFS.OFlTrFee = float(OFlTrFee_e.text())
        self.config.set_key('OFlTrFee', FFS.OFlTrFee)

        FFS.MemPoolLimit = float(MemPoolLimit_e.text())
        self.config.set_key('MemPoolLimit', FFS.MemPoolLimit)

        FFS.ReceivAddress = str(ReceivAddress_e.text())
        self.config.set_key('ReceivAddress', FFS.ReceivAddress)
        
        FFS.FileShopPath = str(FileShopPath_e.text())
        self.config.set_key('FileShopPath', FFS.FileShopPath)
        

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

        Flv , FLfee , TTime = FilePP[GFileID]
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
                    #print('get_outputs=',addr, value , FFS.ReceivAddress )
                    fee -= value
                    if addr == FFS.ReceivAddress:
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
                    status, msg =  self.window.network.broadcast(XTr)
                    print('broadcast_try=',status, msg)
                except:
                    pass            
                     
            print('broadcast=',status, msg)
                
            Tx_res = 1
            return       
        
        Tx_res = 0

 