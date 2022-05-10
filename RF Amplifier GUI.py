

# Pysimple Gui Test #

from faulthandler import disable
from pydoc import visiblename
import PySimpleGUI as sg
import math
import string
import operator

key_list1 = 'power'
key_list2 = 'freq'

newinstrument = True
data = [[" "]]
"""
def instr_add(value1, value2):
    values[]
    data.append()
"""

# Define the window's contents
def make_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['E&xit']],
                ['&Help', ['&About']] ]

      
    headings = ['Freq', 'Voltage', 'Current']
    headings1 = ['Instrument Name', 'VISA Address']
    right_click_menu_def = [[], ['Info', 'Versions', '1', 'Nothing']]

    # layout for setup tab
    setup_layout = [
                    [sg.Text('What is your project name?')],
                    [sg.Input(size=(20,4), key='_INPUT_')],
                    [sg.Text(size=(80,1), key='_OUTPUT_')],
                    [sg.Text('Please enter your instrument Name & VISA address:')], 
                    [sg.Input(size=(20,4), key='_INPUT1_'), sg.Input(size=(20,4), key='_INPUT2_'), sg.Button('Add', key='_ADD_')],
                    [sg.Table(size=(80,1), values=data, headings=headings1, max_col_width=25, text_color='black', background_color='White', auto_size_columns=True, 
                        display_row_numbers=True, justification='right', num_rows=3, key='_TABLE_', row_height=25)],
                    [sg.Radio('Power Sweep', 'Sweep', default=True, enable_events=True, size=(20,1), key='_R1_'), 
                    sg.Radio('Frequency Sweep', 'Sweep', default=True, enable_events=True, size=(20,1), key='_R2_')],
                    [sg.Button('Ok'), sg.Button('Quit')]]
    
    power_sweep_layout = [
                    [sg.Text('Power Sweep Setup')],
                    [sg.Text('Select DC Supply (Sweep)'), sg.OptionMenu(values=('Option 1', 'Option 2', 'Option 3'),  k='_DCP1_')],
                    [sg.Input(size=(10,3), key='_DCP1_')],
                    [sg.Text('Select RF Supply 1')],
                    [sg.Text('Select DC Supply 2')],
                    [sg.Text('Select DC Supply 3')],
                    [sg.Button('Ok', key='_OKP_')]]

    freq_sweep_layout = [
                    [sg.Text('Frequency Sweep Setup')],
                    [sg.Text('Select RF Supply (Sweep)'), sg.OptionMenu(values=('Option 1', 'Option 2', 'Option 3'),  k='_RFF1_')],
                    [sg.Text('Start Freq/(Hz)'), sg.Input(size=(10,3), key='_RFF1START_'),
                        sg.Text('Stop Freq/(Hz)'), sg.Input(size=(10,3), key='_RFF1STOP_'),
                        sg.Text('Stepsize/(Hz)'), sg.Input(size=(10,3), key='_RFF1STEP_')],
                    [sg.Text('Select DC Supply 1')],
                    [sg.Text('Select DC Supply 2')],
                    [sg.Text('Select DC Supply 3')],
                    [sg.Button('Ok', key='_OKF_')]]

    logging_layout = [
                    
                    [sg.Text('Anything printed will display here!')],
                    [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True, expand_y=True, write_only=True,
                                reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True, auto_refresh=True)]]
    
    layout = [[sg.MenubarCustom(menu_def, key='_MENU_', font='Courier 15', tearoff=True)],
                [sg.Text('Demo Of GUI', size=(38, 1), justification='center', font=('Helvetica', 16), relief=sg.RELIEF_RIDGE, k='_TEXT HEADING_', enable_events=True)]]
    
    # defining tabs
    layout +=[[sg.TabGroup([[  
                               sg.Tab('Intrument Setup', setup_layout),
                               sg.Tab('Power Sweep', power_sweep_layout, visible=False, key='_power_'),
                               sg.Tab('Frequency Sweep', freq_sweep_layout, key='_freq_'),
                               sg.Tab('Output', logging_layout)]], expand_x=True, expand_y=True),
                
                ]]
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('Instrument GUI', layout, right_click_menu=right_click_menu_def, right_click_menu_tearoff=True,
                       grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True,
                       scaling=2.0, 
                       )
    window.set_min_size(window.size)
    return window

def main():
    window = make_window(sg.theme())
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read(timeout=100)
        # See if user wants to quit or window was closed
        if event is None:
            break
        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        # Output a message to the window
        # General events
        window['_OUTPUT_'].update('A folder labeled ' + values['_INPUT_'] + ' will be created!')
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key=value) --------')
            for key in values:
                print(key, ' = ',values[key])
        if event in (None, 'Exit'):
            print('[LOG] Clicked Exit!')
            break
        elif event == 'About':
            print('[LOG] Clicked About!')
            sg.popup('Intrument VISA & GUI Demo',
                     'Right click anywhere to see right click menu',
                     'Visit each of the tabs to see available elements',
                     'Output of event and values can be see in Output tab',
                     'The event and values dictionary is printed after every event', keep_on_top=True)
        elif event == 'Edit Me':
            sg.execute_editor(__file__)
        elif event == 'Versions':
            sg.popup(sg.get_versions(), keep_on_top=True)
        # Functional events
        elif event == '_ADD_':                                          # Add an instrument
            global newinstrument
            if newinstrument == True:
                data = [[values['_INPUT1_'], values['_INPUT2_']]]
                newinstrument = False
                window['_TABLE_'].update(values=data)
            else:
                newdata = [values['_INPUT1_'], values['_INPUT2_']]
                data.append(newdata)
                window['_TABLE_'].update(values=data)
        elif event == '_CLEAR_':                                         # clear instruments list (to do)
            break
        elif event == '_RFon_':
            window['_INPUTDC1_'].update(visible=False)

        elif event == '_R1_':                                           # Power tab enable
            window['_power_'].update(visible=True)
            window['_freq_'].update(visible=False)
        elif event == '_R2_':                                           # Freq tab enable
            window['_freq_'].update(visible=True)
            window['_power_'].update(visible=False)
        
            

    window.close()
    exit(0)


if __name__ == '__main__':
    sg.theme('DarkBlue4')
    main()
