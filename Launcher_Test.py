import random
import serial
import serial.tools.list_ports
import sys


def findMEGA():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "0042" in p[2]:
            return (p[0])
    return ('NULL')


def startup():
    mega_port = findMEGA()
    try:
        MEGA = serial.Serial(mega_port, 115200, timeout=1)
    except FileNotFoundError as e:
        print("findMEGA returned 'NULL' looking for Arduino Mega")
    except serial.SerialException as ex:
        pass
    else:
        MEGA.baudrate = 115200
        return MEGA

def wait_for_data(MEGA):
    getdata = False
    while not getdata:
        if MEGA.is_open:
            try:
                startMarker = MEGA.read().decode()
            except Exception as e:
                print('[MegaDataThread] : ERROR: ' + str(e))
            else:
                if startMarker == "<":
                    megaDataStr = MEGA.read(25)  # READ DATA FORMATTED AS ('< 1 2 3 4 5 >')
                    megaDataTemp = list(megaDataStr.decode())
                    megaDataTemp.insert(0, startMarker)
                    megaData = megaDataTemp[:megaDataTemp.index(">") + 1]
                    tempData = "".join(megaData)
                    tempData = tempData.strip("<")
                    tempData = tempData.strip(">")
                    tempData = tempData.split(",")
                    print("[MegaData] : Tempdata=  " , tempData)

                    getdata = False
        else:
            print("lost Mega")


def get_input(MEGA):

    launch = input("Launch Ball? (y/n)")

    if launch == "y":
        ballfeed = "1"
    else:
        ballfeed = "0"

    used_distance = input("Enter Distance")
    used_distance = int(used_distance)
    print(used_distance)

    # motor_speed = input("Enter Motorspeed:")
    # print(motor_speed)

    difficulty = "1"

    RPM = -1.13635244 * used_distance ** 2.0 + 97.7378699 * used_distance + 646.034298  # <-- Polynomial fit
    motor_speed = round((RPM / 5000) * 255)  # Value between 0-255 (On 24 V: 0-5000 RPM)
    targetChoice = int(random.choice([1, 2 , 3, 4]))
    estimated_tof = (0.120617 * used_distance) * 1000  # + difficulty_time
    estimated_tof = round(estimated_tof, 2)
    motor_speed = str(motor_speed)
    send_data = '<' + motor_speed + ',' + motor_speed + ',' + str(targetChoice) + ',' + str(
        difficulty) + ',' + ballfeed + ',' + str(estimated_tof) + '>'

    print("Send this data to Motors?")
    print(send_data)
    send = input("y/n:")

    if send == "y":
        MEGA.write(send_data.encode())
        wait_for_data(MEGA)
    else:
        print("try again?")
        opt = input("y/n:")
        if opt == "n":
            sys.exit()


MEGA = startup()

while True:
    get_input(MEGA)
