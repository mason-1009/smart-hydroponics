#!/usr/bin/env python3

import threading
import time

class test(object):
    
    counter1=0
    counter2=0

    def thread1(self):
        while True:
            time.sleep(1)
            self.counter1=self.counter1+1

    def thread2(self):
        while True:
            time.sleep(0.5)
            self.counter2=self.counter2+1
            
    def __init__(self):
        # start threading
        thread1obj = threading.Thread(target=self.thread1)
        thread2obj = threading.Thread(target=self.thread2)

        # run threads
        thread1obj.start()
        thread2obj.start()

        while True:
            time.sleep(1)
            print(self.counter1)
            print(self.counter2)

if __name__ == "__main__":
    doit=test()
