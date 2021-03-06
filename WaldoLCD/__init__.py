# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin

# import os
# import subprocess
import threading
import qrcode
import serial
from . import lcd
from . import waldoprinter
from .lcd.pconsole import pconsole
from .lcd.session_saver import session_saver
import os
from .lcd.Language import lang
import time



class WaldolcdPlugin(octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.AssetPlugin,
                    octoprint.plugin.StartupPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    ):

    def __init__(self, **kwargs):
        super(WaldolcdPlugin, self).__init__(**kwargs)
        self.lcd_thread = None
        self.file_lock = False


    def get_settings_defaults(self):
        return dict(
            Wifi = {},
            Model = None,
            Language = None,
            Temp_Preset = {},
            sorting_config = {}

            )

    def _get_api_key(self):
        return self._settings.global_get(['api', 'key'])

    def _write_qr_to_file(self, api_key):
        folder = self.get_plugin_data_folder()
        img = qrcode.make(api_key)
        img.save('{}/{}'.format(folder, 'qr_code.png'))

    def on_after_startup(self):
        
        lang_pack = self._settings.get(['Language'])
        self._logger.info("Loading Language Pack " + str(lang_pack))
        lang.load_language(lang_pack)

        passing = lang.pack['Load_Success']['pass']
        self._logger.info("Loading Success? " + str(passing) + " ######################################")
        waldoprinter.lang = lang



        self._logger.info("WaldoLCD Starting up")
        # saves the printer instance so that it can be accessed by other modules
        waldoprinter.printer_instance = self
        self.lcd_thread = threading.Thread(target=lcd.start, args=())
        self.lcd_thread.start()
        self._logger.info("Rendering screen... ")

        # writes printer's QR code to plugin data folder
        api_key = self._get_api_key()
        self._write_qr_to_file(api_key)

        self._logger.info('Preparing Callback to PConsole')
        self._printer.register_callback(pconsole)
        self._logger.info('Callback Complete')

        #get the helper function to determine if the board is updating or not
        helpers = self._plugin_manager.get_helpers("firmwareupdater", "firmware_updating","flash_usb")
        if helpers:
            self._logger.info("Firmware updater has helper functions")

            #Grab firmware updating
            if "firmware_updating" in helpers:            
                self.firmware_updating = helpers["firmware_updating"]
            else:
                self.firmware_updating = self.updater_placeholder

            #Grab flash usb
            if "flash_usb" in helpers:
                self.flash_usb = helpers["flash_usb"]
            else:
                self.flash_usb = self.updater_placeholder
        #if there aren't any helpers then use place holders
        else :
            self._logger.info("Firmware updater does not have a helper function")
            self.firmware_updating = self.updater_placeholder
            self.flash_usb = self.updater_placeholder

        #Get the helpers for Meta Reader
        file_helpers = self._plugin_manager.get_helpers("Meta_Reader", "start_analysis", "collect_data")
        if file_helpers:
            #Grab start analysis
            if "start_analysis" in file_helpers:
                self.start_analysis = file_helpers["start_analysis"]
            else:
                self.start_analysis = self.updater_placeholder

            #Grab Collect Data
            if "collect_data" in file_helpers:
                self.collect_data = file_helpers["collect_data"]
            else:
                self.collect_data = self.updater_placeholder
        #if there aren't any helpers then use place holders
        else:
            self._logger.info("Meta Reader does not have helper Functions")
            self.start_analysis = self.updater_placeholder
            self.collect_data = self.updater_placeholder

        #get helper from Filament runout sensor
        filament_helpers = self._plugin_manager.get_helpers("filament", "check_auto_pause")
        self.check_auto_pause = None
        if filament_helpers:
            self._logger.info("Filament Helpers Exist ###########################")
            self._logger.info(str(filament_helpers))
            if "check_auto_pause" in filament_helpers:
                self.check_auto_pause = filament_helpers["check_auto_pause"]
        else:
            self._logger.info("Filament Helpers DO NOT Exist ###########################")
            self._logger.info(str(filament_helpers))
            

    def on_event(self,event, payload):

        # self._logger.info(str(event))
        # self._logger.info(str(payload))

        def reset_data():
            session_saver.save_variable('FLOW', 100)
            session_saver.save_variable('FEED', 100)
            session_saver.save_variable('FAN', 0)
            self._printer.feed_rate(100)
            self._printer.flow_rate(100)
            self._printer.commands('M106 S0')

        session_saver.saved['event'] = event

        if event == 'PrintStarted':
            #callbacks
            reset_data()
        elif event == 'PrintFailed':
            reset_data()
        elif event == 'PrintDone':
            reset_data()
        elif event == 'PrintCancelled':
            reset_data()
        elif event == "FileDeselected":
            reset_data()
        elif event == "UpdatedFiles":
            if 'file_callback' in session_saver.saved:
                session_saver.saved['file_callback']()
        #throw events to anyone who wants to listen
        session_saver.update_event(event, payload)



    def updater_placeholder(self, **kwargs):
        return False

    def support_hex_files(*args, **kwargs):
        return dict(
                firmware=dict(
                    hex_file=["hex", "HEX"]
                    )
            )


    def get_update_information(self):
        return dict(
            waldolcd=dict(
                displayName="WaldoLCD",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="WheresWaldo",
                repo="WaldoLCD",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/WheresWaldo/WaldoLCD/archive/{target_version}.zip"
            )
        )

    def serial_hook(self, comm_instance, port, baudrate, connection_timeout, *args, **kwargs):

        if port is None or port == 'AUTO':
            # no known port, try auto detection
            comm_instance._changeState(comm_instance.STATE_DETECT_SERIAL)
            serial_obj = comm_instance._detectPort(False)
            if serial_obj is None:
                comm_instance._log("Failed to autodetect serial port")
                comm_instance._errorValue = 'Failed to autodetect serial port.'
                comm_instance._changeState(comm_instance.STATE_ERROR)
                eventManager().fire(Events.ERROR, {"error": comm_instance.getErrorString()})
                return None
    
        else:
            # connect to regular serial port
            comm_instance._log("Connecting to: %s" % port)
            if baudrate == 0:
                serial_obj = serial.Serial(str(port), 250000, timeout=connection_timeout, writeTimeout=10000, parity=serial.PARITY_ODD)
            else:
                serial_obj = serial.Serial(str(port), baudrate, timeout=connection_timeout, writeTimeout=10000, parity=serial.PARITY_ODD)
            serial_obj.close()
            serial_obj.parity = serial.PARITY_NONE
            serial_obj.open()
            self._logger.info("########################################")
            self._logger.info("Restarting Marlin")
            #Reset the controller
            serial_obj.setDTR(1)
            time.sleep(0.1)
            serial_obj.setDTR(0)
            time.sleep(0.2)
            self._logger.info("Marlin Reset")     
            #Flush input and output
            self._logger.info("Flushing Input and Output!")
            serial_obj.flushOutput()
            serial_obj.flushInput()
            self._logger.info("Finished Flushing")
            #write something to the serial line to get rid of any bad characters in the buffer
            self._logger.info("Writing M105")
            first_write = "M105\n"
            serial_obj.write(first_write)

            self._logger.info("########################################")

        return serial_obj

__plugin_name__ = "WaldoLCD"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WaldolcdPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.transport.serial.factory": __plugin_implementation__.serial_hook,
        "octoprint.filemanager.extension_tree": __plugin_implementation__.support_hex_files
    }
