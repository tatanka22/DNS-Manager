from requests import get
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QTime, QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator
from MyGui import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # Timer for å oppatere vinduet og vise tiden. millisec.
        timer1 = QTimer(self)  
        timer1.timeout.connect(self.visTid)
        timer1.start(200)
        # Knapp for å sette tiden i sekunder mellom hver ip-sjekk
        self.btn_set_interval.clicked.connect(self.set_button_clicked)
        self.ip_tid = 120
        self.lineEdit.setText("120")
        # self.lineEdit.textChanged.connect(self.test_change)
        # Validator
        validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.lineEdit.setValidator(validator)
        # Diverse
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        self.last_time = current_time
        self.next_time = current_time
        self.lbl_upsince_time_val.setText(current_time.toString('hh:mm:ss'))
        self.lbl_upsince_date_val.setText(current_date.toString('dd.MM.yyyy'))
        self.last_ip_date = "12.12.12"
        self.last_ip_time = "00:00:00"
        self.last_ip = "192.192.192.192"
    
    def set_button_clicked(self):
        self.ip_tid = int(self.lineEdit.text())
        self.next_time = QTime.currentTime().addSecs(self.ip_tid)
        print('Satt ny ip-tid')
        print(self.ip_tid)

    def ny_ip_actions(self):
        print('Vi har fått ny ip')

    def visTid(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
       
        self.lbl_time_val.setText(current_time.toString('hh:mm:ss'))
        self.lbl_date_val.setText(current_date.toString('dd.MM.yyyy'))
        self.lbl_last_ipcheck_time_val.setText(self.last_time.toString())
        self.lbl_next_ipcheck_val.setText(self.next_time.toString())

        if current_time >= self.next_time:  # Er det tid for ip-check?
            self.last_time = current_time  # lastTime = tiden for siste sjekk
            self.next_time = self.last_time.addSecs(self.ip_tid)

            ip = get('https://api.ipify.org').content.decode('utf8')
            self.lbl_lastip_val.setText(ip)
            self.lbl_lastip_since_date_val.setText(self.last_ip_date)
            print('sjekker-ip...')

            # Har vi ny IP?
            if self.lbl_lastip_val.text() == self.last_ip:
                print('Vi har samme ip')
            else:
                self.last_ip_date = QDate.currentDate().toString('dd.MM.yyyy')   # lastIpate er for dagen vi fikk siste IP
                self.lbl_lastip_since_date_val.setText(self.last_ip_date)
                self.lastip_time = current_time.toString('hh:mm')             # lastIpTime er for når vi fikk siste IP
                self.lbl_lastip_since_time_val.setText(self.last_ip_time)
                self.last_ip = self.lbl_lastip_val.text()
                self.ny_ip_actions()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
