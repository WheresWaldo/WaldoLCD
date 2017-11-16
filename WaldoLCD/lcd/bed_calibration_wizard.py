from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import waldoprinter
from printer_jog import printer_jog
from kivy.clock import Clock
from pconsole import pconsole
from connection_popup import Error_Popup, Warning_Popup
import functools
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from common_screens import Button_Group_Observer, OL_Button, Quad_Icon_Layout, Button_Screen, Picture_Button_Screen, Modal_Question, Wait_Screen, Point_Layout

class Bed_Calibration(object):
    """Bed_Calibration Allows the user to move the head to three different points to manually level the bed through the 
       Screws on the bed"""
    def __init__(self):
        super(Bed_Calibration, self).__init__()
        pconsole.query_eeprom()
        self.model = waldoprinter.printer_instance._settings.get(['Model'])
        self.welcome_screen()
        self.mode = "manual"

    def welcome_screen(self):
        layout = Button_Screen(waldoprinter.lang.pack['Bed_Cal_Wizard']['Welcome']['Body'], 
                               self.tighten_all_screw_instructions,
                               button_text = waldoprinter.lang.pack['Bed_Cal_Wizard']['Welcome']['Button'])
        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Welcome']['Title']
        name = 'welcome_bed_calibration'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )
    def tighten_all_screw_instructions(self):
        layout = Button_Screen(waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Body'], 
                               self.check_for_valid_start,
                               button_text = waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Button'])
        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Title']
        name = 'tilt1'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def check_for_valid_start(self):
        start = self.check_offset()

        #if the ZOffset is not right don't allow the user to continue
        if start:
            self.ask_for_mode()
        else:
            zoff = pconsole.home_offset['Z']
            ep = Error_Popup(waldoprinter.lang.pack['Warning']['Z_Offset_Warning']['Title'], waldoprinter.lang.pack['Warning']['Z_Offset_Warning']['Body1'] + " " +  str(zoff) + " " + waldoprinter.lang.pack['Warning']['Z_Offset_Warning']['Body2'],callback=partial(waldoprinter.waldosm.go_back_to_main, tab='printer_status_tab'))
            ep.open()

    def ask_for_mode(self):

        def manual():
            self.mode = "manual"
            self.prepare_printer()
        def guided():
            self.mode = "guided"
            self.prepare_printer()

        layout = Modal_Question(waldoprinter.lang.pack['Bed_Cal_Wizard']['Mode']['Sub_Title'], 
                       waldoprinter.lang.pack['Bed_Cal_Wizard']['Mode']['Body'],
                       waldoprinter.lang.pack['Bed_Cal_Wizard']['Mode']['Button1'],
                       waldoprinter.lang.pack['Bed_Cal_Wizard']['Mode']['Button2'],
                       manual,
                       guided)

        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Mode']['Title']
        name = 'guided_or_manual'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )



    
    #check the offset to see if it is in an acceptable range
    def check_offset(self):

        offset = float(pconsole.home_offset['Z'])
        #make sure the range is within -20 - 0
        if offset > -20.00 and not offset > 0.00 and offset != 0.00:
            return True
        else:
            return False

    def prepare_printer(self):
        #kill heaters
        waldoprinter.printer_instance._printer.commands('M104 S0')
        waldoprinter.printer_instance._printer.commands('M140 S0')
        waldoprinter.printer_instance._printer.commands('M106 S255')

        waldoprinter.printer_instance._printer.commands('G28') #Home Printer
        waldoprinter.printer_instance._printer.commands('G1 X5 Y10 F5000') # go to first corner
        waldoprinter.printer_instance._printer.commands('G1 Z5')

        fork_mode = self.open_3_point_screen
        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Prepare']['Title1']
        if self.mode == "guided":
            fork_mode = self.guided_instructions
            title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Prepare']['Title2']
            

        layout = Wait_Screen(fork_mode,
                             waldoprinter.lang.pack['Bed_Cal_Wizard']['Prepare']['Sub_Title'],
                             waldoprinter.lang.pack['Bed_Cal_Wizard']['Prepare']['Body'])
        name = "wait_screen"
        back_destination = waldoprinter.waldo_screen()


        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def guided_instructions(self):
        #turn off fans
        waldoprinter.printer_instance._printer.commands('M106 S0')
        point_string = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Error']
        screw = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Error']
        point_icon = "Icons/Bed_Calibration/Bed placement left.png"
        body = (waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Body1'] + screw + waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Body2'])
        self.counter = 1
        self.done = False
        def point_1():
            point_string = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['L_Point']
            screw = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['LF_Screw']
            point_icon = "Icons/Bed_Calibration/Bed placement left.png"
            self.update_body(point_string, screw, point_icon)

            waldoprinter.printer_instance._printer.commands('G1 Z10')
            waldoprinter.printer_instance._printer.commands('G1 X35 Y35 F5000') # go to first corner
            waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_2():
            point_string = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['R_Point']
            screw = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['RF_Screw']
            point_icon = "Icons/Bed_Calibration/Bed placement right.png"
            self.update_body(point_string, screw, point_icon)
            
            waldoprinter.printer_instance._printer.commands('G1 Z10')
            waldoprinter.printer_instance._printer.commands('G1 X160 Y35 F5000') # go to first corner
            waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_3():
            point_string = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['BR_Point']
            screw = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['BR_Screw']
            point_icon = "Icons/Bed_Calibration/Bed placement back right.png"
            self.update_body(point_string, screw, point_icon)
            
            waldoprinter.printer_instance._printer.commands('G1 Z10')
            waldoprinter.printer_instance._printer.commands('G1 X160 Y160 F5000') # go to first corner
            waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_4():
            point_string = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['BL_Point']
            screw = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['BL_Screw']
            point_icon = "Icons/Bed_Calibration/Bed placement back left.png"
            self.update_body(point_string, screw, point_icon)
            
            waldoprinter.printer_instance._printer.commands('G1 Z10')
            waldoprinter.printer_instance._printer.commands('G1 X35 Y160 F5000') # go to first corner
            waldoprinter.printer_instance._printer.commands('G1 Z0')


        def next_point():
            points = [point_1, point_2, point_3, point_4]

            if self.counter == 4 and not self.done:
                self.counter = 0
                self.done = True
            elif self.counter == 4 and self.done:
                self.finish_screws_instructions()
                return

            points[self.counter]()    

            self.counter += 1   

        self.guided_layout = Picture_Button_Screen(point_string, 
                                       body,
                                       point_icon,
                                       next_point,
                                       button_text = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Button_Text'])

        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Title']
        name = 'adjust_screws'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=self.guided_layout
        )

        point_1()

    def update_body(self, point_string, screw, icon):
        body = (waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Body1'] + screw + waldoprinter.lang.pack['Bed_Cal_Wizard']['Guided_Instructions']['Body2'])
        self.guided_layout.body_text = body
        self.guided_layout.title_text = point_string
        self.guided_layout.image_source = icon

    def open_3_point_screen(self):
        #turn off fans
        waldoprinter.printer_instance._printer.commands('M106 S0')
       
        def point_1(state):
            if state:
                waldoprinter.printer_instance._printer.commands('G1 Z10')
                waldoprinter.printer_instance._printer.commands('G1 X35 Y35 F5000') # go to first corner
                waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_2(state):
            if state:
                waldoprinter.printer_instance._printer.commands('G1 Z10')
                waldoprinter.printer_instance._printer.commands('G1 X160 Y35 F5000') # go to first corner
                waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_3(state):
            if state:
                waldoprinter.printer_instance._printer.commands('G1 Z10')
                waldoprinter.printer_instance._printer.commands('G1 X160 Y160 F5000') # go to first corner
                waldoprinter.printer_instance._printer.commands('G1 Z0')

        def point_4(state):
            if state:
                waldoprinter.printer_instance._printer.commands('G1 Z10')
                waldoprinter.printer_instance._printer.commands('G1 X35 Y160 F5000') # go to first corner
                waldoprinter.printer_instance._printer.commands('G1 Z0')

        #make the button observer
        point_observer = Button_Group_Observer()

        #make the buttons
        p1 = OL_Button(waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Left'], 
                       "Icons/Bed_Calibration/Bed placement left.png",
                       point_1,
                       enabled = True,
                       observer_group = point_observer)
        p2 = OL_Button(waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Right'], 
                       "Icons/Bed_Calibration/Bed placement right.png",
                       point_2,
                       enabled = False,
                       observer_group = point_observer)
        p3 = OL_Button(waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Back_Right'], 
                       "Icons/Bed_Calibration/Bed placement back right.png",
                       point_3,
                       enabled = False,
                       observer_group = point_observer)
        p4 = OL_Button(waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Back_Left'], 
                       "Icons/Bed_Calibration/Bed placement back left.png",
                       point_4,
                       enabled = False,
                       observer_group = point_observer)

        bl2 = [p1, p2]
        bl1 = [p4, p3]

        #make screen
        layout = Quad_Icon_Layout(bl1, bl2,  waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Sub_Title'])
        back_destination = waldoprinter.waldo_screen()
        waldoprinter.back_screen(name = 'point_selection', 
                                title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Manual_Instructions']['Title'], 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.finish_screws_instructions,
                                icon = "Icons/Slicer wizard icons/next.png")

    def finish_screws_instructions(self):
        layout = Button_Screen(waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Body'], 
                               self.finish_wizard,
                               button_text = waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Button'])
        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Tilt_Instructions']['Title']
        name = 'tilt2'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def finish_wizard(self):
        
        layout = Picture_Button_Screen(waldoprinter.lang.pack['Bed_Cal_Wizard']['Finish_Wizard']['Sub_Title'], 
                                      waldoprinter.lang.pack['Bed_Cal_Wizard']['Finish_Wizard']['Body'],
                                      'Icons/Manual_Control/check_icon.png',
                                      self.goto_main)
        title = waldoprinter.lang.pack['Bed_Cal_Wizard']['Finish_Wizard']['Title']
        name = 'finish_wizard'
        back_destination = waldoprinter.waldo_screen()

        waldoprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def goto_main(self):
        waldoprinter.printer_instance._printer.commands('G28')
        waldoprinter.waldosm.go_back_to_main('utilities_tab')









    
class Quad_Icon_Layout(BoxLayout):
    body_text = StringProperty("Error")

    def __init__(self, bl1, bl2, body_text, **kwargs):
        super(Quad_Icon_Layout, self).__init__()
        self.body_text =  body_text
        self.bl1 = bl1
        self.bl2 = bl2
        self.alter_layout()

    def alter_layout(self):
        grid = self.ids.button_grid

        grid.clear_widgets()
       
        
        #make a 2x2 grid
        for button in self.bl1:
            grid.add_widget(button)

        for button in self.bl2:
            grid.add_widget(button)

          

