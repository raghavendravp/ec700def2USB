import glib
from pyudev import Context, Monitor
import pyudev
import subprocess
import MySQLdb
import datetime
import sys
import hashlib
import socket
import os
import time
from os.path import join, getsize

def hashfile(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

usbsl = ''

def get_block_infos(dev_name):
    dev = pyudev.Device.from_device_file(context, dev_name)

    try:
        objProc = subprocess.Popen('lsblk --nodeps %s | grep -v SIZE  | awk \'{ print $4 }\'' % dev.get('DEVNAME'),
                                   shell=True, bufsize=0, executable="/bin/bash", stdin=None, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

    except OSError, e:
        print(e)

    # stdOut.communicate() --> dimension [0]: stdout, dimenstion [1]: stderr
    stdOut = objProc.communicate()

    #fetch all data for usb
    devnm = dev.get('DEVNAME')  #--
    plbl = dev.get('ID_FS_LABEL')   #--
    fstyp = dev.get('ID_FS_TYPE')    #--
    dmdl = dev.get('ID_MODEL')     #--
    ptid = dev.get('ID_PATH')   #--
    vdrnm = dev.get('ID_VENDOR') #--
    capc = stdOut[0].strip()   #--
    now = datetime.datetime.now()
    inow = now.strftime('%Y-%m-%d %H:%M:%S')
    try:    #--
        global usbsl
        usbsl = dev.get('ID_SERIAL_SHORT')
    except:
        global usbsl
        usbsl = dev.get('ID_SERIAL')

    #populate usb_events with USB insert event data and all information of USB device
    db = MySQLdb.connect('localhost', 'usbusr', 'reward', 'usb_events')

    cur = db.cursor()
    sql2 = "INSERT INTO usb_events.usb_info (evtdttime, dev_name, part_label, fstype, \
                devmodel, pathid, vendornm, capacity, usbsrl) \
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (inow, devnm, plbl, fstyp, dmdl, ptid, vdrnm, capc, usbsl)
    try:
        cur.execute(sql2)
        db.commit()
    except:
        db.rollback()
    db.close()

try:
    from pyudev.glib import MonitorObserver

    def device_event(observer, device):
        get_block_infos(device.get('DEVNAME'))


except:
    from pyudev.glib import GUDevMonitorObserver as MonitorObserver

    def device_event(observer, action, device):
        get_block_infos(device.get('DEVNAME'))
        #now iterate all directories for files only
        db = MySQLdb.connect('localhost', 'usbusr', 'reward', 'usb_events')
        cur = db.cursor()
        time.sleep(3) # may be needed to mount usb
        for root, dirs, files in os.walk('/media'):
            #fetch file listing
            for file in files:
                flnm = os.path.join(root, file)
                hs = hashfile(flnm)
                sql1 = "INSERT INTO usb_events.file_info (usbsrl, hname, dir_filenm, filehash) \
                        VALUES ('%s', '%s', '%s', '%s')" % \
                        (usbsl, socket.gethostname(), flnm, hs)
                #print sql1
                try:
                    cur.execute(sql1)
                    db.commit()
                except:
                    db.rollback()

context = Context()
monitor = Monitor.from_netlink(context)

monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor)

observer.connect('device-event', device_event)
monitor.start()

glib.MainLoop().run()
