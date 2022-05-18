

# Pysimple Gui Test #

from msilib import Table
from msilib.text import tables
from sqlite3 import connect
import PySimpleGUI as sg
import pyvisa as visa
import os
import math
import string
import operator

key_list1 = 'power'
key_list2 = 'freq'

newinstr = True
instr_data = [["DC Supply 1","GPIB0::2::INSTR"], ["DC Supply 2","GPIB0::3::INSTR"]]
instr_names = ["DC Supply 1","DC Supply 2"]
"""
def instr_add(value1, value2):
    values[]
    data.append()
"""

def instr_open():                  # open and list all instrument names and check whether they are active
    global list
    for i in range(1, len(list)):
        print('--------- Instrument ' + str(i) + ' -----------')
        name = list[i]
        active = [False for x in range(len(list))]
        try:
            resource = rm.open_resource(name)
            instr = resource.query('*IDN?')   
            instr = instr.strip()             
            print(instr)
            address = resource.query('ADDRESS?')
            address = address.strip()
            print('address: ' + address)
            active[i] = True
            print('connected: ' + str(active[i]))

        except Exception as e:
            print(type(e))
            print(name + ' resource not active')
            print('connected: ' + str(active[i]))
    return active

def lib_select(GPIB_address):               # auto selects the library to use
    try:
        resource =  rm.open_resource(GPIB_address)
        instr = resource.query('*IDN?')  
        instr = instr.strip()  
    except Exception as e:
        print(type(e))
        print('device unavailable')
        instr = 'none' 
    if 'CPX400DP' in instr: 
        lib_name = 'CPX400DP power supply'
    elif 'RF' in instr:
        lib_name = 'RF supply'
    else:
        lib_name = 'none'
    print('library select done')
    return lib_name

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
                    [sg.Table(size=(80,1), values=instr_data, headings=headings1, max_col_width=25, text_color='black', background_color='White', auto_size_columns=True, 
                        display_row_numbers=True, justification='right', num_rows=3, key='_TABLE_', row_height=25)],
                    [sg.Radio('Power Sweep', 'Sweep', default=True, enable_events=True, size=(20,1), key='_R1_'), 
                    sg.Radio('Frequency Sweep', 'Sweep', default=True, enable_events=True, size=(20,1), key='_R2_')],
                    [sg.Button('Ok'), sg.Button('Quit')]]
    
    power_sweep_layout = [
                    [sg.Text('Power Sweep Setup')],
                    [sg.Text('Select DC Supply (Sweep)'), sg.OptionMenu(values=instr_names,  k='_DCP1_')],
                    [sg.Input(size=(10,3), key='_DCP1_')],
                    [sg.Text('Select RF Supply 1')],
                    [sg.Text('Select DC Supply 2')],
                    [sg.Text('Select DC Supply 3')],
                    [sg.Button('Ok', key='_OKP_')]]

    freq_sweep_layout = [
                    [sg.Text('Frequency Sweep Setup')],
                    [sg.Text('Select RF Supply (Sweep)'), sg.OptionMenu(values=instr_names, k='_RFF1_'),
                    sg.Text('-', font='bold', text_color='LightGreen', key='_RFFLIB_')],
                    [sg.Text('Start Freq/(GHz):'), sg.Input(size=(10,3), key='_RFF1START_'),
                        sg.Text('Stop Freq/(GHz):'), sg.Input(size=(10,3), key='_RFF1STOP_'),
                        sg.Text('Samples:'), sg.Input(size=(10,3), key='_RFF1SAMPLE_'),
                        sg.Text('Stepsize/(GHz):'), sg.Input(size=(10,3), key='_RFF1STEP_')],
                    [sg.Text('Select DC Supply 1')],
                    [sg.Text('DC Voltage:'), sg.Input(size=(10,3), key='_DCF1VOLT_'),
                    sg.Text('Current Limit:'), sg.Input(size=(10,3), key='_DCF1LIM_')],
                    [sg.Text('Select DC Supply 2')],
                    [sg.Text('Select DC Supply 3')],
                    [sg.Button('Ok', key='_OKF_'),
                    sg.Button('Update', key='_UPDATEF_')]]

    logging_layout = [
                    
                    [sg.Text('Anything printed will display here!')],
                    [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True, expand_y=True, write_only=True,
                                reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True, auto_refresh=True)]]
    
    layout = [[sg.MenubarCustom(menu_def, key='_MENU_', font='Courier 15', tearoff=True)],
                [sg.Text('Demo Of GUI', size=(38, 1), justification='center', font=('Helvetica', 16), relief=sg.RELIEF_RIDGE, k='_TEXT HEADING_')]]
    
    # defining tabs
    layout +=[[sg.TabGroup([[  
                               sg.Tab('Instrument Setup', setup_layout),
                               sg.Tab('Power Sweep', power_sweep_layout, visible=False, key='_power_'),
                               sg.Tab('Frequency Sweep', freq_sweep_layout, key='_freq_'),
                               sg.Tab('Output', logging_layout)]], expand_x=True, expand_y=True),
                
                ]]
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('Instrument GUI', layout, right_click_menu=right_click_menu_def, right_click_menu_tearoff=True,
                       grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True,
                       scaling=1.5, 
                       )
    window.set_min_size(window.size)
    return window
# visa initilization 
os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\bin')
rm = visa.ResourceManager('ktvisa32')
list = rm.list_resources()          # connected device list, pass ?* for all resources not in INSTR

def main():
    global instr_data
    global instr_names
    window = make_window(sg.theme())
    # Check connection to all resources in Keysight resource library
    instr_open()
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
        window['_OUTPUT_'].update('A folder labeled ' + values['_INPUT_'] + ' will be created for the data!')
        #if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):                         # enable to show all key values
        #    print('============ Event = ', event, ' ==============')
        #    print('-------- Values Dictionary (key=value) --------')
        #    for key in values:
        #        print(key, ' = ',values[key])
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
        elif event == '_ADD_':                                          # Add an instrument to all lists
            newinstr = False                                            # comment out
            if newinstr == True:
                instr_data = [[values['_INPUT1_'], values['_INPUT2_']]]       # somehow works by adding the name and the GPIB address into a table
                instr_names = [values['_INPUT1_']]                              # which is a list[list]?
                window['_TABLE_'].update(values=instr_data)
                newinstr = False
            else:
                newdata = [values['_INPUT1_'], values['_INPUT2_']]
                instr_data.append(newdata)
                newinstr_names = values['_INPUT1_']
                instr_names.append(newinstr_names)                
                window['_TABLE_'].update(values=instr_data)      
            window['_DCP1_'].update(values=instr_names)             # update instrument option menus         
            window['_RFF1_'].update(values=instr_names)
            print('--------------')
            print(instr_data)
            print('--------------')

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
        elif event == '_UPDATEF_':                                           # update freq tab & update slected libraries
                                                                            # find current value of option menu in instrument list
            print('-------- Update --------')
            k = values['_RFF1_']                                        # gives current frequency tab option value
            print(k)
            try:
                index = instr_names.index(k)
                print(index)
                sel_address = instr_data[index][1]                      # finds address for selected instrument
                cur_lib_name = lib_select(sel_address)
                print(cur_lib_name)
                window['_RFFLIB_'].update(cur_lib_name)             # shows current active library
                if cur_lib_name == 'none':
                    window['_RFFLIB_'].update(text_color='red')
                else:
                    window['_RFFLIB_'].update(text_color='LightGreen')
            except Exception as e:
                print(type(e))
                print('UPDATE failed')

    window.close()
    exit(0)


if __name__ == '__main__':
    sg.theme('DarkBlue4')
    main()
