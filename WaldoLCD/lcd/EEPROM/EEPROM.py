# -*- coding: utf-8 -*-
# @Author: Matt Pedler
# @Date:   2017-10-19 13:34:53
# @Last Modified by:   BH
# @Last Modified time: 2018-10-15 15:08:44
# coding=utf-8

#Kivy
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

#WaldoLCD
from WaldoLCD.lcd.scrollbox import Scroll_Box_Even_Button, Scroll_Box_Even
from WaldoLCD.lcd.session_saver import session_saver
from WaldoLCD.lcd.pconsole import pconsole
from WaldoLCD import waldoprinter
from WaldoLCD.lcd.connection_popup import Status_Popup
from WaldoLCD.lcd.common_screens import Modal_Question_No_Title, Button_Screen
from WaldoLCD.lcd.wizards.wizard_bb import Wizard_BB, Screen_Node
from WaldoLCD.lcd.file_system.file_screen import Scroll_Box_File_List
from WaldoLCD.lcd.EEPROM.EEPROM_screens import Scroll_Box_EEPROM_List, Change_Value


class EEPROM(object):
    #self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
    def __init__(self, *args, **kwargs):
        self.buttons = []
        self.name = kwargs['name']
        self.title = kwargs['title']
        self.back_destination = kwargs['back_destination']

        #set up the wizard screen
        self.bb = Wizard_BB()
        self.group = 'EEPROM_Group'
       
        #add bb
        waldoprinter.waldosm.add_widget(self.bb)
        waldoprinter.waldosm.current = self.bb.name


        model = waldoprinter.printer_instance._settings.get(['Model'])
        self.refresh_eeprom()

        if model == "Robo R2":
            #add bed PID for the R2
            self.button_order = [
                                 waldoprinter.lang.pack['EEPROM']['Home_Offset'],
                                 waldoprinter.lang.pack['EEPROM']['Probe_Offset'] , 
                                 waldoprinter.lang.pack['EEPROM']['Steps_Unit'], 
                                 waldoprinter.lang.pack['EEPROM']['Accelerations'], 
                                 waldoprinter.lang.pack['EEPROM']['Max_Accelerations'],  
                                 waldoprinter.lang.pack['EEPROM']['Filament_Settings'], 
                                 waldoprinter.lang.pack['EEPROM']['Feed_Rates'], 
                                 waldoprinter.lang.pack['EEPROM']['PID_Settings'],
                                 waldoprinter.lang.pack['EEPROM']['Bed_PID'], 
                                 waldoprinter.lang.pack['EEPROM']['Advanced'],
                                 waldoprinter.lang.pack['EEPROM']['Linear_Advanced'],
                                 waldoprinter.lang.pack['EEPROM']['Reset']
                                 ]
        else:
            self.button_order = [
                                 waldoprinter.lang.pack['EEPROM']['Home_Offset'],
                                 waldoprinter.lang.pack['EEPROM']['Probe_Offset'] , 
                                 waldoprinter.lang.pack['EEPROM']['Steps_Unit'], 
                                 waldoprinter.lang.pack['EEPROM']['Accelerations'], 
                                 waldoprinter.lang.pack['EEPROM']['Max_Accelerations'],  
                                 waldoprinter.lang.pack['EEPROM']['Filament_Settings'], 
                                 waldoprinter.lang.pack['EEPROM']['Feed_Rates'], 
                                 waldoprinter.lang.pack['EEPROM']['PID_Settings'],
                                 waldoprinter.lang.pack['EEPROM']['Advanced'],
                                 waldoprinter.lang.pack['EEPROM']['Linear_Advanced'],
                                 waldoprinter.lang.pack['EEPROM']['Reset']
                                 ]   
        self.load_eeprom()     

    def load_eeprom(self):
        eeprom_list = []
        for entry in self.button_order:
            if entry in self.eeprom_dictionary and self.eeprom_dictionary[entry]['values'] != {}:
                eeprom_list.append(self.eeprom_dictionary[entry])

        #make node
        self.EEPROM_Node = EEPROM_Node(data=eeprom_list, title=self.title)

        #render screen with list
        self.EEPROM_screen = Scroll_Box_EEPROM_List(self.EEPROM_Node.data, self.open_setting)

        self.bb.make_screen(self.EEPROM_screen,
                            title = self.title,
                            back_function = self.previous_list,
                            option_function = 'no_option'
                                )
    
    def refresh_eeprom(self):
        pconsole.query_eeprom()

        '''
        This dictionary contains a few defining elements for each EEPROM entry that we want to display
        name: This is the name that will be displayed on the screen for this value
        command: This is the specific gcode command that this entry is attached to
        filter: This defines what values will be shown to the user
        order: This defines the order that the values will be shown to the user
        range: This will define the numbers by which the user will be able to edit the entry
        values: This will hold the actual values scraped from the EEPROM
        '''
        self.eeprom_dictionary = {
            
            waldoprinter.lang.pack['EEPROM']['Home_Offset'] : {'name': waldoprinter.lang.pack['EEPROM']['Home_Offset'],
                                                              'command': 'M206',
                                                              'order': ['Z'],
                                                              'range': [10, 0.01, 0.1, 1],
                                                              'values': pconsole.home_offset
                                                             },

            waldoprinter.lang.pack['EEPROM']['Probe_Offset'] : {'name': waldoprinter.lang.pack['EEPROM']['Probe_Offset'],
                                                               'command': 'M851',
                                                               'order': ['Z'],
                                                               'range': [10, 0.01, 0.1, 1],
                                                               'values': pconsole.probe_offset
                                                              },

            waldoprinter.lang.pack['EEPROM']['Feed_Rates']: {'name': waldoprinter.lang.pack['EEPROM']['Feed_Rates'],
                                                            'command': 'M203',
                                                            'order': ['X', 'Y', 'Z', 'E', 'T0 E', 'T1 E'],
                                                            'range': [0.01, 0.1, 1, 10],
                                                            'values': pconsole.feed_rate
                                                           },

            waldoprinter.lang.pack['EEPROM']['PID_Settings'] : { 'name': waldoprinter.lang.pack['EEPROM']['PID_Settings'],
                                                                'command': 'M301',
                                                                'order' : ['P', 'I', 'D'],
                                                                'range' : [0.01, 0.1, 1, 10],
                                                                'values': pconsole.PID
                                                              },

            waldoprinter.lang.pack['EEPROM']['Bed_PID']: { 'name': waldoprinter.lang.pack['EEPROM']['Bed_PID'],
                                                          'command': 'M304',
                                                          'order' : ['P', 'I', 'D'],
                                                          'range' : [0.01, 0.1, 1, 10],
                                                          'values': pconsole.BPID
                                                        },

            waldoprinter.lang.pack['EEPROM']['Steps_Unit'] : { 'name': waldoprinter.lang.pack['EEPROM']['Steps_Unit'],
                                                              'command': 'M92',
                                                              'order': ['X', 'Y', 'Z', 'E', 'T0 E', 'T1 E'],
                                                              'range': [0.01, 0.1, 1, 10],
                                                              'values': pconsole.steps_per_unit
                                                            },

            waldoprinter.lang.pack['EEPROM']['Accelerations'] : { 'name': waldoprinter.lang.pack['EEPROM']['Accelerations'],
                                                                 'command': 'M204',
                                                                 'order': ['P', 'R', 'T'],
                                                                 'range': [0.01, 0.1, 1, 10, 100, 1000],
                                                                 'values': pconsole.accelerations
                                                               },

            waldoprinter.lang.pack['EEPROM']['Max_Accelerations'] : { 'name': waldoprinter.lang.pack['EEPROM']['Max_Accelerations'],
                                                                     'command': 'M201',
                                                                     'order': ['X', 'Y', 'Z', 'E', 'T0 E', 'T1 E'],
                                                                     'range': [0.01, 0.1, 1, 10, 100, 1000],
                                                                     'values': pconsole.max_accelerations
                                                                    },

            waldoprinter.lang.pack['EEPROM']['Advanced']: { 'name': waldoprinter.lang.pack['EEPROM']['Advanced'],
                                                           'command': 'M205',
                                                           'order': ['S', 'T', 'X', 'Y', 'Z', 'E'],
                                                           'range': [0.01, 0.1, 1, 10, 100],
                                                           'values': pconsole.advanced_variables
                                                         },
            waldoprinter.lang.pack['EEPROM']['Linear_Advanced']: { 'name': waldoprinter.lang.pack['EEPROM']['Linear_Advanced'],
                                                                  'command': 'M900',
                                                                  'order': ['K','R'],
                                                                  'range': [0.01, 0.1, 1, 10, 100],
                                                                  'values': pconsole.linear_advanced
                                                         },
            waldoprinter.lang.pack['EEPROM']['Reset']: { 'name': waldoprinter.lang.pack['EEPROM']['Reset'],
                                                        'action': self.reset_defaults,
                                                        'values': ''

                                                      },

        }

    #this function will query the eeprom when the user backs out or applys a change to the eeprom
    def refresh_list(self, *args, **kwargs):
        pconsole.query_eeprom()
        self.EEPROM_screen.repopulate_for_new_screen()
        Clock.schedule_once(self.update_title, 0.0)
        
    #this function updates the title when backing out of the change value screen
    def update_title(self, *args, **kwargs):
        self.bb.update_title(self.EEPROM_Node.title)

    def open_eeprom_value(self, setting_data):
        pconsole.dict_logger(setting_data)
        change_value_screen = Change_Value(setting_data, self.bb.back_function)
        change_value_screen.change_screen_event = self.refresh_list

        self.bb.make_screen(change_value_screen,
                            title = "Change Value",
                            option_function='no_option')

    def reset_defaults(self):

        #get the current screen
        back_screen = waldoprinter.waldosm.current

        def reset():
            waldoprinter.printer_instance._printer.commands("M502")
            waldoprinter.printer_instance._printer.commands("M500")
            waldoprinter.printer_instance._printer.commands("M501")

            #make screen to say that the variables have been reset

            #body_text, button_function, button_text = waldoprinter.lang.pack['Button_Screen']['Default_Button']
            content = Button_Screen(waldoprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Body_Text'],
                                    waldoprinter.waldosm.go_back_to_main,
                                    button_text = waldoprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Button'])

            #make screen
            waldoprinter.waldosm._generate_backbutton_screen(name='ack_reset_eeprom', 
                                                           title = waldoprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Title'] , 
                                                           back_destination=back_screen, 
                                                           content=content)

        def cancel():
            waldoprinter.waldosm.current = back_screen

        #make the confirmation screen
        #body_text, option1_text, option2_text, option1_function, option2_function
        content = Modal_Question_No_Title(waldoprinter.lang.pack['EEPROM']['Reset_Confirmation']['Body_Text'],
                                          waldoprinter.lang.pack['EEPROM']['Reset_Confirmation']['positive'],
                                          waldoprinter.lang.pack['EEPROM']['Reset_Confirmation']['negative'],
                                          reset,
                                          cancel) 

        #make screen
        waldoprinter.waldosm._generate_backbutton_screen(name='reset_eeprom', 
                                                       title = waldoprinter.lang.pack['EEPROM']['Reset_Confirmation']['Title'] , 
                                                       back_destination=back_screen, 
                                                       content=content)

    def open_setting(self, setting_data):
        if 'order' in setting_data and 'values' in setting_data:
            #order acts like a filter for what we want the user to see.
            filtered_data = []
            for setting in setting_data['order']:
                if setting in setting_data['values']:
                    data = {
                            'name': setting + ": ",
                            'setting': setting,
                            'data': setting_data
                    }
                    filtered_data.append(data)
                else:
                    Logger.info(str(setting) + " is not in the values list.")
        elif 'action' in setting_data:
            setting_data['action']()
            return #exit this function
        else:
            Logger.info("No Values or Order!")
            pconsole.dict_logger(setting_data)

        #update Node
        self.EEPROM_Node = EEPROM_Node(data=filtered_data, title = setting_data['name'], prev_data=self.EEPROM_Node)

        #update EEPROM list
        self.EEPROM_screen.eeprom_list = self.EEPROM_Node.data
        self.EEPROM_screen.repopulate_for_new_screen()

        #update callback
        self.EEPROM_screen.update_callback(self.open_eeprom_value)

        #update title
        self.bb.update_title(setting_data['name'])

    def previous_list(self):
        Logger.info("Previous list hit")
        if self.EEPROM_Node.return_previous() != None:
            #return the node to the previous node
            self.EEPROM_Node = self.EEPROM_Node.return_previous()

            #refresh the list 
            self.EEPROM_screen.eeprom_list = self.EEPROM_Node.data
            self.EEPROM_screen.repopulate_for_new_screen()
    
            #update callback
            self.EEPROM_screen.update_callback(self.open_setting)
            #update title
            self.bb.update_title(self.EEPROM_Node.title) #restore the title associated with the list
        else:
            #If there is no where left to go then go back to the previous screen in the wizard bb node list
            self.bb.update_back_function(self.bb.back_function_flow)
            self.bb.back_function_flow()


#Linked list to keep track of the EEPROM list
class EEPROM_Node(object):
    data=None
    def __init__(self, data=None, title=None, prev_data=None):
        super(EEPROM_Node, self).__init__()
        self.data = data
        self.title = title
        self.prev_data = prev_data

    def return_previous(self):
        return self.prev_data





