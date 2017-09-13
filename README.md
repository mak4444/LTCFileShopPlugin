# LTCFileShopPlugin

 Плагины к https://electrum-ltc.org/
 Этот плагины предназначены для удобной купли/продажи дешевых файлов. 
 Лайткоин выбран из-за низкой комиссии.
 Файл отдается мгновенно за транзакцию.
 Предполагается, что ради такой мелочи нет смысла специально даблспендить.
 Для выставления файла на продажу, достаточно записать его
 в специальный каталог (по умолчанию Electrum-ltc-shop).
 Путь к этому каталогу прописан в установках при плагине.
 В качестве интерфейса используется стандартный браузер с HTML запросами.
 Плагин FileShop это своего рода WWW сервер.
 При этом, у продавца должен быть запущен Electrum-ltc с плагином FileShop,
 а у покупателя Electrum-ltc с плагином FileBuyer.
 Плагин FileBuyer спросит разрешение у пользователя отпровлять транзакцию.
 В остальном, покупка файла аналогична скачиванию файлов с облачных серверов.
 Технически, произойдут следующие действия:
 Первичный запрос файла переадресуется на localhost:8120 к FileBuyer.
 Тот снова обращается к FileShop и отдает требуемую за файл
 транзакцию. Затем делает обратное перенаправление запроса
 файла к FileShop, но уже с хешем транзакции за файл.

for win:
https://www.python.org/downloads/release/python-2713/
https://pypi.python.org/pypi/win_inet_pton
https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.9.4

http://212.237.6.204:8008 - first shop
 

 Plugins of https://electrum-ltc.org/
 This plugins is designed for convenient purchase/sale of cheap files.
 The Litecoin was selected because of low fee.
 The file is given instantly to the transaction.
 It is assumed that for thes sake of such cheap,
 there is no sense in specifically double-spending.
 To put the file on sale, just write it down
 in a special catalog (default Electrum-ltc-shop).
 The path to this directory is registered in the settings for the plugin.
 The interface is a standard browser with HTML requests.
 The FileShop plug-in is a kind of WWW server.
 In this case, the seller must be running the Electrum-ltc with FileShop plugin.
 and the buyer must be running the Electrum-ltc with FileBuyer plugin.
 The FileBuyer plugin will ask permission from the user to forward the transaction.
 The purchase of a file is similar to downloading files from cloud servers
 Technically, the following actions will occur:
 The primary file request is forwarded to localhost:8120 to FileBuyer.
 That again refers to FileShop and gives the requested file transaction.
 Then does the reverse request redirection
  file to FileShop, but already with a transaction hash for the file.


