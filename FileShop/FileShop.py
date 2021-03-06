from electrum_ltc.plugins import BasePlugin, hook
from electrum_ltc.util import *

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

import io

NFlPrice = 0.04
NFlTrFee = 0.001
FlPrice = 0.01
FlTrFee = 0.0008
OFlPrice = 0.0
OFlTrFee = 0.0
MemPoolLimit = 0.0000001 
Transactions = {}
Tr4del = []
FilePP = {}
ReceivAddress = ''
ReadmeLst = ['readme.txt','readme.html','README.md']

#class FileAtclass:


def FileShop_dir():
    if  os.name == 'posix':
        return os.path.join(os.environ["HOME"], "electrum-ltc-shop")
    elif "APPDATA" in os.environ:
        return os.path.join(os.environ["APPDATA"], "Electrum-ltc-shop")
    elif "LOCALAPPDATA" in os.environ:
        return os.path.join(os.environ["LOCALAPPDATA"], "Electrum-ltc-shop")
    else:
        #raise Exception("No home directory found in environment variables.")
        return

def FileShop_path():
    path = FileShop_dir()
    if not os.path.exists(path):
        if os.path.islink(path):
            raise BaseException('Dangling link: ' + path)
        os.mkdir(path)
    return path


FileShopPath = FileShop_path()
TLock = threading.Lock()


#class FSHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
class FSHandler(http.server.SimpleHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        #self.RequestHandlerClass.base_path = '~/Downloads'

    def translate_path(self, path):
        global FileShopPath
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = FileShopPath # os.getcwd()
        word = ''
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path,word

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        enc = sys.getfilesystemencoding()
        r.append('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)

        r.append("<title>File Shop %s</title>\n" % displaypath)
        r.append("<body>\n<h2>The running <a href=\"https://github.com/mak4444/LTCFileShopPlugin\">Electrum-ltc plugin</a> is needed for downloading</h2>\n")
        r.append("<hr>\n<ul>\n<table border=\"1\"> <tr> <th>Name</th><th>Size</th><th>Modify time</th> <th>Price LTC</th>  <th>Tr Fee LTC/kB </th> </tr>")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            filesize = ""
            HFlPrice = ""
            HFlTrFee = ""
            FDTime = os.path.getmtime(fullname)
            DeltaT = time.mktime(time.localtime()) - FDTime
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            else:
                filesize = str(os.path.getsize(fullname))
                if not name in ReadmeLst:
                    if DeltaT < 60*60:
                        HFlPrice = NFlPrice
                        HFlTrFee = NFlTrFee
                    elif DeltaT < 60*60*24:
                        HFlPrice = FlPrice
                        HFlTrFee = FlTrFee
                    else:
                        HFlPrice = OFlPrice
                        HFlTrFee = OFlTrFee
                    
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<tr><td><li><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
                    % (urllib.parse.quote(linkname), cgi.escape(displayname), filesize ,
                       str(datetime.datetime.fromtimestamp(os.path.getmtime(fullname))) , HFlPrice , HFlTrFee  ) )
        r.append("</table></ul>\n<hr>\n</body>\n</html>\n")
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def TransactionTst(self):
        return 1
    
    def do_PUT(self):
        global Tr4del
        csum = 0
        for char in self.RowTransaction:
            csum += csum + ord(char)
        csum %= 0x10**8
        self.FileID = csum 
        #print("mmoTransaction=",self.RowTransaction,csum)

        # so that the buffer does not grow larger
        try:
            Tr4del.remove(csum)
        except:
            pass                    
        if len(Tr4del) > 9:
            print("del Tr4del[0]=",Tr4del[0],len(Tr4del))
            del Transactions[Tr4del[0]]
            del Tr4del[0]

        Transactions[csum]=self.RowTransaction # self.TransactionTst()
        self.wfile.write(b"ok\r\n")
        Tr4del.append(csum)        

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            #print("rfile.readline")
            self.raw_requestline = self.rfile.readline(65537)
            #print("nextL0=",self.raw_requestline)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            count = 1
            print("raw_requestline=",self.raw_requestline)
            words = self.raw_requestline.decode().split('$')
            self.command = ""
            if len(words) == 2:
                self.command , self.RowTransaction = words
                self.RowTransaction = self.RowTransaction.rstrip()
            if self.command == "PUT":
                self.do_PUT()
                self.close_connection = 1
                return
            
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    def send_head(self):
        global ReceivAddress
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path,fname = self.translate_path(self.path)
        f = None
        print("mmopath=<",path,">")
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            return self.list_directory(path)
            
        #print("mmoself.path=<",self.path,">")
        if len(self.path) < 8 :
            self.wfile.write(("HTTP/1.1 303 See Other\nLocation: http://localhost:8120"+self.path).encode('latin-1', 'strict') )
            self.wfile.write(b"\nContent-Length: 0\nConnection: close\n\n")
            self.close_connection = True
            print("mmoself.path<8",self.path,f)
            return f
        self.IDTran = None
        if  self.path!='/favicon.ico' and not fname in ReadmeLst:
            if self.path[1+8] != "$" : #False:
                # Address to the local buyer
                self.wfile.write(("HTTP/1.1 303 See Other\nLocation: http://localhost:8120"+self.path).encode('latin-1', 'strict') )
                self.wfile.write(b"\nContent-Length: 0\nConnection: close\n\n")
                self.close_connection = True
                print("mmoself.path != $",self.path,f)
                return f
             
            if self.path[1:9]=='ltc00000': # What transaction do you need?
                self.path= self.path.split('$')[1]
                path,fname = self.translate_path(self.path)           
                if fname in ReadmeLst:
                        HFlPrice = 0.
                        HFlTrFee = 0.
                else:
                    FDTime = os.path.getmtime(path)
                    DeltaT = time.mktime(time.localtime()) - FDTime
                    if DeltaT < 60*60:
                        HFlPrice = NFlPrice
                        HFlTrFee = NFlTrFee
                    elif DeltaT < 60*60*24:
                        HFlPrice = FlPrice
                        HFlTrFee = FlTrFee
                    else:
                        HFlPrice = OFlPrice
                        HFlTrFee = OFlTrFee
                FileID = 0
                for char in self.path:
                    FileID += ord(char)
                print('mmoFileID',FileID,self.path)
                FilePP[FileID] = (HFlPrice,HFlTrFee,time.mktime(time.gmtime()))
                self.wfile.write(("%s;%s;%s;%s\r\n"%(HFlPrice,HFlTrFee,time.mktime(time.gmtime()),ReceivAddress)).encode('latin-1', 'strict'))
                return f
            
            try:
                #print('mmoIDTransactions=',self.path[1:9])
                self.IDTran = int(self.path[1:9],base=16)
                self.RowTransaction = Transactions[self.IDTran]
                #print('mmoTransactions=',self.RowTransaction)
                
            #except KeyError:
            except :
                self.send_error(404, "Transaction not found")
                return None
                                    
            self.FileID = 0
            for char in self.path[10:]:
                self.FileID += ord(char)                
            
            print('mmoself.FileID',self.FileID,self.path[10:])
            
            path= self.path.split('$')[1]
            path,fname = self.translate_path(path)           

        try:
            ctype = self.guess_type(path)
            #print("mmoopen.path=<",path,">")
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        
        if self.IDTran != None:   
            if not self.TransactionTst():
                self.send_error(404, "Transaction test error")
                return None       
        
        try:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

class ThreadedHTTPServer(ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread."""

#sudo apt-get install python3-pyqt5
