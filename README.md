# ec700def2USB
Course Project for Defense II - Hash files upon USB insert

1. usbinsert.py can be run as a daemon to detect USB inserts and to perform a file inventory.
2. compile the kernel module from writecatch.c and make writecatch.ko  (insmod writecatch.ko)
3. run the command "tail -f /var/log/kern.log | python -u writemon.py" to have the logs populated upon every file write from  any executables run off the USB 
4. logreader.py has to be run as a scheduled task to read off the logs created by the kernel module and the writemon.py.


