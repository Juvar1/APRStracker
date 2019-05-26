# APRStracker
Simple APRS Receiver and GPX Exporter for Mobilinkd TNC with bluetooth.

Keeps track of the route of one selected station and saves it to GPX file format. Also compresses it in to ZIP archive often needed on online map services.

### Supported and tested configuration
- Works with Python version 3.5
- Tested with [Mobilinkd TNC](https://store.mobilinkd.com/) through bluetooth.
- On the transmitting end, aka APRS tracker, Mobilinkd TNC is connected to Android phone with [APRSdroid](https://aprsdroid.org/) installed. TNC is then connected to Baofeng [UV-5RTP](http://baofengradio.com/enProShowcn.asp?ID=425) walkie talkie. It's important to notice that repeater path in APRSdroid settings must be empty so that only recipient is our own base station.
- On the receiving end, aka APRS base station, other Mobilinkd TNC is connected to Baofeng [UV-5R Plus](http://baofengradio.com/enProShowcn.asp?ID=412) and with bluetooth it's connected to PC with this program running. Also there is external outdoor antenna used. It is self made with [these instructions](http://www.users.on.net/~endsodds/jpole.htm).

### Usage
- Choose tracked station with this if clause <code>if(data.src.count("OH1FWW")):</code> and run program.
- Program prints status and debug information to console window while running.
- When all necessary data is gathered press <code>Ctrl+C</code> to stop program.
- Program closes bluetooth socket and saves all trackpoints to GPX file.
- GPX filename is formed as follows <code>output_[C style timestamp].gpx</code> to prevent overwriting old files.
- At the end program creates compressed ZIP file containing that GPX file.

### How it is working
1. All bluetooth devices is put in to array. If not found any then prints out error message and exit program else prints out all found devices and selects Mobilinkd TNC. If Mobilinkd TNC is not in a list then prints error message and exit program. 
2. Program tries to connect to Mobilinkd TNC. If it's not succeed then prints error message and exit program. 
3. Program goes to work loop and receives all APRS messages from TNC with KISS protocol and decodes them. Source address is compared to predefined value. If it match then parses coordinates from message and saves them to array with timestamp. 
4. When user presses <code>Ctrl+C</code> work loop is terminated and bluetooth socket is closed and array of coordinates is saved to GPX file. Filename contains unique timestamp to prevent overwriting old files. At the end program creates compressed ZIP file containing that GPX file.

### Known issues
I don't know if it's only me or is it common problem, but bluetooth adapter is not always found and sometimes Mobilinkd device is not found. Disconnecting the adapter for short time and restarting Mobilinkd device will help. I have cheap Chinese bluetooth adapter.

### Help
If something is not working in program I'm here for help. Contact if you have any problems.
