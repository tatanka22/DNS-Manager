from requests import get
import sys
import os
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidget, QMainWindow, QCheckBox, QHeaderView, QTableView
from PyQt5.QtCore import QTimer, QTime, QDate, QDateTime, QRegExp, Qt, QAbstractTableModel, QRect
from PyQt5.QtGui import QRegExpValidator, QIcon, QPalette, QColor
from MyGui import Ui_MainWindow
from win2 import Ui_CrudWindow
from domeneshop import Client
from configparser import ConfigParser
import logging
import winsound


load_dotenv()
# api-credentials for domeneshop api
TOKEN = os.getenv('d_shop_token')
SECRET = os.getenv('s_shop_secret')

class MyTableView(QTableView):
    def __init__(self, parent=None):
        super(MyTableView, self).__init__(parent)

        self.context_menu = QtWidgets.QMenu(self)
        table_action1 = self.context_menu.addAction("Modify record")
        table_action2 = self.context_menu.addAction("Delete record")
        table_action3 = self.context_menu.addAction("Add record")
        
        table_action1.triggered.connect(self.modify_record)
        table_action2.triggered.connect(self.delete_record)
        table_action3.triggered.connect(self.add_record)

    def modify_record(self):
        print("Modify record")
        
        win.win2 = MyCrudWindow()  
        win.win2.setWindowTitle( "Modify record")
        win.win2.show()

        # Find current row and fill in data in win.win2
        row = win.tableView.currentIndex().row() # current row is the one we clicked on
        win.win2.label_10.setText(win.data_rec_list[row]['Domene'])
        win.win2.label_7.setText(str(win.data_rec_list[row]['Dom ID']))
        win.win2.label_8.setText(str(win.data_rec_list[row]['Rec ID']))
        win.win2.label_11.setText(win.data_rec_list[row]['Record'])
        win.win2.label_12.setText(win.data_rec_list[row]['Type'])
        win.win2.lineEdit_3.setText(str(win.data_rec_list[row]['TTL']))
        win.win2.lineEdit_4.setText(win.data_rec_list[row]['IP'])
        # Disable delete and add button in win.win2    
        win.win2.btn_Delete_rec.hide()
        win.win2.btn_Add_rec.hide()
        # Disable label 13-16
        win.win2.label_13.hide()
        win.win2.label_14.hide()
        win.win2.label_15.hide()
        win.win2.label_16.hide()
        win.win2.label_17.hide()
        win.win2.label_18.hide()
        win.win2.lineEdit_1.hide()
        win.win2.lineEdit_2.hide()


    def delete_record(self):
        print("Delete record")

        win.win2 = MyCrudWindow()  
        win.win2.setWindowTitle( "Delete record")
        win.win2.show()

        # Find current row and fill in data in win.win2
        row = win.tableView.currentIndex().row() # current row is the one we clicked on
        win.win2.label_10.setText(win.data_rec_list[row]['Domene'])
        win.win2.label_7.setText(str(win.data_rec_list[row]['Dom ID']))
        win.win2.label_8.setText(str(win.data_rec_list[row]['Rec ID']))
        win.win2.label_11.setText(win.data_rec_list[row]['Record'])
        win.win2.label_12.setText(win.data_rec_list[row]['Type'])
        win.win2.label_15.setText(str(win.data_rec_list[row]['TTL']))
        win.win2.label_16.setText(win.data_rec_list[row]['IP'])
       
        # Disable Submit and Add_rec button in win.win2    
        win.win2.btn_Submit_rec.hide()
        win.win2.btn_Add_rec.hide()
        
        # Disable lineEdit_3 and lineEdit_4
        win.win2.label_3.hide()
        win.win2.label_4.hide()
        win.win2.lineEdit_3.hide()
        win.win2.lineEdit_4.hide()
        win.win2.label_17.hide()
        win.win2.label_18.hide()
        win.win2.lineEdit_1.hide()
        win.win2.lineEdit_2.hide()


    def add_record(self):
        print("Add record")

        win.win2 = MyCrudWindow()  
        win.win2.setWindowTitle( "Add record")
        win.win2.show()

        # Find current row and fill in data in win.win2
        row = win.tableView.currentIndex().row() # current row is the one we clicked on
        win.win2.label_10.setText(win.data_rec_list[row]['Domene'])
        win.win2.label_7.setText(str(win.data_rec_list[row]['Dom ID']))

        win.win2.lineEdit_3.setText("3600")
        win.win2.lineEdit_4.setText(win.current_ip)
       
        # Disable Submit and Delete_rec button in win.win2    
        win.win2.btn_Submit_rec.hide()
        win.win2.btn_Delete_rec .hide()
        
        # Disable lineEdit_3 and lineEdit_4
        win.win2.label_6.hide()
        win.win2.label.hide()
        win.win2.label_2.hide()
        win.win2.label_13.hide()
        win.win2.label_14.hide()
        win.win2.label_15.hide()
        win.win2.label_16.hide()
        win.win2.label_8.hide()
        win.win2.label_11.hide()
        win.win2.label_12.hide()
        
   
    def contextMenuEvent(self, event):
        # This method is called whenever the user right-clicks on the table view
        #print("Right-click detected")
        self.context_menu.exec_(event.globalPos())

      
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self._headers = list(data[0].keys()) if data else []

    def data(self, index, role):
        if role == (Qt.DisplayRole or role == Qt.EditRole) and index.column() != 0:
            row_data = self._data[index.row()]
            column_key = self._headers[index.column()]
            return row_data[column_key]
        if role == Qt.DisplayRole and index.column() == 0:
            return None  # Do not return any value for the DisplayRole if columnn == 0. (because we only want icon.)

        if role == Qt.TextAlignmentRole and index.column() == 1:
             return Qt.AlignRight | Qt.AlignVCenter

        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            value = self._data[index.row()]
            value_bool = True
            value_bool = value['Watch']
            if isinstance(value_bool, bool):
                #print('den er bool' + str(value_bool == True))
                if value_bool == True:
                    return QIcon('Resources/tick.png')
                return QIcon('Resources/cross.png')
            return None
            
    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable
    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
    
    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._headers)
        pass

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]



class MyCrudWindow(QMainWindow, Ui_CrudWindow):
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_CrudWindow.__init__(self)
        self.setupUi(self)

        self.btn_Submit_rec.clicked.connect(self.submit_rec)
        self.btn_Delete_rec.clicked.connect(self.delete_rec)
        self.btn_Add_rec.clicked.connect(self.add_rec)
        self.btn_Cancel.clicked.connect(self.close)

    def submit_rec(self):
        print("update_rec")
        print(win.win2.label_10.text())             # Domene
        print(win.win2.label_11.text())             # Record (host)
        print(win.win2.lineEdit_3.text())           # TTL
        print(win.win2.lineEdit_4.text())           # IP
        print(win.win2.label_12.text())             # Type
        print(win.win2.label_7.text())              # Dom ID    
        print(win.win2.label_8.text())              # Rec ID    
        
        try:
            myRec = {"host": win.win2.label_11.text(),          # Record (host)
                    "ttl": int(win.win2.lineEdit_3.text()),     # TTL
                    "type": win.win2.label_12.text(),           # Type
                    "data": str(win.win2.lineEdit_4.text())     # IP
                    }
            win.api_client.modify_record(int(win.win2.label_7.text()), int(win.win2.label_8.text()), myRec)
    
        except:
            print('Could not update record: ' + win.win2.label_11. text() + '.' + win.win2.label_10.text() + 
                  ' with new ip: ' + str(win.win2.lineEdit_4.text()) )
            if win.logging_on == True:
                logging.info(my_date_time() + 'Could not update record: ' + win.win2.label_11. text() + 
                             '.' + win.win2.label_10.text() + ' with new ip: ' + str(win.win2.lineEdit_4.text()) )
        win.get_domains()
        win.win2.close()

    def delete_rec(self):
        print("delete_rec")
        print(win.win2.label_10.text())             # Domene
        print(win.win2.label_11.text())             # Record (host)
        print(win.win2.lineEdit_3.text())           # TTL
        print(win.win2.lineEdit_4.text())           # IP
        print(win.win2.label_12.text())             # Type
        print(win.win2.label_7.text())              # Dom ID    
        print(win.win2.label_8.text())              # Rec ID    
        
        try:
            win.api_client.delete_record(int(win.win2.label_7.text()), int(win.win2.label_8.text()))
            print('Record deleted: ' + win.win2.label_11. text() + '.' + win.win2.label_10.text()  )
            if win.logging_on == True:
                logging.info(my_date_time() + 'Record deleted: ' + win.win2.label_11. text() + 
                             '.' + win.win2.label_10.text()  )
    
        except:
            print('Could not delete record: ' + win.win2.label_11. text() + '.' + win.win2.label_10.text()  )
            if win.logging_on == True:
                logging.info(my_date_time() + 'Could not delete record: ' + win.win2.label_11. text() + 
                             '.' + win.win2.label_10.text()  )
        win.get_domains()
        win.win2.close()

    def add_rec(self):
        print("adding rec")
        
        
        try:
            myRec = {"host": win.win2.lineEdit_1.text(),            # Record (host)
                    "ttl": int(win.win2.lineEdit_3.text()),         # TTL
                    "type": win.win2.lineEdit_2.text(),             # Type
                    "data": str(win.win2.lineEdit_4.text())         # IP
                    }
            win.api_client.create_record(int(win.win2.label_7.text()), myRec)
            print('Record added: ' + win.win2.lineEdit_1.text() + '.' + win.win2.label_10.text()  )
    
        except:
            print('Could not create record: ' + win.win2.lineEdit_1. text() + '.' + win.win2.label_10.text() + 
                  ' with new ip: ' + str(win.win2.lineEdit_4.text()) )
            if win.logging_on == True:
                logging.info(my_date_time() + 'Could not create record: ' + win.win2.lineEdit_1. text() + 
                             '.' + win.win2.label_10.text() + ' with new ip: ' + str(win.win2.lineEdit_4.text()) )
        win.get_domains()
        win.win2.close()

class MyWindow(QMainWindow, Ui_MainWindow):
   
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Api client for domeneshop
        self.api_client = Client(TOKEN, SECRET)

        # Tableview setup (we now use our own class MyTableView, so we moved it from designer and MyGui.py)
        self.tableView = MyTableView(self.tab)
        self.tableView.setGeometry(QRect(0, 30, 611, 621))
        self.tableView.setObjectName("tableView")

        # Log file/logging setup
        logging.basicConfig(filename='ip-check.log', level=logging.INFO)
        logging.debug('This message should go to the log file if level is set to debug')
        logging.info(my_date_time() + 'So we\'re rolling with logging :-)' )

        # Config.ini file setup 
        self.cfg_parser = ConfigParser() 
        if not os.path.exists('config.ini'):    # Makes config.ini, if it does not exist
            self.cfg_parser['DEFAULT'] = {'ip_tid': '120', 'sound_alerts': 'True', 'logging': 'True'}
            self.cfg_parser['IP'] = {'ip': '254.254.254.254', 'ip_since_date_time': ''}
            self.cfg_parser['DOMAINS'] = {'Domain1': 'example1.com', 'domain2': 'example2.com'}
            self.cfg_parser['RECORDS'] = {'test.example1.com': 'True', 'test2.example1.com': 'False'}
            with open('config.ini', 'w') as configfile:
                self.cfg_parser.write(configfile)    
    

        # Reads config.ini
        self.cfg_parser.read('config.ini')
        self.ip_tid = int(self.cfg_parser['DEFAULT']['ip_tid'])
        self.lineEdit.setText(str(self.ip_tid))
        # Reads sound on/off
        self.actionSound_alerts.setChecked(self.cfg_parser['DEFAULT']['sound_alerts'] == 'True')
        # Reads logging on/off
        self.logging_on = (self.cfg_parser['DEFAULT']['logging'] == 'True')
        self.actionLogging_on.setChecked(self.logging_on)
        # Reads ip and ip_date_time from ini-file
        self.ip_from_ini = self.cfg_parser['IP']['ip']
        self.ip_date_time_from_ini = self.cfg_parser['IP']['ip_since_date_time']
        
       
        # Gets domains and records and loads them into tableview
        self.get_domains()

        # Timer to trigger display updates. millisecs.
        timer1 = QTimer(self)  
        timer1.timeout.connect(self.displayUpdates)
        timer1.start(500)

        # Button to set time interval for ip-check
        self.btn_set_interval.clicked.connect(self.set_button_clicked)
        # Button to get domains and records from registrar
        self.btn_table.clicked.connect(self.get_domains)
        # Button to update records with new ip
        self.btn_update_dns.clicked.connect(self.ny_ip_actions)
        
        # Connections for click in table to toggle watch value of record      
        self.tableView.clicked.connect(self.table_clicked)
        self.tableView.doubleClicked.connect(self.table_double_clicked)
      
        # Connections for menu choices 
        self.actionSound_alerts.changed.connect(self.actionSound_alerts_changed)
        self.actionLogging_on.changed.connect(self.actionLogging_on_changed)        

        # Validator too only allow numbers in lineEdit
        validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.lineEdit.setValidator(validator)
        
        # Diverse
        self.last_date_time = QDateTime.currentDateTime()
        self.next_date_time = QDateTime.currentDateTime()

        self.upsince_date_time = QDateTime.currentDateTime()

        self.retry_ip_secs = 5              # time for retrying ipfy.org if unavailable

        # Dummy values for current ip as we will not get our ip before first display update
        self.current_ip_date_time = "onsdag 12.12.1212 00:00:00"
        self.current_ip = "255.255.255.255"

        
    def closeEvent(self, event):  # closeEvent is called when the user clicks the X in the upper right corner of the window.
        """This method is called when the user clicks the X in the upper right corner of the window."""
 
        if win.win2 is not None and win.win2.isVisible():
            event.ignore()
        else:
            logging.info(my_date_time() + 'Closing program' )
            event.accept() # let the window close

    
    def set_button_clicked(self):                               # Button to set time interval for ip-check        
        self.ip_tid = int(self.lineEdit.text())
        print('Satt ny ip-tid til: ' + str(self.ip_tid) + ' s.')

        self.next_date_time = self.current_date_time.addSecs(self.ip_tid)

        # We also update next time for ip-check, as we now changed the interval        
        self.next_datetime = self.current_date_time.addSecs(self.ip_tid)
                
        # Let's also record this in the log
        if self.logging_on == True:
            logging.info(my_date_time() + 'Satt nytt tidsinterval for ip-sjekk : ' + str(self.ip_tid) + ' s. ' )
        
        # We also apply changes to ini file
        self.cfg_parser['DEFAULT']['ip_tid'] = str(self.ip_tid)
        with open('config.ini', 'w') as configfile:
            self.cfg_parser.write(configfile)
                       
    
    def actionSound_alerts_changed(self):                       # Menu choice for turning on/off sound alerts
        # Update setting in ini-file
        self.cfg_parser['DEFAULT']['sound_alerts'] = str(self.actionSound_alerts.isChecked())
        with open('config.ini', 'w') as configfile:
            self.cfg_parser.write(configfile)
        
        # Write to log
        if self.actionSound_alerts.isChecked() == True:
            play_sound('Resources\sound_ipcheck.wav')
            if self.logging_on == True: 
                logging.info(my_date_time() + 'Sound_alerts turned on' )
        if self.actionSound_alerts.isChecked() == False:
            play_sound('Resources\sound_ipcheck.wav') ### todo bytt ut med lyd for sound_alerts off
            if self.logging_on == True:
                logging.info(my_date_time() + 'Sound_alerts turned off' )             

    
    def actionLogging_on_changed(self):                         # Menu choice for turning on/off logging to file
        # Skriver til logg at vi har slått av/på logging og setter variabel logging_on til True/False
        # vi bruker den variabelen andre steder vi logger for å sjekke om vi skal logge eller ikke
        if self.actionLogging_on.isChecked() == True:
            logging.info(my_date_time() + 'Logging turned on. Hello world!' )
            self.logging_on = True
        else: 
            logging.info(my_date_time() + 'Logging turned off. See you...'  )
            self.logging_on = False
        
        # Update setting in ini-file
        self.cfg_parser['DEFAULT']['logging'] = str(self.actionLogging_on.isChecked())
        with open('config.ini', 'w') as configfile:
            self.cfg_parser.write(configfile)


    def ny_ip_actions(self):
        """Actions to take with  API when we have a new ip"""
        # We need to update the records we are watching with the new ip
        for record in self.data_rec_list:                   
            if record["Watch"] == True:
                print('Updating record: ' + record["Record"] + '.' + record["Domene"] + ' with new ip: ' + self.current_ip)
                if self.logging_on == True:
                    logging.info(my_date_time() + 'Updating record: ' + record["Record"] + '.' + record["Domene"] + ' with new ip: ' + self.current_ip )
                try:
                    myRec = {"host": record["Record"],
                            "ttl": 3600,
                            "type": "A",
                            "data": str(self.current_ip)
                            }
                    self.api_client.modify_record(record["Dom ID"], record["Rec ID"], myRec)
                except:
                    print('Could not update record: ' + record["Record"] + '.' + record["Domene"] + ' with new ip: ' + self.current_ip)
                    if self.logging_on == True:
                        logging.info(my_date_time() + 'Could not update record: ' + record["Record"] + '.' + record["Domene"] + ' with new ip: ' + self.current_ip )
                    continue
        # As we have updated some records, we can now reload domains and records from registrar
        self.get_domains()
       
        # svar = self.api_client.create_record(1834394, myRec)
        # print("ffffff" + str(svar))
        

    def table_clicked(self):
        print("table clicked")
        pass


    def table_double_clicked(self):
        # Toggles the 'Watch' value of the record(Row) in the corresponding dictionary
        row = self.tableView.currentIndex().row() # current row is the one we clicked on
        self.data_rec_list[row]['Watch'] = not self.data_rec_list[row]['Watch']
        print(self.data_rec_list[row]['Record'])
        
        # Update config.ini with new value for 'Watch'  
        curr_record = self.data_rec_list[row]['Record'] + '.' + self.data_rec_list[row]['Domene']
        value = self.data_rec_list[row]['Watch']
        self.cfg_parser['RECORDS'][curr_record] = str(value)
        with open('config.ini', 'w') as configfile:
           self.cfg_parser.write(configfile)

        print('We wrote new value for ' + curr_record + ' to config.ini file. ' + 'Watch set to: ' + str(value) )
        
        # We also log this to file
        if self.logging_on == True:
            logging.info(my_date_time() + 'New value for ' + curr_record +   '  Watch set to: ' + str(value) )

        # Update the view after changes made to data in model
        self.tableView.model().beginResetModel()
        self.tableView.model().endResetModel()
        self.tableView.update()


    def get_domains(self):
        """ Henter domener og records hos registrar. Records ender opp i data_rect_list, en liste av dicts, en dict for hver record.
            Legger også til kolonne først i dicten med boolean verdi for om vi vil ip-checke det domenet eller ikke.
            Laster også data inn i tableview."""
        self.data_rec_list =[]
        domains = []
        try:
            domains = self.api_client.get_domains()
        except:
            print('Could not get domains from registrar')
            if self.logging_on == True:
                logging.info(my_date_time() + 'Could not get domains from registrar' )
            return
      
        for domain in domains:
            dom_txt = format(domain["domain"])
            records = []
            print(dom_txt)
            
            try:
                # Get records for this domain
                records = self.api_client.get_records(domain["id"]) 
            except:
                print('Could not get records for domain: ' + dom_txt)
                if self.logging_on == True:
                    logging.info(my_date_time() + 'Could not get records for domain: ' + dom_txt )
                continue

            for record in records:
                               
                if record["type"] == 'A':#  and record["host"] != '@' :
                    if record["host"] == "@":
                        record["host"] = ""

                    print(record["id"], record["host"], record["type"], record["data"])

                    # Here we should check if we have a record in config.ini for this record
                    # if we do, we should use that value for 'Watch' instead of default value False       
                    if record["host"] + "." + dom_txt in self.cfg_parser['RECORDS']:  
                        print('We have a record for this domain in config.ini, so we use that value for Watch')  
                        watch_value = self.cfg_parser['RECORDS'][record["host"] + '.' + dom_txt] == 'True'
                        mydict = {"Watch": watch_value, 
                                  "Record": record["host"], 
                                  "Domene": dom_txt,"Type": record["type"], 
                                  "TTL": record["ttl"], "IP": record["data"], 
                                  "Rec ID": record["id"],
                                  "Dom ID": domain["id"]}
                        
                        self.data_rec_list.append(mydict)
                        
                    else:
                        # We have no record for this record in config.ini, so we set 'Watch' to default value False
                        print('We have no record for this record in config.ini, so we set Watch to False')
                        mydict = {"Watch": False, 
                                  "Record": record["host"], 
                                  "Domene": dom_txt,"Type": record["type"],
                                  "TTL": record["ttl"], 
                                  "IP": record["data"], 
                                  "Rec ID": record["id"],
                                  "Dom ID": domain["id"]}
                        
                        self.data_rec_list.append(mydict)
                       
                        # We also add this record to config.ini with value False    
                        self.cfg_parser['RECORDS'][record["host"] + '.' + dom_txt] = 'False'
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile)
                        print('We also add this record to config.ini with value False')

    
        # We Make a model and loads it into the tableview
        tableModel = TableModel(self.data_rec_list)
        self.tableView.setModel(tableModel)
        
        # Set column width for tableview
        header = self.tableView.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        # Record this in the log
        if self.logging_on == True:
            logging.info(my_date_time() +  'get_table_domains: ' + str(self.data_rec_list)   )

               
    def displayUpdates(self):
        """Displays time and date in GUI. Also keeps track of when it is time to check our ip."""
        self.current_date_time = QDateTime.currentDateTime()

        # Displays time
        self.lbl_time_val.setText(self.current_date_time.toString('hh:mm:ss'))
        self.lbl_date_val.setText(self.current_date_time.toString('dddd dd.MM.yyyy'))

        # Displays upsince time
        self.lbl_upsince_time_val.setText(self.upsince_date_time.toString('hh:mm:ss'))
        self.lbl_upsince_date_val.setText(self.upsince_date_time.toString('dddd dd.MM.yyyy'))

        # Displays last and next time for ip-check
        self.lbl_last_ipcheck_time_val.setText(self.last_date_time.toString('dddd dd.MM.yyyy hh:mm:ss'))
        self.lbl_next_ipcheck_val.setText(self.next_date_time.toString('dddd dd.MM.yyyy hh:mm:ss'))

        # Display the current ip and the date_time we got it
        self.lbl_current_ip.setText(self.current_ip)  
        self.lbl_current_ip_since_date_time.setText(self.current_ip_date_time)   
                    
        if self.current_date_time >= self.next_date_time:  # time for ip-check?
            if self.get_our_ip():
                self.compare_ip()


    def get_our_ip(self):
        """ Gets our ip from ipify.org and puts it in self.current_ip """
        print('sjekker-ip hos ipify.org...')
        try:
            #self.current_ip = get('https://api.ipify.org').content.decode('utf8')
            self.current_ip = get('https://api.ipify.org').text
            # Update last and next time for ip-check 
            self.last_date_time = self.current_date_time 
            self.next_date_time = self.current_date_time.addSecs(self.ip_tid)
            return True
        except:
            print('Could not get ip from api.ipify.org. Retrying in ' + str(self.retry_ip_secs) +' secs.')
            self.next_date_time = self.current_date_time.addSecs(self.retry_ip_secs)
            if self.logging_on == True:
                logging.info(my_date_time() + 'Could not get ip from api.ipify.org. Retrying in 5 secs...' )
            return False


    def compare_ip(self):        
        """ Function to compare our current ip with the ip previously displayed """ 
        print('comparing')
        if self.lbl_current_ip.text() == self.current_ip: 
            # Same ip, no problem..
            print('We have the same ip')
            play_sound('Resources\sound_ipcheck.wav')
            if self.logging_on == True:
                logging.info(my_date_time() + 'We have the same ip: ' + self.current_ip )
        else:
            # So, we have a different ip. It may really be new, or we may just have started the program, causing last displayed ip to be 
            # different from our current_ip. If self.lbl_current_ip, the last displayed ip, is 
            # 255.255.255.255, dummy ip set in MyWindow __init__ at startup, we know that we have just started the program. 
            # In that case we have to look for the current ip in the ini-file to see if  we have a prior record of it there or not. 
            # If we do, it is not a new ip, but if we do not, it is more likely to really be a new ip. That is, UNLESS the  ini-file itself is new. 
            # In that case we can never be sure if it is a new ip or not. In that case we signal this by setting the ip_date_time to
            # current date without time in the ini-file, when we store the new ip there.
            # Whether the ini-file is new or not we can tell from the ip-adress stored in it. If self.ip_from_ini is 254.254.254.254 
            # (dummy ip read from file) that means our ini-file is brand new and we have no prior record of any ip's. In that case we
            # can safely declare our current_ip is a new ip.
             
            if self.lbl_current_ip.text() == '255.255.255.255':        
                # We have just started the program, as last displayed ip is 255.255.255.255
                # Therefore we have to check with ini-file to see if we have a prior record of self.current_ip there
                if self.ip_from_ini == self.current_ip:
                    # We have just started the program and found in ini-file that we have the same ip as we had last we ran the program
                    print ('We had a restart and found in ini-file that we have the same ip as last run: ' + self.current_ip)
                    self.current_ip_date_time = self.ip_date_time_from_ini
                    if self.logging_on == True:
                        logging.info(my_date_time() + 'We had a restart and still have the same ip as last run: ' + self.current_ip )
                else:
                    # We have just started the program and we did not findt the current ip in ini-file
                    # So ip may really be new, or it is just that ini-file is new
                    if self.ip_from_ini == "254.254.254.254":
                        # ini-file is new
                        print('We have a new ip, but as ini-file is new, we can not be sure that it really is new')
                        # We thus set current_ip_date_time to current date without time, to signal that we have no exact knowledge of when we got this ip
                        self.current_ip_date_time = self.current_date_time.toString('ddd dd.MM.yyyy')
                        
                        if self.logging_on == True:
                            logging.info(my_date_time() + 'We have a new ip, but as ini-file is new, we can not be sure that it really is new: ' + self.current_ip )
                        # Write new ip and since_time in config.ini
                        self.cfg_parser['IP']['ip'] = self.current_ip
                        self.cfg_parser['IP']['ip_since_date_time'] = self.current_date_time.toString('ddd dd.MM.yyyy')
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile)
                    else:
                        # ini-file is not new, so we have a ip different from what is in ini-file
                        print('We have a new ip, and as ini-file is not new, we can be sure that it really is new')
                        play_sound('Resources\sound_new_ip.wav')
                       
                        if self.logging_on == True:
                            logging.info(my_date_time() + 'We just started the program and have a new ip: ' + self.current_ip )
                        # Write new ip and since_date_time in config.ini
                        self.cfg_parser['IP']['ip'] = self.current_ip
                        self.cfg_parser['IP']['ip_since_date_time'] = self.current_date_time.toString('ddd dd.MM.yyyy hh:mm:ss')
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile)
                                                
                        self.current_ip_date_time = self.current_date_time.toString('ddd dd.MM.yyyy hh:mm:ss')
                        self.get_domains()      # for å unngå feil i ny_ip_actions
                        self.ny_ip_actions()
            else:
                # We are here because last displayed ip is different from current_ip, and last_ip displayed is not 255.255.255.255,
                # so we have not just started the program. That means we actually have a new ip.
                print('We actually have a new ip')
                play_sound('Resources\sound_new_ip.wav')
                if self.logging_on == True:
                    logging.info(my_date_time() + 'We have a new ip: ' + self.current_ip )
                
                # Write new ip and since_date_time in config.ini
                self.cfg_parser['IP']['ip'] = self.current_ip
                self.cfg_parser['IP']['ip_since_date_time'] = self.current_date_time.toString('ddd dd.MM.yyyy hh:mm:ss')
                with open('config.ini', 'w') as configfile:
                    self.cfg_parser.write(configfile)   
                            
                self.current_ip_date_time = self.current_date_time.toString('ddd dd.MM.yyyy hh:mm:ss')  
                self.get_domains()              # for å unngå feil i ny_ip_actions
                self.ny_ip_actions()


   
    

def play_sound(sound):
    # Play a system sound
    if (win.actionSound_alerts.isChecked() == True):
        # print("spiller lyd: " + sound)
        winsound.PlaySound(sound, winsound.SND_FILENAME)

def my_date_time():
    """Returns current datetime[QDataTime object]  + leading and trailing spaces."""
    dt = ' ' + QDateTime.currentDateTime().toString('dddd dd.MM.yyyy hh:mm:ss' + ' ') 
    return dt

def set_dark_theme(app):
    palette = QPalette()

    # Set color for different elements:
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    

    app.setPalette(palette)
        # Set the color of the QTabWidget
    app.setStyleSheet("""
    QTabWidget::pane { /* The tab widget frame */
        border-top: 2px solid #C2C7CB;
    }
    QTabWidget::tab-bar {
        left: 5px; /* move to the right by 5px */
    }
    QTabBar::tab {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                    stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
        border: 2px solid #C4C4C3;
        border-bottom-color: #C2C7CB; /* same as the pane color */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 8ex;
        padding: 2px;
    }
    QTabBar::tab:selected, QTabBar::tab:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                    stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
    }
    QTabBar::tab:selected {
        border-color: #9B9B9B;
        border-bottom-color: #C2C7CB; /* same as pane color */
    }
    """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #set_dark_theme(app)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
