# -*- coding: utf-8 -*-
# @Author: Matt Pedler
# @Date:   2017-10-20 14:35:15
# @Last Modified by:   BH
# @Last Modified time: 2018-10-15 11:35:54

#kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.clock import Clock

#WaldoLCD
from WaldoLCD import waldoprinter
from WaldoLCD.lcd.printer_jog import printer_jog
from WaldoLCD.lcd.common_screens import Button_Screen, Picture_Button_Screen
from WaldoLCD.lcd.pconsole import pconsole
from WaldoLCD.lcd.connection_popup import Error_Popup, Warning_Popup
from WaldoLCD.lcd.wizards.preheat_wizard.preheat_overseer import Preheat_Overseer
from WaldoLCD.lcd.wizards.wizard_bb import Wizard_BB, Screen_Node
from WaldoLCD.lcd.common_screens import Image_on_Button_Screen, Picture_Image_on_Button_Screen, Temperature_Wait_Screen, Title_Picture_Image_on_Button_Screen, Extruder_Selector
from WaldoLCD.lcd.wizards.FTZO.FTZO_workflow import FTZO_workflow
from WaldoLCD.lcd.wizards.FTZO.FTZO_screens import Picture_Instructions, Z_offset_saver

#python
from functools import partial
import time
import gc

class Fine_Tune_ZOffset(object):
    """docstring for Fine_Tune_ZOffset"""
    def __init__(self, name, title, back_destination, state):
        super(Fine_Tune_ZOffset, self).__init__()
        self.bb = Wizard_BB()
        self.group = 'FTZO_group'
        self.welcome = None
        self.workflow = None
        self.ph_overseer = None
        self.zo_saver = None
        self.debug_mode = False

        self.name = name #name of initial screen
        self.title = title
        self.back_destination = back_destination
        self.bb.back_destination = self.back_destination
        self.dual = False
        self.state = state
        self.selected_tool = 'tool0'

        #add bb
        waldoprinter.waldosm.add_widget(self.bb)
        waldoprinter.waldosm.current = self.bb.name
        self.welcome_screen() #start the wizard

        #variable that does not get a soft restart
        self.preparing_in_progress = False

    #Cleanup the wizard by dereferrencing everything in the wizard
    def cleanup(self):
        Logger.info("Deleting: FTZO")   
        #Cleanup the wizard and remove all summoned objects from memory

        #remove BB from screen manager object
        waldoprinter.waldosm.remove_widget(self.bb)

        #ask BB to delete all of it's nodes
        self.bb.delete_node()

        #dereference BB
        self.bb =''

        #ask the welcome screen to kill itself
        if self.welcome != None:
            self.welcome.cleanup()

        #Ask the main workflow to clean itself up
        if self.workflow != None:
            self.workflow.cleanup()

        #Ask Preheat to clean itself up
        if self.ph_overseer != None:
            self.ph_overseer.cleanup()

        #ask the Z-Offset saver to clean itself up
        if self.zo_saver != None:
            self.zo_saver.cleanup()

        #dereference self    
        del_list = []
        for self_var in self.__dict__:
            del_list.append(self_var)
            self.__dict__[self_var] = '' #set variables to nothing.
        for self_var in del_list:
            #Logger.info("Deleting " + str(self_var))
            del self.__dict__[self_var]

        #Tell Self to print out any remaining referrers 
        # Logger.info("---> Printing referrers of FTZO")
        # gc.collect()
        # for referer in gc.get_referrers(self):
        #     Logger.info(referer)
        # Logger.info("---> Done printing referrers of FTZO")

        #delete self.
        del self


    def welcome_screen(self):
        self.welcome = Button_Screen(waldoprinter.lang.pack['FT_ZOffset_Wizard']['Welcome']['Body'],
                               self.process_machine_state,
                               button_text=waldoprinter.lang.pack['FT_ZOffset_Wizard']['Welcome']['Button_Text'])
        title = waldoprinter.lang.pack['FT_ZOffset_Wizard']['Welcome']['Title']
        self.welcome.change_screen_actions = self.cleanup

        self.bb.make_screen(self.welcome,
                            title,
                            option_function='no_option')


    def process_machine_state(self):
        ext_number = 1
        if 'extruder' in self.state:
            ext_number = int(self.state['extruder'])

        #decide what the layout should be
        if ext_number > 1:
            self.select_extruder()
        else:
            self.choose_material()

    def select_extruder(self):
        #detirmine machine state and behaviour of the wizard
        es = Extruder_Selector(self.dual_or_single_fork, make_screen=self.bb.make_screen, group=self.group)
        es.show_screen()

    def dual_or_single_fork(self, extruder):
        extruders = ['EXT1', 'EXT2', 'BOTH']

        if extruder in extruders:
            if extruder == 'BOTH':
                self.dual = True
            else:
                self.dual = False
                tool_dict = {
                    'EXT1': 'tool0',
                    'EXT2': 'tool1'
                }
                self.selected_tool = tool_dict[extruder]
            self.choose_material()
        else:
            Logger.info("ERROR Invalid selection")
            raise ValueError(str(extruder) + " Is not a valid selection")

    def choose_material(self, *args):
        Logger.info("Making Preheat_Overseer with group: " + str(self.group))
        self.ph_overseer = Preheat_Overseer(end_point=self.collect_heat_settings,
                         name='preheat_wizard',
                         title=waldoprinter.lang.pack['Utilities']['Preheat'],
                         back_destination=self.bb.name,
                         dual = self.dual,
                         back_button_screen = self.bb,
                         group = self.group)

    def collect_heat_settings(self, extruder, bed):
        #save the collected heat settings
        self.extruder = extruder
        self.bed = bed
        self.instruction1()

    def instruction1(self):
        layout = Button_Screen(waldoprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Body'],
                               self.instruction2)
        title = waldoprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Title']

        self.bb.make_screen(layout,
                            title,
                            option_function='no_option'
                            )


    def instruction2(self):
        layout = Picture_Instructions()
        title = waldoprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Title']

        self.bb.make_screen(layout,
                            title,
                            option_function=self.start_workflow,
                            option_icon="Icons/Slicer wizard icons/next.png"
                            )

    def start_workflow(self):
        if type(self.extruder) != list:
            temps = {
                'tool0': self.extruder,
                'bed': self.bed
            }
        else:
            temps = {
                'tool0': self.extruder[0],
                'tool1': self.extruder[1],
                'bed': self.bed
            }
        self.workflow = FTZO_workflow(self.dual, self.selected_tool, temps, self.finish_wizard, self.bb, debug=self.debug_mode)

    def finish_wizard(self):
        waldoprinter.printer_instance._printer.commands('M500')
        offset = pconsole.home_offset['Z']
        self.zo_saver = Z_offset_saver(self.goto_main,
                                [waldoprinter.lang.pack['FT_ZOffset_Wizard']['Save_Offset']['Saving'], waldoprinter.lang.pack['FT_ZOffset_Wizard']['Finish']['Sub_Title'] ]
                                )
        title = waldoprinter.lang.pack['FT_ZOffset_Wizard']['Finish']['Title']

        self.bb.make_screen(self.zo_saver,
                            title,
                            option_function = 'no_option')

    def goto_main(self):
        waldoprinter.printer_instance._printer.commands('M104 S0')
        waldoprinter.printer_instance._printer.commands('M140 S0')
        waldoprinter.printer_instance._printer.commands('G28')
        waldoprinter.waldosm.go_back_to_main('utilities_tab')
        #cleanup self
        self.cleanup()
        
