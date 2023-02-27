#!/usr/bin/env python3
# coding=utf-8
import os, struct, sys
from DOGZILLALib import DOGZILLA
import time
import threading

import board
import neopixel

stati = ["idle", "felice", "arrabbiato"]
statoCorrente = stati[0]

# Imposta il numero di LED e il pin GPIO utilizzato
NUM_LED = 24
PIN = board.D12 # GPio 12
intensità = 0.2 # da 0 a 1

occhi = neopixel.NeoPixel(PIN, NUM_LED) # Inizializza la striscia Neopixel
occhi.brightness = intensità
for i in range(5):
    occhi.show()
    occhi.fill((0, 0, 0))
    occhi.show()
    occhi.fill((0, 255, 0))
    occhi.show()
    time.sleep(.1)
    occhi.show()
    occhi.fill((0, 0, 0))
    occhi.show()
    time.sleep(.1)
print("NEOPIXEL tutto ok")

def arrabbiato_task():
    global statoCorrente
    global stati
    occhi.brightness = 1
    for i in range(10):
        occhi.show()
        occhi.fill((0, 0, 0))
        occhi.show()
        occhi.fill((255, 0, 0))
        occhi.show()
        time.sleep(.1)
        occhi.show()
        occhi.fill((0, 0, 0))
        occhi.show()
        time.sleep(.1)
    statoCorrente = stati[0]

# Definizione di una funzione che esegue l'effetto arcobaleno sui Neopixel
def rainbow(occhi, wait):
    for z in range(3):
        for j in range(256):
            for i in range(NUM_LED):
                color = wheel((i+j) & 255)
                occhi[i] = color
            occhi.show()
            time.sleep(wait / 1000.0)

# Funzione per calcolare il valore del colore in base alla posizione
def wheel(pos):
    pos = 255 - pos
    if pos < 85:
        return (255 - pos * 3, 0, pos * 3)
    elif pos < 170:
        pos -= 85
        return (0, pos * 3, 255 - pos * 3)
    else:
        pos -= 170
        return (pos * 3, 255 - pos * 3, 0)

# V1.1.9
class Dogzilla_Joystick(object):

    def __init__(self, dog, js_id=0, debug=True):
        self.__debug = debug
        self.__js_id = int(js_id)
        self.__js_isOpen = False
        self.__dog = dog
        self.__pace_width = 100
        self.__pace_freq = 2
        self.__height = 105
        self.__ignore_count = 20
        self.__play_ball = 0

        self.__WIDTH_SCALE_X = 0.25
        self.__WIDTH_SCALE_Y = 0.2
        self.__WIDTH_SCALE_Z = 1.0
        
        self.STATE_OK = 0
        self.STATE_NO_OPEN = 1
        self.STATE_DISCONNECT = 2
        self.STATE_KEY_BREAK = 3

        # Find the joystick device.
        print('Joystick Available devices:')
        # Shows the joystick list of the Controler, for example: /dev/input/js0
        for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                print('    /dev/input/%s' % (fn))

        # Open the joystick device.
        try:
            js = '/dev/input/js' + str(self.__js_id)
            self.__jsdev = open(js, 'rb')
            self.__js_isOpen = True
            print('---Opening %s Succeeded---' % js)
        except:
            self.__js_isOpen = False
            print('---Failed To Open %s---' % js)
        
        # Defining Functional List
        self.__function_names = {
            # BUTTON FUNCTION
            0x0100 : 'A',
            0x0101 : 'B',
            0x0102 : 'X',
            0x0103 : 'Y',
            0x0104 : 'L1',
            0x0105 : 'R1',
            0x0106 : 'SELECT',
            0x0107 : 'START',
            0x0108 : 'MODE',
            0x0109 : 'BTN_RK1',
            0x010A : 'BTN_RK2',

            # AXIS FUNCTION
            0x0200 : 'RK1_LEFT_RIGHT',
            0x0201 : 'RK1_UP_DOWN',
            0x0202 : 'L2',
            0x0203 : 'RK2_LEFT_RIGHT',
            0x0204 : 'RK2_UP_DOWN',
            0x0205 : 'R2',
            0x0206 : 'WSAD_LEFT_RIGHT',
            0x0207 : 'WSAD_UP_DOWN',
        }

    def __del__(self):
        if self.__js_isOpen:
            self.__jsdev.close()
        if self.__debug:
            print("\n---Joystick DEL---\n")

    # Return joystick state
    def is_Opened(self):
        return self.__js_isOpen
    
    # reset DOGZILLA
    def __dog_reset(self):
        self.__play_ball = 0
        self.__dog.reset()
        self.__pace_width = 100
        self.__pace_freq = 2
        self.__height = 105
        
    # Control robot
    def __data_processing(self, name, value):
        global statoCorrente
        global stati

        # ANALOGICI
        if name == 'RK1_UP_DOWN':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__pace_width))
            fvalue = int(self.__pace_width * self.__WIDTH_SCALE_X * value)
            self.__dog.move('x', fvalue)
        elif name=="RK1_LEFT_RIGHT":
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__pace_width))
            fvalue = int(self.__pace_width * self.__WIDTH_SCALE_Y * value)
            self.__dog.move('y', fvalue)
        
        elif name == 'BTN_RK1':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     self.__pace_width = self.__pace_width + 40
            #     if self.__pace_width > 100:
            #         self.__pace_width = 20

        elif name == 'RK2_UP_DOWN':
            value = value / 32767
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            fvalue = value * 15
            self.__dog.attitude('p', fvalue)
        elif name == 'RK2_LEFT_RIGHT':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__pace_width))
            # fvalue = -value * 24
            # self.__dog.attitude('r', fvalue)
            if value == 0:
                self.__dog.turn(0)
            elif value == 1 or value == -1:
                fvalue = int(self.__pace_width * self.__WIDTH_SCALE_Z * value)
                self.__dog.turn(fvalue)
        
        elif name == 'BTN_RK2':
            # if value == 1:
            #     self.__pace_freq = self.__pace_freq + 1
            #     if self.__pace_freq > 3:
            #         self.__pace_freq = 1
            #     if self.__pace_freq == 1:
            #         self.__dog.pace("slow")
            #     elif self.__pace_freq == 2:
            #         self.__dog.pace("normal")
            #     elif self.__pace_freq == 3:
            #         self.__dog.pace("high")
            if self.__debug:
                print (name, ":", value, self.__pace_freq)

        elif name == 'WSAD_LEFT_RIGHT':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            fvalue = (value * self.__pace_width * self.__WIDTH_SCALE_Y)
            self.__dog.move('y', fvalue)
        elif name == 'WSAD_UP_DOWN':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__pace_width))
            fvalue = int(value * self.__pace_width * self.__WIDTH_SCALE_X)
            self.__dog.move('x', fvalue)

        # TASTI PRINCIPALI
        elif name == 'A':
            if self.__debug:
                print (name, ":", value)
            statoCorrente = stati[1]
            arrabbiato = threading.Thread(target=arrabbiato_task, name="arrabbiato_task")
            arrabbiato.setDaemon(True)
            arrabbiato.start()
            # if value == 1:
            #     self.__height = self.__height - 10
            #     if self.__height < 75:
            #         self.__height = 75
            #     self.__dog.translation('z', self.__height)
        elif name == 'B':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     self.__dog.attitude('y', -35)
            # else:
            #     self.__dog.attitude('r', 0)
            #     self.__dog.attitude('y', 0)
        elif name == 'X':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     self.__dog.attitude('y', 35)
            # else:
            #     self.__dog.attitude('r', 0)
            #     self.__dog.attitude('y', 0)
        elif name == 'Y':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     self.__height = self.__height + 10
            #     if self.__height > 115:
            #         self.__height = 115
            #     self.__dog.translation('z', self.__height)
        
        # DORSALI
        elif name == 'L1':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     # self.__dog.action(3) # 匍匐前进 CRAWL
            #     self.__dog.action(10) # 三轴联动 3 Axis
        elif name == "L2":
            # value = ((value/32767)+1)/2
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            # if value == 1:
            #     # self.__dog.action(17) # 求食 PRAY
            #     self.__dog.action(16) # 左右摇摆 SWING
            
        elif name == 'R1':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     # self.__dog.action(16) # 左右摇摆 SWING
            #     if self.__play_ball == 0:
            #         self.__play_ball = 2
            #         task_1 = threading.Thread(target=self.__play_ball_task, args=(self.__play_ball,), name="play_ball_task")
            #         task_1.setDaemon(True)
            #         task_1.start()
        elif name == "R2":
            # value = ((value/32767)+1)/2
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            # if value == 1:
            #     self.__dog.action(11) # 撒尿 PEE
                    
        elif name == 'SELECT':
            if self.__debug:
                print (name, ":", value)
            # if value == 1:
            #     self.__obstacle_crossing()
        elif name == 'START':
            if self.__debug:
                print (name, ":", value)
            #   Stop the action and restore the original position
            if value == 1:
                self.__dog_reset()

        elif name == 'MODE':
            if self.__debug:
                print (name, ":", value)
        

        else:
            pass

    # Handles events for joystick
    def joystick_handle(self):
        if not self.__js_isOpen:
            # if self.__debug:
            #     print('Failed To Open Joystick')
            return self.STATE_NO_OPEN
        try:
            evbuf = self.__jsdev.read(8)
            if evbuf:
                time, value, type, number = struct.unpack('IhBB', evbuf)
                func = type << 8 | number
                name = self.__function_names.get(func)
                # print("evbuf:", time, value, type, number)
                # if self.__debug:
                #     print("func:0x%04X, %s, %d" % (func, name, value))
                if name != None:
                    self.__data_processing(name, value)
                else:
                    if self.__ignore_count > 0:
                        self.__ignore_count = self.__ignore_count - 1
                    if self.__debug and self.__ignore_count == 0:
                        print("Key Value Invalid")
            return self.STATE_OK
        except KeyboardInterrupt:
            if self.__debug:
                print('Key Break Joystick')
            return self.STATE_KEY_BREAK
        except:
            self.__js_isOpen = False
            print('---Joystick Disconnected---')
            return self.STATE_DISCONNECT

    # reconnect Joystick
    def reconnect(self):
        try:
            js = '/dev/input/js' + str(self.__js_id)
            self.__jsdev = open(js, 'rb')
            self.__js_isOpen = True
            self.__ignore_count = 20
            print('---Opening %s Succeeded---' % js)
            return True
        except:
            self.__js_isOpen = False
            # if self.__debug:
            #     print('Failed To Open %s' % js)
            return False


if __name__ == '__main__':
    g_debug = False
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == "debug":
            g_debug = True
    print("debug=", g_debug)

    g_dog = DOGZILLA()
    js = Dogzilla_Joystick(g_dog, debug=g_debug)
    try:
        while True:
            if statoCorrente == stati[0]:
                print("stato ==> ", stati[0])
                rainbow(occhi, wait=10)
            elif statoCorrente == stati[1]:
                print("stato ==> ", stati[1])
                arrabbiato = threading.Thread(target=arrabbiato_task, name="arrabbiato_task")
                arrabbiato.setDaemon(True)
                arrabbiato.start()
                

            
            state = js.joystick_handle()
            if state != js.STATE_OK:
                if state == js.STATE_KEY_BREAK:
                    break
                time.sleep(1)
                js.reconnect()
            
    except KeyboardInterrupt:
        pass
    del js
