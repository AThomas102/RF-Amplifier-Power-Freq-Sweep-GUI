
# attach a channel to the votlage setting function
# Pysimple Gui Test #

from contextlib import nullcontext
from msilib import Table
from msilib.text import tables
from multiprocessing.connection import wait
from sqlite3 import connect
import PySimpleGUI as sg
from numpy import arange
import pyvisa as visa
import os
import math
import string
import operator


key_list1 = [('_Pa' + str(c) + '_') for c in range(2)] + [('_Pb' + str(c) + '_') for c in range(3)]                                     # NEEDS CONTINUOUS UPDATING 
                                                                                                                                        # key_list for power supply changes


newinstr = True
instr_data = [["DC Supply 1","GPIB0::2::INSTR"], ["DC Supply 2","GPIB0::3::INSTR"],["DC Supply 3","GPIB0::10::INSTR"],["DC Supply 4","GPIB0::11::INSTR"]]
instr_names = ["DC Supply 1","DC Supply 2","DC Supply 3","DC Supply 4"]
lib_select_keys = ["_PO1_", "_PO2_", "_FO1_"]
lib_change_keys = ["_PLIB1_", "_PLIB2_", "_FLIB1_"]
"""
def instr_add(value1, value2):
    values[]
    data.append()
"""

def instr_open():                  # open and list all instrument names on program start and check whether they are active
    for i in range(0, len(instr_list)):
        print('--------- Instrument ' + str(i+1) + ' -----------')
        name = instr_list[i]
        active = [False for x in range(len(instr_list))]
        try:
            resource = rm.open_resource(name)
            instr = resource.query('*IDN?')   
            instr = instr.strip()             
            print(instr)
            try:
                address = resource.query('ADDRESS?')
                address = address.strip()
                print('address: ' + address)
            except Exception as e:
                print('address command not recognised')
            active[i] = True
            print('connected: ' + str(active[i]))

        except Exception as e:
            print(type(e))
            print(name + ' resource not active or *IDN? command not recognised')
            print('connected: ' + str(active[i]))
    return active

def option_menu_update(window, values, libsl, libck, instr_names, instr_data):  # updates the current device from the one selected in the option menu
    for i in range(len(libsl)):
        print('i=' + str(i))
        k = values[libsl[i]]                                        # gives current frequency tab option value
        print('=> option menu ' + libsl[i] + ' = ' + k) 
        try:                                                
            index = instr_names.index(k)
            print(index)
            try:
                sel_address = instr_data[index][1]                      # finds address for selected instrument
            except Exception as e:
                print(type(e))
                print('no device found with this GPIB address')

            cur_lib_name = lib_select(sel_address)
            print(cur_lib_name)
            window[libck[i]].update(cur_lib_name)                  # shows current active library
            if cur_lib_name == 'none':
                window[libck[i]].update(text_color='red')
            else:
                window[libck[i]].update(text_color='LightGreen')
            print('library text updated')
        except Exception as e:
            print(type(e))
            print('UPDATE key = ' + libsl[i] + ' failed')


def lib_select(GPIB_address):               # auto selects the library to use
    try:
        resource =  rm.open_resource(GPIB_address)
        instr = resource.query('*IDN?')  
        instr = instr.strip()
        print('-library available for this GPIB address-')  
    except Exception as e:
        print(type(e))
        print('-device library unavailable-')
        instr = 'none' 
    if 'CPX400DP' in instr:                 # add libraries here
        lib_name = 'CPX400DP DC Power Supply'
    elif 'SMW200A' in instr:
        lib_name = 'SMW200A RF Supply'
    elif 'MX100TP' in instr:
        lib_name = 'MX100TP DC Power Supply'
    else:
        lib_name = 'none'                           # if returns 'none' then there is no library available yet for this device
    return lib_name

def rf_input_check(values):
    try:
        freq = float(values['_PRF_0_0_'])
        start = float(values['_PRF_0_1_'])
        stop = float(values['_PRF_0_2_'])
        step = float(values['_PRF_0_3_'])
        if freq not in arange(0.1, 30, 0.1):                           # might need to update this depending on the device
            print('Invalid freq, please use any value from 0.1-30 GHz in steps of 0.1')
        elif start not in arange(-80, 30, 1):                     # can change this range if needed
            print('Invalid start RF power, please use any value from -80 - 30 dBm')
            return 0
        elif stop not in arange(-80, 30, 1):
            print('Invalid stop RF power, please use any value from -80 - 30 dBm')
            return 0 
        elif stop < start:
            print('RF stop must be greater than RF start, please change')
            return 0
        elif step not in arange(0.1, 2, 0.1):
            print('invalid Step value, please use any value from 0.1-2.0 dB in steps of 0.1')
            return 0
        print('RF parameters OK')
        return 1
    except Exception as e:
        print(type(e))
        print('-unable to recognise RF parameters please check-')





def update_RF_supply(values, sweep_type):           # sweep type used to show which tab is currently in use 
    freq = float(values['_PRF_0_0_'])               
    try:
        if sweep_type == 'power':
            k = values['_PO1_']                     # get current option menu value
            index = instr_names.index(k)
            sel_address = instr_data[index][1]
            rf_supply =  rm.open_resource(sel_address) # open rf supply instrument
            rf_supply.write('', freq)
            rf_supply.write('', freq)
    except Exception as e:
        print(type(e))
        print('-unable to recognise RF parameters please check-')
        
    wait(1)
'''
def start_POWER_sweep():            # starts power sweep when start button is pressed
    check whether inputs are valid, e.g start and stop within range
    break if not, or if ok then advance and assign start as green or add green dot
    wait(1)
    step up 0.1 dbm from start to finish
    wait(0.1)
    read and wait for outputs
'''

def update_voltage(dc_supply, voltage_setting, channel):  # sends voltage setting
    try:
        float(voltage_setting)
        dc_supply.write('V' + str(channel) + ' ' + str(voltage_setting))
        print('Voltage SET')
    except Exception as e: 
        print(type(e))
        print('voltage setting not a value')

def update_current(dc_supply, current_setting, channel):  # sends current setting
    try:
        float(current_setting)
        dc_supply.write('V' + str(channel) + ' ' + str(current_setting))
        print('Current SET')
    except Exception as e: 
        print(type(e))
        print('current setting not a value')

def update_tab(window, parameter):
    window['_power_'].update(visible=parameter)
    window['_freq_'].update(visible=not(parameter))


    


def CPX400DP_library():                 # library to determine which options/inputs should be disabled in the layout
    d = 0                               # if they are not available for this model


# Define the window's contents
def make_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['E&xit']],
                ['&Help', ['&About']] ]

      
    headings = ['Freq', 'Voltage', 'Current']
    headings1 = ['Instrument Name', 'VISA Address']
    rfsupply_columns = ['Freq (GHz):', 'Start (dBm):', 'Stop (dBm):', 'step (dB):']
    dcsupply_columns = ['Voltage (V):', 'Current Lim (A):', 'Other Setting:']
    right_click_menu_def = [[], ['Info', 'Versions', '1', 'Nothing']]
    # layout for input columns
    rf_column1 = [[sg.Text(rfsupply_columns[j], size=(12, 1), pad=(8,1), justification='l') for j in range(4)] for i in range(1)]
    rf_column2 = [[sg.InputText(size=(14, 2), pad=(6,1), justification='l', k=('_PRF_' + str(i) + '_' + str(j) + '_')) for j in range(4)] for i in range(1)]
    power_column1 = [[sg.Text('Channel:', size=(10,1))] + [sg.Text(dcsupply_columns[j], size=(12, 1), pad=(8,1),justification='l') for j in range(3)] for i in range(1)]
    power_column2 = [[sg.Text(str(i+1), size=(10,1), justification='c')] + [sg.InputText(size=(14, 1), pad=(6,1), justification='l', k=('_PDC1_' + str(i) + '_' + str(j) + '_')) for j in range(3)] for i in range(2)]

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
                    sg.Radio('Frequency Sweep', 'Sweep', default=False, enable_events=True, size=(20,1), key='_R2_')],
                    [sg.Button('Ok'), sg.Button('Quit')]]
    
    # RF Power sweep tab, all keys include P at beginning or end
    power_sweep_layout = [                                                              
                    [sg.Text('Power Sweep Setup')],
                    [sg.Text('Select RF Supply (Sweep)', font ='bold'), sg.OptionMenu(values=instr_names, size=(12,1),  k='_PO1_'),           # options menu variables
                    sg.Text('-', font='bold', text_color='red', key='_PLIB1_')],
                    [sg.Col(rf_column1, size=(600, 25))],   # rf table texts
                    [sg.Col(rf_column2, size=(600, 30))],   # rf table inputs
                    # [sg.Text('Samples:', size=(12,1)), sg.Text('Start (dBm):', size=(12,1)), sg.Text('Stop (dBm):', size=(12,1)), sg.Text('Freq (GHz):', size=(12,1))],
                    # [sg.Input(justification='l', size=(14,2), key=('_Pa_' + str(c) + '_')) for c in range(4)],
                    [sg.Text('Select DC Supply 1', pad=((4,4),(10,0)), font ='bold'), sg.OptionMenu(values=instr_names, size=(12,1), pad=((1,1),(10,0)),  k='_PO2_'),           # options menu variables
                    sg.Text('-', font='bold', text_color='red', key='_PLIB2_')],
                    [sg.Col(power_column1, size=(600, 25))],
                    [sg.Col(power_column2, size=(600, 60))],
                    # [sg.Input(justification='l', pad=((20,0),(0,0)), size=(20,2), key=('_Pb' + str(c) + '_')) for c in range(3)],
                    [sg.Text('Select DC Supply 2', font ='bold')],
                    [sg.Text('Select DC Supply 3', font ='bold')],
                    [sg.Button('Ok', key='_OKP_'), sg.Button('Update', key='_UPDATEP_')]]

    freq_sweep_layout = [
                    [sg.Text('Frequency Sweep Setup')],
                    [sg.Text('Select RF Supply (Sweep)', font ='bold'), sg.OptionMenu(values=instr_names, size=(12,1), k='_FO1_'),           # options menu variables
                    sg.Text('-', font='bold', text_color='red', key='_FLIB1_')],
                    [sg.Text('Start Freq (GHz):', size=(18,1)), sg.Text('Stop Freq (GHz):', size=(18,1)), sg.Text('Samples:', size=(18,1)), sg.Text('Stepsize (GHz):', size=(18,1))],
                    
                    [sg.Input(justification='l', size=(20,2), key=('_Fa' + str(c) + '_')) for c in range(4)],
                    [sg.Text('Select DC Supply 1', font ='bold')],
                    [sg.Text('DC Voltage:'), sg.Input(size=(10,3), key='_DCF1VOLT_'),
                    sg.Text('Current Limit:'), sg.Input(size=(10,3), key='_DCF1LIM_')],
                    [sg.Text('Select DC Supply 2', font ='bold')],
                    [sg.Text('Select DC Supply 3', font ='bold')],
                    [sg.Button('Ok', key='_OKF_'), sg.Button('Update', key='_UPDATEF_')]]

    logging_layout = [
                    
                    [sg.Text('Anything printed will display here!')],
                    [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True, expand_y=True, write_only=True,
                                reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True, auto_refresh=True)]]
    
    layout = [[sg.MenubarCustom(menu_def, key='_MENU_', font='Courier 15', tearoff=True)],
                [sg.Text('Demo Of GUI', size=(38, 1), justification='center', font=('Helvetica', 16), relief=sg.RELIEF_RIDGE, k='_TEXT HEADING_')]]
    
    # defining tabs
    layout +=[[sg.TabGroup([[  
                               sg.Tab('Instrument Setup', setup_layout),
                               sg.Tab('Power Sweep', power_sweep_layout, visible=True, key='_power_'),
                               sg.Tab('Frequency Sweep', freq_sweep_layout, visible=False, key='_freq_'),
                               sg.Tab('Output', logging_layout)]], expand_x=True, expand_y=True),
                
                ]]
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('Instrument GUI', layout, right_click_menu=right_click_menu_def, right_click_menu_tearoff=True,
                       grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True,
                       scaling=1.5, element_padding=(4, 2)
                       )
    window.set_min_size(window.size)
    return window
# visa initilization 
os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\bin')
rm = visa.ResourceManager('ktvisa32')
instr_list = rm.list_resources()          # connected device list, pass ?* for all resources not in INSTR

def main():
    global instr_list
    global instr_data
    global instr_names
    window = make_window(sg.theme())
    print(instr_list)
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
        #'''
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):                         # enable to show all key values
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key=value) --------')
            for key in values:
                print(key, ' = ',values[key])
        #'''
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
            for key in lib_select_keys:
                window[key].update(values=instr_names)             # update all instrument option menus         
            print('--------------')
            print(instr_data)
            print('--------------')

        # elif event == '_CLEAR_':                                         # clear instruments list (to do)
        #    break
        elif event == '_RFon_':
            window['_INPUTDC1_'].update(visible=False)

        elif event == '_R1_':                                           # Power tab enable
            update_tab(window, parameter=True)
        elif event == '_R2_':                                           # Freq tab enable
            update_tab(window, parameter=False)

        elif event == '_OKF_' or event == '_OKP_':                                           # updates all selected libraries
        # find current value of option menu in instrument list
            print('-------- OK --------')                                                               # needs to be done better
            option_menu_update(window, values, lib_select_keys, lib_change_keys,
                                instr_names, instr_data)            # this could be done better

        if event == '_UPDATEP0_' or event == '_UPDATEP_':                                        # sends values to instrument RF Supply        
            print('-------- Update (P0) --------')
            if rf_input_check(values) == True:
                update_RF_supply(values, 'power')
            else:
                print('rf input is invalid')
         

        if event == '_UPDATEP1_' or event == '_UPDATEP_':                                        # sends values to instrument DC supply 1
            print('-------- Update (P1) --------')                                                 # updateP1 button needs to be added, if just one instrument
            voltage_setting_1 = values['_PDC1_0_0_']                                               # this entire event can probably be put into a single general function later on
            voltage_setting_2 = values['_PDC1_1_0_']                                               # just generally tidied up
            current_setting_1 = values['_PDC1_0_1_']
            current_setting_2 = values['_PDC1_1_1_']
            print('Power supply 1 channel 1 Voltage: ' + str(voltage_setting_1))
            k = values['_PO2_']
            try:                                               
                index = instr_names.index(k)
                print(index)
                sel_address = instr_data[index][1]                                              # finds address for selected instrument
                DC1 = rm.open_resource(sel_address)
                update_voltage(DC1, voltage_setting_1, channel=1)                                           # updates DC supply voltages and currents on this device
                update_voltage(DC1, voltage_setting_2, channel=2)                                           
                update_current(DC1, current_setting_1, channel=1)
                update_current(DC1, current_setting_2, channel=2)      
            except:
                print('-unable to recognise DC1 parameters please check-')
        

    window.close()
    exit(0)


if __name__ == '__main__':
    sg.theme('DarkBlue4')
    main()
