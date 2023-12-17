from requests import get
import sys
import os
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QHeaderView
from PyQt5.QtCore import QTimer, QTime, QDate, QRegExp, QModelIndex, Qt, QAbstractTableModel
from PyQt5.QtGui import QRegExpValidator, QStandardItem, QColor, QFont, QStandardItemModel, QIcon
from MyGui import Ui_MainWindow
from domeneshop import Client
from configparser import ConfigParser
import winsound

load_dotenv()
# api-credentials for domeneshop api
TOKEN = os.getenv('d_shop_token')
SECRET = os.getenv('s_shop_secret')

class StandardItem(QStandardItem):
    list = []
    colors = []
    colors.append(QColor(0,0,0))
    colors.append(QColor(0,0,255))

    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__()
        
        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
   
        StandardItem.list.append(self)
        
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self._headers = list(data[0].keys()) if data else []

    def data(self, index, role):
        if role == Qt.DisplayRole and index.column() != 0:
            row_data = self._data[index.row()]
            column_key = self._headers[index.column()]
            return row_data[column_key]
        if role == Qt.DisplayRole and index.column() == 0:
            return None  # Do not return any value for the DisplayRole if columnn == 0. (because we only want icon.)

        if role == Qt.TextAlignmentRole and index.column() == 1:
             return Qt.AlignRight | Qt.AlignVCenter

        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            value = self._data[index.row()]
            valuebol = value['Watch']
            if isinstance(valuebol, bool):
                if valuebol == True:
                    return QIcon('tick.png')
                return QIcon('cross.png')
    
    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._headers)
        pass

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.api_client = Client(TOKEN, SECRET)

        #   henter domener direkte
        self.get_table_domains()

        # Timer for å oppdatere vinduet og vise tiden. millisec.
        timer1 = QTimer(self)  
        timer1.timeout.connect(self.visTid)
        timer1.start(200)

        # Knapp for å sette tiden i sekunder mellom hver ip-sjekk
        self.btn_set_interval.clicked.connect(self.set_button_clicked)
        self.ip_tid = 120
        self.lineEdit.setText("120")

        # buttons for domains
        self.btn_domains.clicked.connect(self.get_domains)
        self.btn_table.clicked.connect(self.get_table_domains)

        # Validator
        validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.lineEdit.setValidator(validator)
        
        # Diverse
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()

        self.last_time = current_time
        self.next_time = current_time 

        self.upsince_time = current_time
        self.upsince_date = current_date

        self.last_ip_date = "12.12.12"
        self.last_ip_time = "00:00:00"
        self.last_ip = "192.192.192.192"

        self.lbl_lastipsince = "01:01:01"
        self.lbl_lastip_since_date = "12.12.12"

        # bool for soundalerts on or off
        self.sound_bool = True

        # parser for config.ini 
        self.cfg_parser = ConfigParser() 
        
        self.make_config()  # lager inifil hvis den ikke finnes

        # reads config.ini
        self.cfg_parser.read('config.ini')
        self.ip_tid = int(self.cfg_parser['DEFAULT']['ip_tid'])
        self.sound_bool = (self.cfg_parser['DEFAULT']['sound_alerts'] == 'True')
        self.actionSound_alerts.setChecked(self.sound_bool)
        self.lineEdit.setText(str(self.ip_tid))
        

    def make_config(self):  
        # creates config.ini if it does not exist
        if not os.path.exists('config.ini'):
            self.cfg_parser['DEFAULT'] = {'ip_tid': '120', 'sound_alerts': 'True'}
            self.cfg_parser['DOMAINS'] = {'domain1': 'example.com', 'domain2': 'example2.com'}
            self.cfg_parser['RECORDS'] = {'record1': 'example.com', 'record2': 'example2.com'}
            self.cfg_parser['IP'] = {'ip': '12.123.12.123'}
            with open('config.ini', 'w') as configfile:
                self.cfg_parser.write(configfile)      

    def set_button_clicked(self):
        self.ip_tid = int(self.lineEdit.text())
        self.next_time = QTime.currentTime().addSecs(self.ip_tid)
        print('Satt ny ip-tid')
        print(self.ip_tid)

    def ny_ip_actions(self):
        # here we will put code for to do with api
        pass

    def treeViewClicked(self):
        print("tree-view clicked")
        
        item_ind = self.treeView.currentIndex()
        print(item_ind.data())
        
    def treeViewDoubleClicked(self):
        print("tree-view dobleclicked")

        item_ind = self.treeView.currentIndex()
                
        a=0
        for item in StandardItem.list:
            a +=1
            #
            #print (item.text() + str(a))
            
            if item.text() == str(item_ind.data()):
                if item.foreground() == StandardItem.colors[0]:
                    item.setForeground(StandardItem.colors[1])
                else: 
                    item.setForeground(StandardItem.colors[0])

    def table_clicked(self):
        print("table clicked")

    def table_double_clicked(self):
        print("table double clicked")
        
        # toggle the 'Watch' value in the corresponding dictionary
        row = self.tableView.currentIndex().row()
        self.data_rec_list[row]['Watch'] = not self.data_rec_list[row]['Watch']
        
        # update the view after changes made to data in model
        self.tableView.model().beginResetModel()
        self.tableView.model().endResetModel()
        self.tableView.update()

    def get_table_domains(self):
        #   henter domener og records hos registrar. data om disse ender opp i data_rect_list, en liste av dicts.
        #   legger også til kolonne først i dicten med boolean verdi for om vi vil ip-checke det domenet eller ikke.
        self.data_rec_list =[]
        domains = self.api_client.get_domains()
        for domain in domains:
            dom_txt = format(domain["domain"])
            print(dom_txt)
            
            for record in self.api_client.get_records(domain["id"]):
                               
                if record["type"] == 'A':#  and record["host"] != '@' :
                    if record["host"] == "@":
                        record["host"] = ""

                    print(record["id"], record["host"], record["type"], record["data"])

                    mydict = {"Watch": True, "Record": record["host"], "Domene": dom_txt,"Type": record["type"], "TTL": record["ttl"], "IP": record["data"], "ID": record["id"]}
                    self.data_rec_list.append(mydict)
        
        # lager model og laster data.
        tableModel = TableModel(self.data_rec_list)
        # laster model inn i tableView som allerede er lagt til i UI-filen(qtdesigner)
        self.tableView.setModel(tableModel)
        
        #item = tableModel.index(4,0)
        #print(item.data())

        # setter kolonnebredder for tableView
        header = self.tableView.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.tableView.clicked.connect(self.table_clicked)
        self.tableView.doubleClicked.connect(self.table_double_clicked)
       
    def get_domains(self):
        treeModel = QStandardItemModel()
              
        rootNode = treeModel.invisibleRootItem()
        self.treeView.setModel(treeModel)
        self.treeView.setHeaderHidden(True)

        self.treeView.clicked.connect(self.treeViewClicked)
        self.treeView.doubleClicked.connect(self.treeViewDoubleClicked)
    
        self.domains = self.api_client.get_domains()
       
        for domain in self.domains:
            print("*****")

            dom_txt = format(domain["domain"])
            domene = StandardItem(dom_txt, 12)
            rootNode.appendRow(domene)
            #domene.setColumnCount(1)
            print("DNS records for {0}:" + dom_txt)
            print("id: {0}".format(domain["id"]))
            
            for record in self.api_client.get_records(domain["id"]):
                                
                if record["type"] == 'A':# and record["host"] != '@' :
                    if record["host"] == "@":
                        record["host"] = ""
                    print(record["id"], record["host"], record["type"], record["data"])
                    self.min_record = StandardItem( record['host'] + '.' + dom_txt,12 )
                                      
                    domene.insertRow(0,self.min_record)
                   
        
        myRec = {"host": "test56",
                "ttl": 3600,
                "type": "A",
                "data": "62.24.36.27"
                }

        myRec2 = {"host": "test56",
                "ttl": 3600,
                "type": "A",
                "data": "88.92.182.26"
                }
        # svar = self.api_client.create_record(1834394, myRec)
        # print("ffffff" + str(svar))
        #svar = self.api_client.modify_record(1834394, 5947892, myRec2)
        #print("ffffff" + str(svar))
        
        
    def visTid(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
       
        # prints time
        self.lbl_time_val.setText(current_time.toString('hh:mm:ss'))
        self.lbl_date_val.setText(current_date.toString('dddd dd.MM.yyyy'))

        # prints upsince time
        self.lbl_upsince_time_val.setText(self.upsince_time.toString('hh:mm:ss'))
        self.lbl_upsince_date_val.setText(self.upsince_date.toString('dddd dd.MM.yyyy'))

        # printer verdier i labels for last and next ip-check
        self.lbl_last_ipcheck_time_val.setText(self.last_time.toString())
        self.lbl_next_ipcheck_val.setText(self.next_time.toString())

        # prints values in label for ip
        self.lbl_lastip_val.setText(self.last_ip)  

        if current_time >= self.next_time:  # time for ip-check?
            # update last and next time for ip-check 
            
            self.last_time = current_time 
            self.next_time = self.last_time.addSecs(self.ip_tid)
            # gets my ip
            print('sjekker-ip...')
            self.last_ip = get('https://api.ipify.org').content.decode('utf8')
                   
            if self.lbl_lastip_val.text() == self.last_ip:  # har vi ny IP?
                print('Vi har samme ip')
                play_sound('systemAsterisk')
            else:
                print('Vi har fått ny ip')
                #play_sound('systemHand')
                play_sound('systemNotification')
                self.lbl_lastip_val.setText(self.last_ip)
                self.last_ip_date = QDate.currentDate().toString('dd.MM.yyyy')   # lastIpate er for dagen vi fikk siste IP
               # self.lbl_lastip_since_date.setText(self.last_ip_date)
                self.lastip_time = current_time.toString('hh:mm:ss')             # lastIpTime er for når vi fikk siste IP
               # self.lbl_lastip_since.setText(self.last_ip_time)
               # self.last_ip = self.lbl_lastip.text()
                self.ny_ip_actions()

def play_sound(sound):
        # Play a system sound
    print("her for å spille lyd")
    if MyWindow().sound_bool:
        print("spiller lyd")
        winsound.PlaySound('windows Notify', winsound.SND_ASYNC)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
