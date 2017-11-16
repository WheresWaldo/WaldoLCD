from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import RoundedRectangle
from kivy.clock import Clock
from kivy.logger import Logger
from pconsole import pconsole
from .. import waldoprinter
from multiprocessing import Process

DEFAULT_FONT = 'Roboto'


class MainScreen(Screen):
    """
    Represents the the main screen template with 3 tab buttons on the top bar: Files, Printer, and Settings

    Is in charge of orchestrating content update for all 3 tabs
    """
    lang = waldoprinter.lang

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)        


    def query_eeprom(self):
        if not waldoprinter.printer_instance._printer.is_printing():

            pconsole.query_eeprom()  

    def update_file_sizes(self):
        self.ids.files_content.update_file_sizes()      

    
    def open_tab(self, tab_id):
        t = self.ids[tab_id]
        #Logger.info('Tab: {}'.format(t))
        self.ids.mstp.switch_to(t)


    def update_tab(self,tab):
        waldoprinter.open_tab = tab

class MainScreenTabbedPanel(TabbedPanel):
    """
    Represents the tabbed panels. Handles toggling between FilesTab, PrinterStatusTab and SettingsTab
    """

    def __init__(self, **kwargs):
        super(MainScreenTabbedPanel, self).__init__(**kwargs)







