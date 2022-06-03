
# used imports:
import PySimpleGUI as sg
import numpy as np
import pyvisa as visa
import os
import time

class BuildGui:

    def __init__(self, window):
        self.window = window
        self.pwr_idx = 0
        self.freq_idx = 0
        self.tabs = ['pwr','freq']
        self.rfsupply_col_names = ['Freq (GHz):', 'Start (dBm):', 'Stop (dBm):', 'Step (dB):']
        self.dcsupply_col_names = ['Voltage (V) 1/2:', 'Current Lim (A) 1/2:',
                                   'Voltage (V) 3/4:', 'Current Lim (A) 3/4:']
        self.default_rf_inputs = ['0.5', '-20', '-10', '1']

    # change separator colour
    def sep_colour(self, sepname, sepcolour):
        style_name = sepname + "Line.TSeparator"
        button_style = sg.ttk.Style()
        button_style.theme_use(self.window.TtkTheme)
        button_style.configure(style_name, background = sepcolour)
        self.window[sepname].Widget.configure(style = style_name)

    def power_supply_col_name(self):
        names = [[sg.Text('Channel:', size=(18,1), font='bold 10')] 
                            + [sg.Text(self.dcsupply_col_names[j],
                           size=(16, 1), font='bold 10', justification='l') 
                           for j in range(4)] for i in range(1)]
        pwr_col_names = sg.Col(names, size=(800, 25))
        return pwr_col_names

    def power_supply_col_inputs(self, tab_name, disabled=True):
        inputs = [[sg.Text(str(i+1) + '/' + str(i+3), size=(18,1), justification='c')] + 
                            [sg.InputText(size=(18, 1), justification='l', disabled=disabled, 
                             k=('_' +  str(tab_name) + '_DC' + str(self.pwr_idx + 1)
                              + '_' + str(i) + '_' + str(j) + '_'))
                             for j in range(4)] for i in range(2)]
        if tab_name == 'pwr':                     # useful for iterating the input keys
            self.pwr_idx = self.pwr_idx+1
        elif tab_name == 'freq':
            self.freq_idx = self.freq_idx+1
        power_col_inputs = sg.Col(inputs, size=(800, 60))
        return power_col_inputs

    def rf_supply_col_name(self):
        names = [[sg.Text(self.rfsupply_col_names[j], size=(16, 1),
                  font='bold 10', justification='l')
                  for j in range(4)] for i in range(1)]
        rf_col_names = sg.Col(names, size=(600, 25))
        return rf_col_names
        
    def rf_supply_col_inputs(self, tab_name, disabled=True):
        inputs = [[sg.InputText(self.default_rf_inputs[j], size=(18, 1),
                   justification='l', disabled=disabled,
                    k=('_' +  str(tab_name) + '_RF' + str(i) + '_' + str(j) + '_'))
                   for j in range(4)] for i in range(1)]
        rf_col_inputs = sg.Col(inputs, size=(600, 30))
        return rf_col_inputs
        
        
    def update_tab(self, booli):
        window['_PWR.TAB_'].update(visible=booli)
        window['_FRQ.TAB_'].update(visible=not(booli))
        if booli:
            ManageInputs.cur_tab = 'pwr'
        else:
            ManageInputs.cur_tab = 'freq'

class InstrConnect:

    name = {'DC Power Supply (1)':'DC1','DC Power Supply (2)':'DC2',
            'DC Power Supply (3)':'DC3','DC Power Supply (4)':'DC4'}
    addr = {'DC1':'','DC2':'','DC3':'','DC4':''}
    chs= {'DC1':1,'DC2':0,'DC3':0,'DC4':0}

    def __init__(self, rm):
        self.instrlist = rm.list_resources()

    def instr_check(self, rm):
        connected = []
        print(self.instrlist)
        for addr in self.instrlist:
            try:
                rsrc = rm.open_resource(addr)
                idn = rsrc.query('*IDN?')
                if idn:
                    connected.append([idn, addr, self.chs])
            except:
                pass              
        return connected
    
    def DCSupply_check_channels(self, rm):
        for supply in self.name:
            try:
                dc_supply = rm.open_resource(self.addr[supply])
                for ch in range(4):
                    v = float(dc_supply.query('V' + str(ch) + 'O?'))    # this command is for the CPX400DP power supply
                    self.chs[supply] = ch+1
            except:
                pass
        return self.chs

class ManageInputs(InstrConnect):

    DCinputs = {'DC1':[],'DC2':[],'DC3':[],'DC4':[]}
    RFinputs = {}
    cur_tab = 'pwr'

    def __init__(self, chs, addr):
        self.chs = chs
        self.addr = addr
        
    def get_DC_inputs(self, values):
        for supply in self.chs:
            if self.chs[supply] > 0:    # get channel 1 voltage & current
                ch1 = [[values['_' + self.cur_tab + '_' + supply + '_0_0_'],
                 values['_' + self.cur_tab + '_' + supply + '_0_1_']]] 
                self.DCinputs[supply] = ch1                  
            if self.chs[supply] > 1:        # for 2 channel supplies
                ch2 = [values['_' + self.cur_tab + '_' + supply + '_1_0_'],
                 values['_' + self.cur_tab + '_' + supply + '_1_1_']]
                self.DCinputs[supply].append(ch2)
            if self.chs[supply] > 2:        # for 3 channel supplies
                ch3 = [values['_' + self.cur_tab + '_' + supply + '_0_2_'],
                 values['_' + self.cur_tab + '_' + supply + '_0_3_']]
                self.DCinputs[supply].append(ch3)
            if self.chs[supply] > 3:        # for 4 channel supplies
                ch4 = [values['_' + self.cur_tab + '_' + supply + '_1_2_'],
                 values['_' + self.cur_tab + '_' + supply + '_1_3_']]
                self.DCinputs[supply].append(ch4)
        # print(self.DCinputs)
        return self.DCinputs 

    def DC_input_check(self, values):       # checks all dc current limit and voltage values are in valid range
        for supply in self.chs:             # for all supplies
            for i in range(self.chs[supply]):  # for all channels
                if i%2 == 0: j = 0
                else: j = 1
                try:
                    voltage = float(values['_' + str(self.cur_tab) + '_'
                     + str(supply) + '_' + str(j) + '_' + str(i-j) + '_'])
                    current = float(values['_' + str(self.cur_tab) + '_'
                     + str(supply) + '_' + str(j) + '_' + str(i-j+1) + '_'])
                    print(voltage)
                    print(current)
                    if  0 <= voltage <= 30 and (100*voltage)%1 == 0:                           
                        print('OK Voltage on channel:', str(i+1))
                    else:
                        print('-Invalid voltage on channel:', str(i+1),
                         ', please use any value from 0-30 V in steps of 0.01-')
                        return 0
                    if  0 <= current <= 5 and (100*current)%1 == 0:                           
                        print('OK Current on channel:', str(i+1))
                    else:
                        print('-Invalid current on channel:', str(i+1),
                         ', please use any value from 0-5 A in steps of 0.01-')
                        return 0
                except Exception as e:
                    print(type(e))
                    print('-please input a value-')
                    return 0
        print('DC parameters OK')
        return 1

    def enable_channels(self, window):
        for supply in self.addr:             # for all supplies
            for i in range(4):               # for all channels
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=True) # disable all dc inputs
            for i in range(self.chs[supply]):  
                if i%2 == 0: j = 0
                else: j = 1
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=False) # reenable available channels

    def disable_inputs(self, window, enabled):           # disable all inputs/other that might need disabling before the sweep start
        for supply in self.addr:    # disable all dc inputs            
            for i in range(4):               
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=True) 

    def get_RF_inputs(self, values):
        if str(self.cur_tab) == 'pwr':
            self.RFinputs['freq'] = float(values['_pwr_RF0_0_'])
            self.RFinputs['start'] = float(values['_pwr_RF0_1_'])
            self.RFinputs['stop'] = float(values['_pwr_RF0_2_'])
            self.RFinputs['step'] = float(values['_pwr_RF0_3_'])
        print(self.RFinputs)
        return self.RFinputs
    
    def RF_input_check(self, values):
        if str(self.cur_tab) == 'pwr':
            try:
                freq = float(values['_pwr_RF0_0_'])
                start = float(values['_pwr_RF0_1_'])
                stop = float(values['_pwr_RF0_2_'])
                step = float(values['_pwr_RF0_3_'])
                if  0.1 <= freq <= 30 and (100*freq)%1 == 0:                           
                    print('OK Frequency')
                else:
                    print('Invalid freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if -80 <= start <= 30 and (10*start)%1 == 0:                     
                    print('OK start')
                else:
                    print('Invalid start RF power, please use any value from -80 - 30 dBm')
                    return 0
                if -80 <= stop <= 30 and (10*stop)%1 == 0:
                    print('OK stop')
                else:
                    print('Invalid stop RF power, please use any value from -80 - 30 dBm')
                    return 0
                if start < step:
                    print('OK start and stop')
                else:
                    print('RF stop must be greater than RF start')
                    return 0
                if 0.01 <= step <= 10 and (100*step)%1 == 0:
                    print('OK step')
                else:
                    print('invalid Step value, please use any value from 0.01-10.0 dB in steps of 0.01')
                    return 0
                print('RF parameters OK')
                return 1
            except Exception as e:
                print(type(e))
                print('-unable to recognise RF parameters please check-')

#Class InstrControl():

if __name__ == '__main__':

    frqsuff = ['Hz', 'kHz', 'MHz', 'GHz']

    # standard theme colour
    sg.theme('DarkBlue4')
    BG = BuildGui(window=None)
    setup_col_1 = [[sg.Button('Search Instruments', key='_INSTR.SEARCH_',
                              font='bold 11', button_color='Gray58')],
                   [sg.Table(size=(80,1), values=[['','','']],
                             headings=['Instrument ID', 'VISA Address',
                                       'Instrument Function'],
                             max_col_width=25, text_color='black',
                             background_color='White', auto_size_columns=True,
                             display_row_numbers=False, justification='right',
                             num_rows=3, key='_INSTR.TABLE_', row_height=25,
                             enable_events=True,
                             select_mode=sg.TABLE_SELECT_MODE_BROWSE)]]

    setup_layout = [
        [sg.Col(setup_col_1)], [sg.HorizontalSeparator(key='_SEP.1_')],
        [sg.Text('Select instrument from table and assign functionality:',
                 font='bold 12'), sg.Push()],
        [sg.Text('Instrument ID:', size=(18,1), font='bold 11'),
         sg.Input(size=(28,1), disabled=True, key='_SLCT.INSTR_'),
         sg.Push()],
        [sg.Text('Instrument functionality:', size=(18,1), font='bold 11'),
         sg.OptionMenu(values=['Vector Signal Generator', 'DC Power Supply (1)',
                       'DC Power Supply (2)', 'DC Power Supply (3)', 'DC Power Supply (4)'],
                       key='_INSTR.FUNC_'),
         sg.Push()],
        [sg.Col([[sg.Button('Update Instrument', key='_UPDATE.INSTR_',
                   font='bold 11', button_color='Gray58')]]),
         sg.Push()],
        [sg.HorizontalSeparator(key='_SEP.2_')],
        [sg.Text('Select sweep mode:', font='bold 12'), sg.Push()],
        [sg.Col([[sg.Radio('Power Sweep', 'Sweep', default=True,
                           enable_events=True, key='_PWR.SWEEP_',
                           font='bold 11')],
        [sg.Radio('Frequency Sweep', 'Sweep', default=False,
                  enable_events=True, key='_FRQ.SWEEP_', font='bold 11')]]),
         sg.Push()]
        ]

    frq_layout = [
        [sg.Text('Select frequency sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [sg.Text('Start Freq:', size=(18,1)),
         sg.Text('Stop Freq:', size=(18,1))],
        [sg.Input(justification='l', size=(13,2), key=('_F1_')),
         sg.OptionMenu(values=frqsuff),
         sg.Input(justification='l', size=(13,2), key=('_F2_')),
         sg.OptionMenu(values=frqsuff)],
        ]

    pwr_layout = [
         [sg.Text('Select power sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name()],   # rf table texts
        [BG.rf_supply_col_inputs('pwr', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 1: ', 
                   font='bold 12')],
        [sg.Text('-', k='_pwr1_')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 2: ', 
                   font='bold 12')],
        [sg.Text('-', k='_pwr2_')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 3: ', 
                   font='bold 12')],
        [sg.Text('-', k='_pwr3_')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [sg.Text('-', k='_pwr3_')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.Button('Ok', pad=(5,10), key='_OKP_'),
         sg.Button('Update', pad=(5,10), key='_UPDATEP_'),
         sg.Button('START', pad=((600,20),(10,10)), key='_STARTP_')], 
          # TO DO, color start button green or red depending on whether all inputs are valid
    ]
    
    
    layout = [[sg.TabGroup([[
        sg.Tab('Instrument Setup', setup_layout, element_justification= 'c'),
        sg.Tab('Power Sweep', pwr_layout, visible=True, key='_PWR.TAB_'),
        sg.Tab('Frequency Sweep', frq_layout, visible=False, key='_FRQ.TAB_')]],
                           tab_location='centertop', title_color='White',
                           tab_background_color='Gray',
                           selected_title_color='White',
                           selected_background_color='Purple',
                           border_width=5)]]

    window = sg.Window('RF Amplifier Frequency/Power Sweep',
                       layout, grab_anywhere=True, resizable=True,
                       margins=(0,0), finalize=True,
                       scaling=1.5, element_padding=(4, 2))
    
    window.set_min_size(window.size)
    os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries '
                                 'Suite\\bin')
    rm = visa.ResourceManager('ktvisa32')
    BG = BuildGui(window)
    BG.sep_colour('_SEP.1_','SlateBlue3')
    BG.sep_colour('_SEP.2_','SlateBlue3')
    
    while True:
        event, values = window.read()  
        IC = InstrConnect(rm)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):                         # enable to show all key values
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key=value) --------')
            for key in values:
                print(key, ' = ',values[key])

        if event == '_INSTR.SEARCH_':
            connected = IC.instr_check(rm)
            window['_INSTR.TABLE_'].update(values=connected)
            
            if len(connected) == 0:
                sg.popup_error(f'No connected instruments detected. Ensure '
                               'instrument connected and search again.')

        elif event == '_INSTR.TABLE_':
            try:
                rowselected = [connected[row] for row in values[event]]
                instrselected = rowselected[0]
                window['_SLCT.INSTR_'].update(instrselected)
            except:
                sg.popup_error(f'Select correct connection when '
                               'displayed in the table.')

        elif event == '_UPDATE.INSTR_':
            if values['_SLCT.INSTR_'] != '' and values['_INSTR.FUNC_'] != '':
                connected[rowselected][2] = values['_INSTR.FUNC_']
                IC.addr[IC.name['_INSTR.FUNC_']] = connected[rowselected][1]    # add instr addr
                window['_INSTR.TABLE_'].update(values=connected)
                MI.enable_channels(window)

            else:
                sg.popup_error(f'Make sure instrument and functionality '
                                'both selected in order to update table.')

        elif event == '_PWR.SWEEP_':
            BG.update_tab(booli=True)
            
        elif event == '_FRQ.SWEEP_':
            BG.update_tab(booli=False)
            
        elif event == '_OKF_' or event == '_OKP_':                                           
            print('-------- OK --------')                                                               
            try:
                MI = ManageInputs(IC.chs, IC.addr)
                if MI.DC_input_check(values) == True:
                    if MI.RF_input_check(values) == True:
                        DCinputs = MI.get_DC_inputs(values)
                        RFinputs = MI.get_RF_inputs(values)
                    else:
                        print('RF signal generator input is invalid')
                else:
                    print('DC supply input is invalid')
            except:
                print('Instrument connect not completed')
                
        elif event == '_UPDATEP0_' or event == '_UPDATEP_':
            print('-------- Update (P0) --------')
            if MI.DC_input_check(values) == True:
                    if MI.RF_input_check(values) == True:


    window.close()
