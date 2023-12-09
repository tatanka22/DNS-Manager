from requests import get
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QTime, QDate
from MyGui import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        timer1 = QTimer(self)  # Timer for å vise tiden. millisec.
        timer1.timeout.connect(self.visTid)
        timer1.start(200)
        self.SetBtn.clicked.connect(self.set_button_clicked)
        self.iptid = 120
        self.lineEdit.setText("120")
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        self.lastTime = current_time
        self.nextTime = current_time
        self.lastIpDate = "12.12.12"
        self.lastIpTime = "00:00:00"
        self.lastIp = "192.192.192.192"
        self.label_upsince_val.setText(current_time.toString())
        self.lbl_upsince_date_val.setText(current_date.toString('dd.MM.yyyy'))

    def set_button_clicked(self):
        self.iptid = int(self.lineEdit.text())
        print('Satt ny ip-tid')
        print(self.iptid)
        self.nextTime = QTime.currentTime().addSecs(self.iptid)

    def nyIpActions(self):
        print('Vi har fått ny ip')

    def visTid(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
       
        self.lbl_time_val.setText(current_time.toString('hh:mm:ss'))
        self.lbl_date_val.setText(current_date.toString('dd.MM.yyyy'))
        self.lbl_lastipchecktime_val.setText(self.lastTime.toString())
        self.lbl_nextipcheck_val.setText(self.nextTime.toString())

        if current_time >= self.nextTime:  # Er det tid for ip-check?
            self.lastTime = current_time  # lastTime = tiden for siste sjekk
            self.nextTime = self.lastTime.addSecs(self.iptid)

            ip = get('https://api.ipify.org').content.decode('utf8')
            self.lbl_lastip_val.setText(ip)
            self.lbl_lastipsincedate_val.setText(self.lastIpDate)
            print('sjekker-ip')

            # Har vi ny IP?
            if self.lbl_lastip_val.text() == self.lastIp:
                print('Vi har samme ip')
            else:
                self.lastIpDate = QDate.currentDate()
                self.lastIpDate = self.lastIpDate.toString('dd.MM.yyyy')
                self.lbl_lastipsincedate_val.setText(self.lastIpDate)
                self.lastIpTime = current_time.toString('hh:mm:ss')  # lastIpTime er for når vi fikk siste IP
                self.lbl_lastipsincetime_val.setText(self.lastIpTime)
                self.lastIp = self.lbl_lastip_val.text()
                self.nyIpActions()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
