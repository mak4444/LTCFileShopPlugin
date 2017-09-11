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
from electrum_ltc.transaction import Transaction

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import socket
import SocketServer
import threading
import sys
import datetime
import time

quest_obj = QObject()
quest_result = None
quest_recv = None
raw_xt = None

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
        print ("myreferer=",myreferer)
        #bWidget = QWidget()
        #bWidget.focus()


        if  len(myreferer) > 1: 

            self.wfile.write("HTTP/1.1 303 See Other\n")

            BShop = myreferer[2].split(':')
            BShopPort = 80
            if len(BShop) == 2:
                BShopPort = int(BShop[1])
            print("mmoco=<",BShop[0],BShopPort,">")
            if BShopPort == 8120:
                self.send_error(404, "File not found")
                return

            # Give me the transaction parameters
            bsocet = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bsocet.connect((BShop[0],BShopPort))
            httpsend = "GET " + "/ltc00000$" +self.path + "\r\n\r\n" 
            print("TransactionParam parameters query",httpsend,">")
            bsocet.send(httpsend)
            quest_recv =  bsocet.recv(1024).rstrip()
            print ("TransactionParam=",quest_recv)
            bsocet.close()
            #self.BTCTransaction = 'make' + quest_recv

            precv = quest_recv.split(';')
            tquestion = "Amount = %sLTC\nFee = %sLTC\nTime = %s"%( precv[0],precv[1], str(datetime.datetime.fromtimestamp(float( precv[2]))) )

            if float(precv[0]) + float(precv[1]) > 1.0 :
                 self.send_error(404, "too expensive")
                 return

            quest_result = None # QMessageBox.NoButton

            quest_obj.emit(SIGNAL('BuyerServerSig'))

            while quest_result == None: # QMessageBox.NoButton:
               time.sleep(0.1)

            if not quest_result:
                 self.send_error(404, "Cancel")
                 return

            print('DO_raw_xt', raw_xt)

            self.BTCTransaction = '%s'%raw_xt

            # Send  transaction

            bsocet = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bsocet.connect((BShop[0],BShopPort))
            httpsend = "PUT$" + self.BTCTransaction + "\r\n\r\n"
            print("Transaction send",httpsend)
            bsocet.send(httpsend)
            print ("Shop Answer=",bsocet.recv(4))
            bsocet.close()
            
            csum = 0
            for char in self.BTCTransaction:
                csum += csum + ord(char)
            #for char in self.path:
            #    csum += ord(char)
            csum %= 0x10**8
        #self.wfile.write("HTTP/1.1 303 See Other\nLocation: http://localhost:8120/$0000"+self.path)
            #httpsend = "HTTP/1.1 303 See Other\nLocation: " + myreferer[0] + "//" +  myreferer[2] + "/%08X$"%csum +self.path 
            httpsend = "Location: " + myreferer[0] + "//" +  myreferer[2] + "/%08X$"%csum +self.path 
            print("to browser",csum,httpsend,">")
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


#class BuyerServer(threading.Thread):
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
        d = WindowModalDialog(self.window, "New Contact")
        vbox = QVBoxLayout(d)
        vbox.addWidget(QLabel(self.tquestion))
        vbox.addLayout(Buttons(CancelButton(d), OkButton(d)))
        return d.exec_()
            #self.window.set_contact(unicode(line2.text()), str(line1.text()))

    def new_question(self):
        global quest_result
        global raw_xt

        self.precv = quest_recv.split(';')
        ufee = int( float(self.precv[1]) * 10**8 )
        coins = self.window.get_coins()
        outputs = [(0,self.precv[3],int( float(self.precv[0]) * 10**8 ))]
        fee = ufee 
        
        if coins == []:

            receiv_address = self.window.wallet.dummy_address()
            coins = [{'prevout_hash': u'', 'value': 000000000, 'height': 0, 'address': receiv_address , 'coinbase': False, 'prevout_n': 0}]
            print('receiv_address', receiv_address)                
        try:
            if ufee == 0:
                quest_tx = self.window.wallet.make_unsigned_transaction(coins, outputs, self.window.config, 0)
                raw_xt = quest_tx.__str__()
            else:
                while 1:
                    quest_tx = self.window.wallet.make_unsigned_transaction(coins, outputs, self.window.config, fee)
                    print('quest_tx=', quest_tx)
                    raw_xt = quest_tx.__str__()
                    tlen = len( raw_xt ) / 2
                    if   abs(fee - ufee * tlen / 1000 ) < 100 :
                        break
                    fee = ufee * tlen / 1000
        except NotEnoughFunds:
            self.window.show_message("Insufficient funds")
            quest_result = 0
            return
        except BaseException as e:
            #traceback.print_exc(file=sys.stdout)
            self.window.show_message(str(e))
            quest_result = 0
            return

        
        self.window.show_transaction(quest_tx, u'')
        tx_hash, status, label, can_broadcast, can_rbf, amount, fee, height, conf, timestamp, exp_n = self.window.wallet.get_tx_info(quest_tx)
        
        if fee==None:
            fee = 0
            
        time_str = str(datetime.datetime.fromtimestamp(float( self.precv[2])))
        self.tquestion = "Amount = %fLTC\nFee = %sLTC\nTime = %s"%( amount / 10.**8   , fee / 10.**8 , time_str )
        
        
        quest_result = self.new_contact_dialog()

        print('dialog=', quest_result)
        

        #while True:             time.sleep(2)             print("new_question",quest_result )    
        
