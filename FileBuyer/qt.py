from PyQt4.QtGui import *
from PyQt4.QtCore import *
import PyQt4.QtCore as QtCore

from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc_gui.qt.util import WindowModalDialog , Buttons , CancelButton, OkButton , EnterButton
from electrum_ltc_gui.qt.password_dialog import PasswordDialog
from electrum_ltc.util import *
from electrum_ltc.transaction import Transaction

from functools import partial

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import socket
import SocketServer
import threading
import sys
import datetime
import time
import inspect

quest_obj = QObject()
quest_result = None
quest_recv = None
raw_xt = None
fuse = 1.
BuyPw =  None

def dset(d):
    d.setWindowState(Qt.WindowActive)
    d.setWindowFlags(d.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    # don't work
    d.show()
    d.raise_()
    d.activateWindow()
    d.setFocus()

class GetHandler(BaseHTTPRequestHandler):

    global quest_obj

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
             
    def do_GET(self):
        global quest_result
        global quest_recv
        global raw_xt
        myreferer =  self.headers.get('referer', "").split('/') #  ['http:', '', 'localhost:8008', '']
        self.BTCTransaction = "123" # " BTC Transaction "
        #print("myreferer=",myreferer)

        if  len(myreferer) > 1: 
            self.wfile.write("HTTP/1.1 303 See Other\n")
            BShop = myreferer[2].split(':')
            BShopPort = 80
            if len(BShop) == 2:
                BShopPort = int(BShop[1])
            #print("mmoco=<",BShop[0],BShopPort,">")
            if BShopPort == 8120:
                self.send_error(404, "File not found")
                return
            # Give me the transaction parameters
            bsocet = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bsocet.connect((BShop[0],BShopPort))
            httpsend = "GET " + "/ltc00000$" +self.path + "\r\n\r\n" 
            #print("TransactionParam parameters query",httpsend,">")
            bsocet.send(httpsend)
            quest_recv =  bsocet.recv(1024).rstrip()
            #print ("TransactionParam=",quest_recv)
            bsocet.close()

            precv = quest_recv.split(';')
            tquestion = "Amount = %sLTC\nFee = %sLTC\nTime = %s"%( precv[0],precv[1], str(datetime.datetime.fromtimestamp(float( precv[2]))) )

            if float(precv[0]) + float(precv[1]) > fuse:
                self.send_error(404, "the fuse has tripped")
                return
            quest_result = None
            quest_obj.emit(SIGNAL('BuyerServerSig'))
            while quest_result == None:
                time.sleep(0.1)
            if not quest_result:
                self.send_error(404, "Cancel")
                return
            #print('DO_raw_xt', raw_xt)
            self.BTCTransaction = '%s'%raw_xt
            # Send  transaction
            bsocet = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bsocet.connect((BShop[0],BShopPort))
            httpsend = "PUT$" + self.BTCTransaction + "\r\n\r\n"
            #print("Transaction send",httpsend)
            bsocet.send(httpsend)
            rcv = bsocet.recv(4)
            print ("Shop Answer=",rcv)
            bsocet.close()
            
            csum = 0
            for char in self.BTCTransaction:
                csum += csum + ord(char)
            csum %= 0x10**8
            httpsend = "Location: " + myreferer[0] + "//" +  myreferer[2] + "/%08X$"%csum +self.path 
            #print("to browser",csum,httpsend,">")
            self.wfile.write(httpsend)
            self.wfile.write("\nContent-Length: 0\nConnection: close\n\n")
        return
       
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Hello')
        return

    def send_header(self, keyword, value):
        """Send a MIME header."""
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s: %s\r\n" % (keyword, value))

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = 1
            elif value.lower() == 'keep-alive':
                self.close_connection = 0

class BuyerServer(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.server = HTTPServer(('localhost', 8120), GetHandler)
        self.server.serve_forever()

    def SStop(self):
        self.server.shutdown()
        self.server.server_close()
        self.quit()

class Plugin(BasePlugin):
    global quest_obj
    Server = None
    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
        self.obj = QObject()
        self.obj.connect(quest_obj, SIGNAL('BuyerServerSig'), self.new_question)
              
        if(self.Server == None):
            self.Server = BuyerServer()
            self.Server.start()

    def requires_settings(self):
        return True

    def settings_widget(self, window):
        return EnterButton( ('Settings'), partial(self.settings_dialog, window))

    def settings_dialog(self, window):
        global BuyPw
        BuyPw = self.window.password_dialog('')
        print('BuyPw=',BuyPw)

    def close(self):
        self.Server.SStop()

    @hook
    def load_wallet(self, wallet, window):
        self.window = window

    @hook
    def init_qt(self, gui):
        for window in gui.windows:
            self.window = window
            break        

    def new_contact_dialog(self):
        d = WindowModalDialog(self.window, "transaction send")
        vbox = QVBoxLayout(d)
        vbox.addWidget(QLabel(self.tquestion))
        vbox.addLayout(Buttons(CancelButton(d), OkButton(d)))
        dset(d)
        return d.exec_()       

    def new_question(self):
        global quest_result
        global BuyPw
        global raw_xt

        self.precv = quest_recv.split(';')
        ufee = int( float(self.precv[1]) * 1e8 )
        coins = self.window.get_coins()
        outputs = [(0,self.precv[3],int( float(self.precv[0]) * 1e8 ))]
        fee = ufee 

        if  (BuyPw == None) & ( ufee + outputs[0][2] !=0 ) :
            d = PasswordDialog(self.window)
            dset(d)
            BuyPw = d.run()
        
        if coins == []:

            receiv_address = self.window.wallet.dummy_address()
            coins = [{'prevout_hash': u'', 'value': 000000000, 'height': 0, 'address': receiv_address , 'coinbase': False, 'prevout_n': 0}]
            #print('receiv_address', receiv_address)                
        try:
            if ufee == 0:
                quest_tx = self.window.wallet.make_unsigned_transaction(coins, outputs, self.window.config, 0)
                if outputs[0][2]:
                    self.window.wallet.sign_transaction(quest_tx, BuyPw)
                raw_xt = quest_tx.__str__()
            else:
                while 1:
                    quest_tx = self.window.wallet.make_unsigned_transaction(coins, outputs, self.window.config, fee)
                    self.window.wallet.sign_transaction(quest_tx, BuyPw)
                    raw_xt = quest_tx.__str__()
                    tlen = len( raw_xt ) / 2
                    if   abs(fee - ufee * tlen / 1000 ) < 100 :
                        break
                    fee = ufee * tlen / 1000
        except NotEnoughFunds:
            self.window.activateWindow()
            self.window.show_message("Insufficient funds")
            quest_result = 0
            return
        except BaseException as e:
            self.window.activateWindow()
            self.window.show_message(str(e))
            quest_result = 0
            BuyPw = None
            return
        
        #self.window.show_transaction(quest_tx, u'')
        tx_hash, status, label, can_broadcast, can_rbf, amount, fee, height, conf, timestamp, exp_n = self.window.wallet.get_tx_info(quest_tx)
        
        if fee==None:
            fee = 0

        if amount + fee == -10:
            quest_result = True
            return

        time_str = str(datetime.datetime.fromtimestamp(float( self.precv[2])))

        self.tquestion = '''do you wish to send the transaction?

Amount = %fLTC
Fee = %sLTC
'''%( amount / 1e8  , fee / 1e8)
                
        quest_result = self.new_contact_dialog()
	#quest_result = self.window.password_dialog(self.tquestion, parent = self.window.top_level_window())

        print('dialog=', quest_result)
        
        
