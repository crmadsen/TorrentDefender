import subprocess
import time
import os,sys
import ctypes
from PyQt4 import QtCore, QtGui, uic
import socket

qtCreatorFile = 'GUI.ui'

global interface
interface = subprocess.check_output('ip route list | grep default | awk \'{print $5} \'',shell=True)
interface = interface.replace("\n","")

# Import the GUI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyGUI(QtGui.QMainWindow, Ui_MainWindow):
    global interface

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # Your torrent client
        self.torrentClient = 'transmission'
        self.torrentClient = self.torrentClient.replace("'","")
        self.task = ''
        self.enable = 0

        self.pushButton.clicked.connect(self.enableButtonHandler)

        os.system('ifconfig %s up' % interface)
        os.system('ifconfig lo up')

    def enableButtonHandler(self):
        if self.isAdmin():
            self.enable = 1
            self.refresh()
        else:
            self.isAdmin()

    # Checks for admin status
    def isAdmin(self):
        self.task = ''
        try: 
            is_admin = os.getuid() == 0
            return True
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        if not is_admin:
            self.label_4.setText('Root access is required, please run program as superuser.')
            self.enable = 0
            return

    def netStatus(self):
        try:
            host = '8.8.8.8'
            socket.create_connection((host, 53), 2)
            return True
        except Exception as ex:
            return False 
            pass
        return False

    def vpnStatus(self):
        f = open('/dev/null','w')
        try:
            output = subprocess.check_output('ifconfig',shell=True,stderr=f).splitlines()
        except subprocess.CalledProcessError:
            output = ''
        if any('tun' in t for t in output):
            return True
        else:
            return False

    def BTStatus(self):
        try:
            task = subprocess.check_output("pstree | grep %s" % self.torrentClient, shell=True).splitlines()
        except subprocess.CalledProcessError:
            task = ''

        if any(self.torrentClient in q for q in task):
            return True
        else:
            return False
        
    def refresh(self):
        while(True):
            NetStatus = self.netStatus()
            if NetStatus == True:
               self.label.setStyleSheet('background: green')
            elif NetStatus == False:
                self.label.setStyleSheet('background: dark red')

            VPNStatus = self.vpnStatus()
            if VPNStatus == True:
                self.label_2.setStyleSheet('background: green')
            elif VPNStatus == False:
                self.label_2.setStyleSheet('background: dark red')

            BTstatus = self.BTStatus()
            if BTstatus == True:
                self.label_3.setStyleSheet('background: green')
            else:
                self.label_3.setStyleSheet('background: dark red')

            if BTstatus == True and VPNStatus == False:

                try:
                    task = subprocess.check_output("pstree | grep %s" % self.torrentClient, shell=True).splitlines()
                except subprocess.CalledProcessError:
                    task = ''

                os.system('ifconfig %s down' % interface)
                try:
                    subprocess.call("pkill -f %s" % self.torrentClient, shell=True)
                    self.label_4.setText('Killing torrent client...')
                except OSError:
                    self.label_4.setText('Unable to kill torrent client...')

                time.sleep(5)

                try:
                    rtn = subprocess.check_output("pstree | grep %s" % self.torrentClient, shell=True).splitlines()
                except subprocess.CalledProcessError:
                    rtn = 0

                if rtn == 0:
                    self.label_4.setText('Torrent client down, reenabling connection...')
                    os.system('ifconfig %s up' % interface)
                    os.system('ifconfig lo up')

                elif not any(self.torrentClient in q for q in task):
                    self.label_4.setText('No torrent client found, reenabling connection...')
                    os.system('ifconfig %s up' % interface)
                    os.system('ifconfig lo up')

            time.sleep(0.5)
            QtGui.qApp.processEvents()


    # # find tunnel and verify up/down status
    # try:
    #     task = subprocess.check_output("pstree | grep %s" % torrentClient, shell=True).splitlines()
    # except subprocess.CalledProcessError:
    #     task = ''

    # if enable == 1 and not any('tun' in t for t in output) and any(torrentClient in q for q in task):
    #     enable = 0
    #     os.system('ifconfig %s down' % interface)

    #     try:
    #         subprocess.call("pkill -f %s" % torrentClient, shell=True)
    #     except OSError:
    #         print('Unable to kill torrent client...')

    #     # Pause to kill process
    #     time.sleep(5)

    #     try:
    #         rtn = subprocess.check_output("pstree | grep %s" % torrentClient, shell=True).splitlines()
    #     except subprocess.CalledProcessError:
    #         rtn = 0

    #     if rtn == 0 and enable == 0:
    #         print('Torrent client down, reenabling connection...')
    #         os.system('ifconfig %s up' % interface)
    #         os.system('ifconfig lo up')
    #         enable = 1

    #     elif not any(torrentClient in q for q in task) and enable == 0:
    #         print('No torrent client found, reenabling connection...')
    #         os.system('ifconfig %s up' % interface)
    #         os.system('ifconfig lo up')
    #         enable = 1

    # return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyGUI()

    window.show()
    sys.exit(app.exec_())