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
import logging
import winsound

load_dotenv()
# api-credentials for domeneshop api
TOKEN = os.getenv('d_shop_token')
SECRET = os.getenv('s_shop_secret')

      
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
            value_bool = True
            value_bool = value['Watch']
            if isinstance(value_bool, bool):
                #print('den er bool' + str(value_bool == True))
                if value_bool == True:
                    return QIcon('Resources/tick.png')
                return QIcon('Resources/cross.png')
            return None
            
    
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

        # Api client for domeneshop
        self.api_client = Client(TOKEN, SECRET)

        # Log file setup
        logging.basicConfig(filename='ip-check.log', level=logging.INFO)
        logging.debug('This message should go to the log file if level is set to debug')
        logging.info(my_date_time() + 'So we\'re rolling with logging :-)' )

        # Parser for config.ini file setup
        self.cfg_parser = ConfigParser() 
        # Makes config.ini, if it does not exist
        self.newIni = False # Used to check if we have a new ini-file
        if not os.path.exists('config.ini'):
            self.cfg_parser['DEFAULT'] = {'ip_tid': '120', 'sound_alerts': 'True', 'logging': 'True'}
            self.cfg_parser['IP'] = {'ip': '12.123.12.123', 'ip_since_date': '12.12.12', 'ip_since_time': '00:00:00'}
            self.cfg_parser['DOMAINS'] = {'Domain1': 'example1.com', 'domain2': 'example2.com'}
            self.cfg_parser['RECORDS'] = {'test.example1.com': 'True', 'test2.example1.com': 'False'}
            with open('config.ini', 'w') as configfile:
                self.cfg_parser.write(configfile)    
            self.newIni = True

        # Reads config.ini
        self.cfg_parser.read('config.ini')
        self.ip_tid = int(self.cfg_parser['DEFAULT']['ip_tid'])
        self.actionSound_alerts.setChecked(self.cfg_parser['DEFAULT']['sound_alerts'] == 'True')
        self.lineEdit.setText(str(self.ip_tid))
        self.logging_on = (self.cfg_parser['DEFAULT']['logging'] == 'True')
        self.actionLogging_on.setChecked(self.logging_on)
        self.ip_from_ini = self.cfg_parser['IP']['ip']
        self.ip_date_from_ini = self.cfg_parser['IP']['ip_since_date']
        self.ip_time_from_ini = self.cfg_parser['IP']['ip_since_time']

        # Gets domains and records and loads them into tableview
        self.get_domains()

        # Timer to trigger display updates. millisecs.
        timer1 = QTimer(self)  
        timer1.timeout.connect(self.visTid)
        timer1.start(500)

        # Knapp for å sette tiden i sekunder mellom hver ip-sjekk
        self.btn_set_interval.clicked.connect(self.set_button_clicked)
        
        # Knapp for å hente domener og records hos registrar
        self.btn_table.clicked.connect(self.get_domains)
       
        # Connections for doubleclick in table to toggle watch value of record      
        self.tableView.clicked.connect(self.table_clicked)
        self.tableView.doubleClicked.connect(self.table_double_clicked)

        # Connections for menu choices 
        self.actionSound_alerts.changed.connect(self.actionSound_alerts_changed)
        self.actionLogging_on.changed.connect(self.actionLogging_on_changed)        

        # Validator too only allow numbers in lineEdit
        validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.lineEdit.setValidator(validator)
        
        # Diverse
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()

        self.last_time = current_time
        self.next_time = current_time 

        self.upsince_time = current_time
        self.upsince_date = current_date

        self.current_ip_date = "12.12.12"
        self.current_ip_time = "00:00:00"
        self.current_ip = "192.192.192.192"
     


    def set_button_clicked(self):
        self.ip_tid = int(self.lineEdit.text())
        print('Satt ny ip-tid til: ' + str(self.ip_tid) + ' s.')

        # We also update next time for ip-check, as we now changed the interval        
        self.next_time = QTime.currentTime().addSecs(self.ip_tid)
                
        # Let's also record this in the log
        if self.logging_on == True:
            logging.info(my_date_time() + 'Satt nytt tidsinterval for ip-sjekk : ' + str(self.ip_tid) + ' s. ' )
        
        # We also apply changes to ini file
        self.cfg_parser['DEFAULT']['ip_tid'] = str(self.ip_tid)
        with open('config.ini', 'w') as configfile:
            self.cfg_parser.write(configfile)

                         
    # Menu choice for turning on/off sound alerts
    def actionSound_alerts_changed(self):
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

    # Menu choice for turning on/off logging to file
    def actionLogging_on_changed(self):
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
        
    # Here we will put code for to do with api
    def ny_ip_actions(self):
        pass

    def table_clicked(self):
        #print("table clicked")
        pass

    def table_double_clicked(self):
        # Toggles the 'Watch' value of the record(Row) in the corresponding dictionary
        row = self.tableView.currentIndex().row() # current row is the one we clicked on
        self.data_rec_list[row]['Watch'] = not self.data_rec_list[row]['Watch']
        print(self.data_rec_list[row]['Record'])
        

        # Update config.ini with new value for 'Watch'  
        self.cfg_parser['RECORDS'][self.data_rec_list[row]['Record'] + '.' + self.data_rec_list[row]['Domene']] = str(self.data_rec_list[row]['Watch'])
        with open('config.ini', 'w') as configfile:
           self.cfg_parser.write(configfile)
        print('We wrote new value for Watch to config.ini')
        
        # Update the view after changes made to data in model
        self.tableView.model().beginResetModel()
        self.tableView.model().endResetModel()
        self.tableView.update()

    def get_domains(self):
        """ Henter domener og records hos registrar. Data om disse ender opp i data_rect_list, en liste av dicts, en dict for hver record.
            Legger også til kolonne først i dicten med boolean verdi for om vi vil ip-checke det domenet eller ikke.
            laster også data inn i tableview."""
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

                    # Here we should check if we have a record in config.ini for this record
                    # if we do, we should use that value for 'Watch' instead of False       
                    if record["host"] + "." + dom_txt in self.cfg_parser['RECORDS']:  
                        print('We have a record for this domain in config.ini, so we use that value for Watch')  
                        watch_value = self.cfg_parser['RECORDS'][record["host"] + '.' + dom_txt] == 'True'
                        mydict = {"Watch": watch_value, "Record": record["host"], "Domene": dom_txt,"Type": record["type"], "TTL": record["ttl"], "IP": record["data"], "ID": record["id"]}
                        self.data_rec_list.append(mydict)
                        
                    else:
                        # We have no record for this record in config.ini, so we set 'Watch' to False
                        print('We have no record for this record in config.ini, so we set Watch to False')
                        mydict = {"Watch": False, "Record": record["host"], "Domene": dom_txt,"Type": record["type"], "TTL": record["ttl"], "IP": record["data"], "ID": record["id"]}
                        self.data_rec_list.append(mydict)
                        
                        
                        # We also add this record to config.ini with value False    
                        self.cfg_parser['RECORDS'][record["host"] + '.' + dom_txt] = 'False'
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile)
                        print('We also add this record to config.ini with value False')

    
        # Makes a model and loads it into the tableview
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

        # Record this in the log
        if self.logging_on == True:
            logging.info(my_date_time() +  'get_table_domains: ' + str(self.data_rec_list)   )

       
       
    def visTid(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
       
        # Displays time
        self.lbl_time_val.setText(current_time.toString('hh:mm:ss'))
        self.lbl_date_val.setText(current_date.toString('dddd dd.MM.yyyy'))

        # Displays upsince time
        self.lbl_upsince_time_val.setText(self.upsince_time.toString('hh:mm:ss'))
        self.lbl_upsince_date_val.setText(self.upsince_date.toString('dddd dd.MM.yyyy'))

        # Displays last and next time for ip-check
        self.lbl_last_ipcheck_time_val.setText(self.last_time.toString())
        self.lbl_next_ipcheck_val.setText(self.next_time.toString())

        # Display the current ip
        self.lbl_current_ip_val.setText(self.current_ip)  

        # Display current ip date and time (i.e. the time we got the current ip)
        self.lbl_lastip_since_date.setText(self.current_ip_date)   
        self.lbl_lastip_since_time.setText(self.current_ip_time)


        if current_time >= self.next_time:  # time for ip-check?
            # Update last and next time for ip-check 
            self.last_time = current_time 
            self.next_time = self.last_time.addSecs(self.ip_tid)
           
            # Gets our ip
            print('sjekker-ip...')
            self.current_ip = get('https://api.ipify.org').content.decode('utf8')
                   
            if self.lbl_current_ip_val.text() == self.current_ip:  # har vi samme IP?
                print('We have the same ip')
                play_sound('Resources\sound_ipcheck.wav')
                if self.logging_on == True:
                    logging.info(my_date_time() + 'We have the same ip: ' + self.current_ip )
                
            else:
                # Looks like we have a new ip
                # but we need to compare with ip from ini-file, as we might have just restarted the program
                if self.current_ip != self.ip_from_ini:
                    if self.newIni == True:
                        print('we have a new ini-file so we have no prior record of this ip')
                        self.current_ip_date = QDate.currentDate().toString('dd.MM.yyyy')  
                        self.current_ip_time = current_time.toString('hh:mm:ss') 
                         # Set new ip in config.ini
                        self.cfg_parser['IP']['ip'] = self.current_ip
                        self.cfg_parser['IP']['ip_since_date'] = current_date.toString('dd.MM.yyyy')
                        self.cfg_parser['IP']['ip_since_time'] = current_time.toString('hh:mm:ss')
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile) 
                        self.newIni = False
                    else:
                        # We actually have a new ip
                        print('We actually have a new ip')
                        play_sound('Resources\sound_new_ip.wav')
                        if self.logging_on == True:
                            logging.info(my_date_time() + 'We have a new ip: ' + self.current_ip )
                        
                        # Set new ip in config.ini
                        self.cfg_parser['IP']['ip'] = self.current_ip
                        self.cfg_parser['IP']['ip_since_date'] = current_date.toString('dd.MM.yyyy')
                        self.cfg_parser['IP']['ip_since_time'] = current_time.toString('hh:mm:ss')
                        with open('config.ini', 'w') as configfile:
                            self.cfg_parser.write(configfile)   
                                    
                        self.current_ip_date = QDate.currentDate().toString('dd.MM.yyyy')  
                        self.current_ip_time = current_time.toString('hh:mm:ss')           
                    
                        self.ny_ip_actions()
                else:
                    print ('Looks like we had a restart and still have the same ip: ' + self.current_ip)
                    self.current_ip_date = self.ip_date_from_ini
                    self.current_ip_time = self.ip_time_from_ini
                    if self.logging_on == True:
                        logging.info(my_date_time() + 'Looks like we had a restart and still have the same ip: ' + self.current_ip )
                    pass
                


def play_sound(sound):
    # Play a system sound
    if (win.actionSound_alerts.isChecked() == True):
        # print("spiller lyd: " + sound)
        winsound.PlaySound(sound, winsound.SND_FILENAME)

def my_date_time():
    """Returns current date and time as one string + spaces"""
    current_time = QTime.currentTime()
    current_date = QDate.currentDate()
    #print(current_time.toString('hh:mm:ss'))
    #print(current_date.toString('dddd dd.MM.yyyy'))
    dt = current_date.toString(' ' + 'dd.MM.yyyy') + ' ' + current_time.toString('hh:mm:ss' + ' ')
    return dt
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
