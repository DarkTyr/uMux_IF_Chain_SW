

import serial
import random
import string

# COM_PORT = "COM18"
COM_PORT = "COM20"
LENGTH = 40
CMD = "USB:LOOPBACK:"
TERM = "\n"

com = serial.Serial(port=COM_PORT, timeout=1)

com.write("*IDN?\n".encode())
com.read_until()

IDN = com.read_until()
print("Firmware IDN: {}".format(IDN))

n = 0
def usb_loopback_data_test(num_itters, print_debug):
    for n in range(num_itters):
        if(print_debug):
            print("Itteration Number : {}".format(n))

        data = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(LENGTH))
        if(print_debug > 1):
            print("\tSent Data: {}". format(data))

        com.write((CMD + data + TERM).encode())
        com.read_until()    # Read the RCVD return form the firmware, this just states it was a valid command
        ret = com.read_until()

        if(print_debug > 1):
            print("\tRCVD Data: {}". format(ret.decode()[:-1]))

        if(ret.decode()[:-1] == data):
            pass
        else:
            print("RVCD bad data back: \n\t{} != {}".format(data, ret))
            break

