# APRStracker.py
#
# Simple APRS Receiver and GPX Exporter for Python 3.5
# Works only with Mobilinkd TNC with Bluetooth
#
# Copyright (C) 2019, Juha-Pekka Varjonen, Juvar, OH1FWW
# Version 1.0
#

import bluetooth, re, ax25
from datetime import datetime
import zipfile, zlib

# search all available bt devices and put them to array
results = []
try:
    btDevices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = 8)
except bluetooth.btcommon.BluetoothError as err: 
    print("Info: %s" % err.args)
    exit()
except OSError: #No such device (if no bt adapters)
    print("Info: No adapters")
    exit()
for addr, name in btDevices:
    results.append([name,addr,1])


# inform user about available bt devices
# Automatically select Mobilinkd TNC
# exit if not any bt devices
mobilinkd = ""
if(len(results) > 0):
    print("Info: Found %d devices" % len(results))
    for (name, host, port) in results:
        print(name)
        if(name.count("Mobilinkd")):
            mobilinkd = host
else:
    print("Info: No devices found")
    exit()
if(mobilinkd == ""):
    print("Info: No Mobilinkd TNC found")
    exit()


# try connect to selected bt device
try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mobilinkd, 1))
except bluetooth.btcommon.BluetoothError as err:
    print("Info: %s" % err.args)
    exit()
print("Info: Succesfully connected to host: %s" % mobilinkd)


# receive data from TNC and decode ax25 and filter with station ID
# exit with CTRL+C and finalize connection and GPX file
rec = False     # initially starting with frame end
aprsResult = "" # initially decoded aprs message is empty
trackPointArray = [] # initialize GPX TrackPoint Array
try:
    while True:
        msg = sock.recv(1024) # wait input, buffer max size

        # break received string into characters
        for char in msg:

            # Python3 internal bugfix
            if(isinstance(char, int)):
                value = chr(char)
            else:
                value = char

            # FEND, frame start/end char (KISS protocol)
            if(ord(value) == 0xc0):
                rec = not rec
                if(rec == False): # if frame end received
                    data = ax25.Ax25(aprsResult)

                    # frame error condition
                    if(data.info.__len__() == 0):
                        rec = True
                        continue # start from beginning

                    # tracked call sign
                    if(data.src.count("OH1FWW")):
                        # parse data
                        test = re.search(r"^(.).*(\d{4}\.\d\d[NS])(.)(\d{5}\.\d\d[EW])(.).*",data.info)
                        if test:
                            # object data
                            if (data.info[0] == "!" or data.info[0] == "="):

                                # coordinate conversion
                                # degrees and minutes to decimal degrees
                                lat = float(test.group(2)[:2]) + (float(test.group(2)[2:7]) / 60.0);
                                lon = float(test.group(4)[:3]) + (float(test.group(4)[3:8]) / 60.0);
                                if(test.group(2)[-1:] == "S"):
                                    lat = -abs(lat)
                                if(test.group(4)[-1:] == "W"):
                                    lon = -abs(lon)

                                trackPointArray.append("<trkpt lat=\"%.8f\" lon=\"%.8f\"><time>%s</time></trkpt>\n" % (lat,lon,datetime.utcnow().isoformat()))
                                # print debug info
                                print("Received from: %s, lat: %.8f, lon: %.8f" % (data.src,lat,lon))

                    aprsResult = ""
            elif(rec == True):
                aprsResult += value
        
except KeyboardInterrupt:
    # disconnect and close socket
    sock.shutdown(2) # socket.SHUT_RDWR = 2
    sock.close()
    print("\nsocket closed")

    # create filename with local timestamp
    filename = "output_%s.gpx" % datetime.now().ctime()
    with open(filename, "w") as text_file:
        text_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        text_file.write("<gpx version=\"1.0\">\n")
        text_file.write("    <name>route</name>\n")
        text_file.write("    <trk>\n")
        text_file.write("        <trkseg>\n")
        for line in trackPointArray:
            text_file.write("        %s" % line)
        text_file.write("        </trkseg>\n")
        text_file.write("    </trk>\n")
        text_file.write("</gpx>\n")

    print("GPX file saved")

    with zipfile.ZipFile(filename + ".zip") as myzip:
        myzip.write(filename, compress_type=zipfile.ZIP_DEFLATED)
    
    print("ZIP file created")
