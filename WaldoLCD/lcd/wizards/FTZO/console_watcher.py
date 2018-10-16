# -*- coding: utf-8 -*-
# @Author: Matt Pedler
# @Date:   2017-10-31 13:02:40
# @Last Modified by:   BH
# @Last Modified time: 2018-10-15 19:12:12

import octoprint.printer
from WaldoLCD import waldoprinter
import time
from kivy.clock import Clock
from kivy.logger import Logger
class Console_Watcher(octoprint.printer.PrinterCallback, object):
    called_callback = False
    def __init__(self,callback, *args, **kwargs):
        super(Console_Watcher, self).__init__(*args, **kwargs)
        self.callback = callback

        #register the observer with octoprint
        Logger.info("Registering Console Watcher")
        waldoprinter.printer_instance._printer.register_callback(self)
        
    def __del__(self):
        Logger.info("Deleting Console Watcher through __del__!")
        self.callback = None
        del self

    def on_printer_add_message(self, data):
        if data.find("ACTION COMPLETE!") != -1:
            Clock.schedule_once(self.callback_caller, 0.0)
            

    def callback_caller(self, *args, **kwargs):
        #add protections in case self.callback goes out of scope
        if callable(self.callback):
            self.callback()
        else:
            Logger.info("Callback is not callable!")
        waldoprinter.printer_instance._printer.unregister_callback(self)