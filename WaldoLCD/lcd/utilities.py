from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanelHeader
from scrollbox import Scroll_Box_Even, Scroll_Box_Icons, Waldo_Icons
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from .. import waldoprinter
from netconnectd import NetconnectdClient
from kivy.logger import Logger
from kivy.clock import Clock
from session_saver import session_saver

#Buttons

class Waldo_Controls(Button):
    pass
class Wizards(Button):
    pass
class Network(Button):
    pass
class Updates(Button):
    pass
class Factory_Reset(Button):
    pass

class UtilitiesTab(TabbedPanelHeader):
    """
    Represents the Utilities tab header and dynamic content
    """
    pass


class UtilitiesContent(BoxLayout):
    def __init__(self, **kwargs):
        super(UtilitiesContent, self).__init__()

        #add Icons
        self.wiz = Waldo_Icons('Icons/White_Utilities/Wizards.png', waldoprinter.lang.pack['WaldoIcons']['Wizards'] , 'WIZARDS')
        self.rc = Waldo_Icons('Icons/White_Utilities/Print tuning_White.png', waldoprinter.lang.pack['WaldoIcons']['Print_Tuning'], 'PRINT_TUNING')
        self.net = Waldo_Icons('Icons/White_Utilities/Networking.png', waldoprinter.lang.pack['WaldoIcons']['Network'], 'NETWORK')
        self.upd = Waldo_Icons('Icons/White_Utilities/Updates.png', waldoprinter.lang.pack['WaldoIcons']['Update'], 'UPDATES')
        self.sys = Waldo_Icons('Icons/System_Icons/Shutdown 2.png', waldoprinter.lang.pack['WaldoIcons']['System'], 'SYSTEM')
        self.opt = Waldo_Icons('Icons/White_Utilities/Options.png', waldoprinter.lang.pack['WaldoIcons']['Options'], 'OPTIONS')
        icons = [self.rc, self.wiz, self.net, self.upd, self.opt, self.sys]
        layout = Scroll_Box_Icons(icons)
        self.clear_widgets()
        self.add_widget(layout)

        self.state = 'NOT_PRINTING'
        self.last_state = None
        Clock.schedule_interval(self.monitor_layout, 1)

    def monitor_layout(self, dt):
        if waldoprinter.printer_instance._printer.is_printing() != True:
            self.state = 'NOT_PRINTING'
            self.rc.icon_name = waldoprinter.lang.pack['WaldoIcons']['Fan_Control']
            self.rc.img_source = 'Icons/White_Utilities/Fans.png'
            self.rc.generator = "FAN_CONTROL"
        elif waldoprinter.printer_instance._printer.is_printing():
            self.state = 'PRINTING'
            self.rc.icon_name = waldoprinter.lang.pack['WaldoIcons']['Print_Tuning']
            self.rc.img_source = 'Icons/White_Utilities/Print tuning_White.png'
            self.rc.generator = 'PRINT_TUNING'


        #monitor for errors
        if 'current_error' in session_saver.saved:
            error = session_saver.saved['current_error']

            if error == 'MAINBOARD' or error == 'BED_DISCONNECT':
                self.wiz.button_state = True
                self.rc.button_state = True
                self.opt.button_state = True
            #if the firmware is being updated dont allow the user to update the printer, since it also includes a firmware update(Sometimes)
            elif error == 'FIRMWARE':
                self.wiz.button_state = True
                self.rc.button_state = True
                self.upd.button_state = True
                self.opt.button_state = True
                self.sys.button_state = True
            elif self.state == 'NOT_PRINTING':
                self.wiz.button_state = False
                self.rc.button_state = False
                self.upd.button_state = False
                self.opt.button_state = False
                self.sys.button_state = False
            else:
                self.wiz.button_state = True






class QRCodeScreen(BoxLayout):
    img_source = waldoprinter.printer_instance.get_plugin_data_folder() + '/qr_code.png'
