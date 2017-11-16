# coding: UTF-8
from .. import waldoprinter
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.clock import Clock

class Temperature_Label(Button):
    extruder_one_temp = NumericProperty(0)

    def __init__(self, waldosm=None, **kwargs):
        self.sm = waldosm
        Clock.schedule_interval(self.update, 1/30)

    def update(self, dt):
        temps = waldoprinter.printer_instance._printer.get_current_temperatures()
        current_data = waldoprinter.printer_instance._printer.get_current_data()
        if 'tool0' in temps.keys():
            self.extruder_one_temp = temps['tool0']['actual']
            self.extruder_one_max_temp = temps['tool0']['target']
        else:
            self.extruder_one_temp = 0
            self.extruder_one_max_temp = 0


        if self.sm.current != 'extruder_control_screen':
            return False
