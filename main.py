from requests import get
import sys
import os
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QCheckBox
from PyQt5.QtCore import QTimer, QTime, QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator, QStandardItem, QColor, QFont, QStandardItemModel
from MyGui import Ui_MainWindow
from domeneshop import Client

load_dotenv()
# api-credentials for domeneshop api
TOKEN = os.getenv('d_shop_token')
SECRET = os.getenv('s_shop_secret')

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__()
        
        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

        self.check = QCheckBox('hallo')
   

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.api_client = Client(TOKEN, SECRET)

        # Timer for å oppdatere vinduet og vise tiden. millisec.
        timer1 = QTimer(self)  
        timer1.timeout.connect(self.visTid)
        timer1.start(200)

        # Knapp for å sette tiden i sekunder mellom hver ip-sjekk
        self.btn_set_interval.clicked.connect(self.set_button_clicked)
        self.ip_tid = 120
        self.lineEdit.setText("120")

        # button for domains
        self.btn_domains.clicked.connect(self.get_domains)

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
    
    def set_button_clicked(self):
        self.ip_tid = int(self.lineEdit.text())
        self.next_time = QTime.currentTime().addSecs(self.ip_tid)
        print('Satt ny ip-tid')
        print(self.ip_tid)

    def ny_ip_actions(self):
        # here we will put code for api
        pass

    def get_domains(self):
       
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()
        self.treeView.setModel(treeModel)
        self.treeView.setHeaderHidden(True)


        self.domains = self.api_client.get_domains()
        for domain in self.domains:
            print("*****")

            dom_txt = format(domain["domain"])
            domene = StandardItem(dom_txt, 12)
            rootNode.appendRow(domene)

            print("DNS records for {0}:" + dom_txt)
            print("id: {0}".format(domain["id"]))
            
            for record in self.api_client.get_records(domain["id"]):
                print(record["id"], record["host"], record["type"], record["data"])
                
                if record["type"] == 'A' and record["host"] != '@' :
                    min_record = StandardItem( record["host"] + "." + dom_txt , 10)
                    domene.appendRow(min_record)

        myRec = {"host": "test",
                "ttl": 3600,
                "type": "A",
                "data": "62.24.36.27"}
        #client.create_record(1834394, myRec)

       
              
        


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
            else:
                print('Vi har fått ny ip')
                self.lbl_lastip_val.setText(self.last_ip)
                self.last_ip_date = QDate.currentDate().toString('dd.MM.yyyy')   # lastIpate er for dagen vi fikk siste IP
                self.lbl_lastip_since_date_val.setText(self.last_ip_date)
                self.lastip_time = current_time.toString('hh:mm:ss')             # lastIpTime er for når vi fikk siste IP
                self.lbl_lastip_since_time_val.setText(self.last_ip_time)
                self.last_ip = self.lbl_lastip_val.text()
                self.ny_ip_actions()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
