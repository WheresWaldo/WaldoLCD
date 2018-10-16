# -*- coding: utf-8 -*-
# @Author: Matt Pedler
# @Date:   2017-10-20 12:29:26
# @Last Modified by:   BH
# @Last Modified time: 2018-10-15 17:05:11
#WaldoLCD

from WaldoLCD import waldoprinter
from WaldoLCD.lcd.scrollbox import Scroll_Box_Icons, Waldo_Icons
from WaldoLCD.lcd.wizards.zoffset.z_offset_wizard import ZoffsetWizard
from WaldoLCD.lcd.wizards.filament_wizard.filament_wizard import FilamentWizard
from WaldoLCD.lcd.wizards.FTZO.fine_tune_zoffset import Fine_Tune_ZOffset
from WaldoLCD.lcd.wizards.bed_calibration.bed_calibration_wizard import Bed_Calibration
from WaldoLCD.lcd.wizards.PID_Autotune.PID_Overseer import PID_Overseer
from wizard_bb import Wizard_BB

#kivy
from kivy.logger import Logger

class Wizards(object):
    """
    This Class will the wizards page under Utilities >> Wizards. 
    This change will happen due to the Dual Extruder Update. We need some sort of code
    to setup the mode for each wizard. This class will detect how the printer is set up
    then pass on that configuration to the selected wizard. 

    Modes are C2, R2, R2_Dual_Extrusion. 

    This class is also here to optomize code. 
    """
    def __init__(self, soft_load=False,**kwargs):
        super(Wizards, self).__init__()
        #set up variables

        if not soft_load:
            back_destination = 'wizards_screen'
        else:
            back_destination = 'main'
        
        self.acceptable_wizards={#Wizards sub screen
                                'ZOFFSET': {'name':'zoffset', 
                                      'title':waldoprinter.lang.pack['Utilities']['ZOffset'], 
                                      'back_destination': back_destination, 
                                      'function': self.generate_zoffset_wizard},
                        
                                'FIL_LOAD': {'name':'filamentwizard',
                                       'title':waldoprinter.lang.pack['Utilities']['Filament'],
                                       'back_destination':back_destination, 
                                       'function': self.generate_filament_wizard},
                        
                                'FIL_CHANGE': {'name':'filamentwizard',
                                        'title':waldoprinter.lang.pack['Utilities']['Filament'],
                                        'back_destination':back_destination, 
                                        'function': self.generate_filament_change_wizard},
                        
                                'FINE_TUNE':{'name': 'fine_tune_wizard', 
                                       'title': waldoprinter.lang.pack['Utilities']['FT_Wizard'], 
                                       'back_destination': back_destination, 
                                       'function': self.fine_tune_wizard},
                        
                                'BED_CALIBRATION':{'name': 'bed_calibration', 
                                          'title': waldoprinter.lang.pack['Utilities']['Bed_Cal'], 
                                          'back_destination': back_destination, 
                                          'function': self.bed_calibration},
                                'PID_TUNE': {'name': 'pid_tune',
                                             'title': "PID Autotune Wizard",
                                             'back_destination': back_destination,
                                             'function': self.pid_tune

                                            }
                                }

        self.settings = waldoprinter.printer_instance._settings

        #grab the current state of the machine
        self.state = self.get_state()

        #zip up everything and populate a screen
        if not soft_load:
            self.make_wizards_screen(**kwargs)
        else:
            Logger.info("Loading Wizard Module without an interface")

    def get_state(self):
        # profile = self.settings.global_get(['printerProfiles', 'defaultProfile'])

        # if 'extruder' in profile:
        #     extruder_count = int(profile['extruder']['count'])
        # else:
        #     extruder_count = 1

        #re-enable this code when Dual extrusion is ready for release
        extruder_count = 1

        model = self.settings.get(['Model'])

        return {'model': model,
                'extruder': extruder_count}

    def make_wizards_screen(self, **kwargs):
        name = kwargs['name']
        title = kwargs['title']
        back_destination = kwargs['back_destination']
        
        z = Waldo_Icons('Icons/Zoffset illustration/Z-offset.png', waldoprinter.lang.pack['WaldoIcons']['Z_Offset'], 'ZOFFSET', callback = self.load_wizard)
        fl = Waldo_Icons('Icons/Icon_Buttons/Load Filament.png', waldoprinter.lang.pack['WaldoIcons']['Fil_Load'], 'FIL_LOAD', callback = self.load_wizard)
        fc = Waldo_Icons('Icons/Icon_Buttons/Change Filament.png', waldoprinter.lang.pack['WaldoIcons']['Fil_Change'], 'FIL_CHANGE', callback = self.load_wizard)
        fine_tune = Waldo_Icons('Icons/Zoffset illustration/Fine tune.png', waldoprinter.lang.pack['WaldoIcons']['FTZ_Offset'], 'FINE_TUNE', callback = self.load_wizard)
        pid_tune = Waldo_Icons('Icons/Icon_Buttons/PID.png', "PID Tuner" , 'PID_TUNE', callback = self.load_wizard)
        bed_calib = Waldo_Icons('Icons/Bed_Calibration/Bed placement.png', waldoprinter.lang.pack['WaldoIcons']['Bed_Cal'], 'BED_CALIBRATION', callback = self.load_wizard)
    
        #If it's not an R2 we dont need the bed calibration wizard
        if self.state['model'] == "Robo R2":
          
          buttons = [fc, fl, z, bed_calib, fine_tune, pid_tune]
        else:
          buttons = [fc, fl, z, fine_tune, pid_tune]
    
        current_data = waldoprinter.printer_instance._printer.get_current_data()
        is_printing = current_data['state']['flags']['printing']
        is_paused = current_data['state']['flags']['paused']
        if is_printing or is_paused:
            z.button_state = True
            fine_tune.button_state = True
            pid_tune.button_state = True
            bed_calib.button_state = True
        else:
            for button in buttons:
                button.button_state = False

        c = Scroll_Box_Icons(buttons)
    
        waldoprinter.waldosm._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

    def load_wizard(self, generator = '', name = '', **kwargs):
        wizard = generator
        if wizard in self.acceptable_wizards:
            Logger.info("Changing wizard to " + wizard)
            self.acceptable_wizards[wizard]['function'](name=self.acceptable_wizards[wizard]['name'],
                                                        title = self.acceptable_wizards[wizard]['title'],
                                                        back_destination = self.acceptable_wizards[wizard]['back_destination'])
        else:
            Logger.info(wizard + " Is Not an acceptable wizard")
            return False

    def generate_zoffset_wizard(self, **kwargs):
        wizard = ZoffsetWizard(state=self.state)
        
    def generate_filament_wizard(self, **kwargs):
        # Instantiates the FilamentWizard and gives it a screen. Passes management of filament wizard related screens to FilamentWizard instance.
        wizard = FilamentWizard('LOAD', name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination'], state=self.state) 
               
    def generate_filament_change_wizard(self, **kwargs):
        wizard = FilamentWizard('CHANGE', name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination'], state=self.state) 
        
    def fine_tune_wizard(self, **kwargs):
        #self.debug_FTZO()
        wizard = Fine_Tune_ZOffset(name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination'], state=self.state)
        
    def bed_calibration(self, **kwargs):
        wizard = Bed_Calibration(kwargs['name'], kwargs['title'], kwargs['back_destination'])
        
    def pid_tune(self, **kwargs):
        wizard = PID_Overseer(kwargs['name'], kwargs['title'], kwargs['back_destination'])
                

########################################### Debug Code #####################################################
    def debug_FTZO(self):
        # Check the debug state. If true, print out a list of instances of
        # Fine_Tune_ZOffset recognized by the garbage collector
        import gc
        from WaldoLCD.lcd.wizards.FTZO.fine_tune_zoffset import Fine_Tune_ZOffset
        from WaldoLCD.lcd.wizards.FTZO.FTZO_workflow import FTZO_workflow
        from WaldoLCD.lcd.wizards.FTZO.FTZO_screens import Update_Offset, Picture_Instructions, FTZO_Button, FTZO_Options, Z_offset_saver 

        
        Logger.info("---> Checking Fine_Tune_ZOffset instances")
        obj_len = 0
        for obj in gc.get_objects():
            if isinstance(obj, Fine_Tune_ZOffset):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, FTZO_workflow):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, Update_Offset):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, Picture_Instructions):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, FTZO_Button):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, FTZO_Options):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
            elif isinstance(obj, Z_offset_saver ):
                obj_len += 1
                Logger.info("GC: " + str(obj))
                continue
        Logger.info("There are " + str(obj_len) + " FilamentWizard Objects active")

        # Print out the instance of this class. The name of the instance and
        # address in memory will be printed.
        Logger.info("SELF: " + str(self))
