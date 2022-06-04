
# used imports:
from cgitb import text
from shutil import ExecError
import PySimpleGUI as sg
import numpy as np
import pandas as pd
import pyvisa as visa
import os
import time
import datetime

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
        style_name = sepname + 'Line.TSeparator'
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
        self.window['_PWR.TAB_'].update(visible=booli)
        self.window['_FRQ.TAB_'].update(visible=not(booli))
        if booli:
            ManageInputs.cur_tab = 'pwr'
        else:
            ManageInputs.cur_tab = 'freq'
        #print(ManageInputs.cur_tab)

class InstrConnect:

    name = {'DC Power Supply (1)':'DC1','DC Power Supply (2)':'DC2',
            'DC Power Supply (3)':'DC3','DC Power Supply (4)':'DC4', 'Vector Signal Generator':'RF1'}
    addr = {}
    chs = {'DC1':1,'DC2':0,'DC3':0,'DC4':0}

    def __init__(self, rm):
        self.instrlist = rm.list_resources()

    def instr_check(self, rm):
        connected = []
        print(self.instrlist)
        for addr in self.instrlist:
            try:
                rsrc = rm.open_resource(addr)
                idn = rsrc.query('*IDN?')
                try:
                    for ch in range(4):
                        v = float(rsrc.query('V' + str(ch) + 'O?'))    # for CPX400DP power supply
                        if v:
                            channels = ch+1
                except:
                    pass
                if idn:
                    connected.append([idn, addr, channels])
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

    def __init__(self):
        self.chs = InstrConnect.chs
        self.addr = InstrConnect.addr
        
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
        #print(self.DCinputs)
        return self.DCinputs 

    def DC_input_check(self, values):       # checks all dc current limit and voltage values are in valid range
        for supply in self.chs:             # for all supplies
            for i in range(self.chs[supply]):  # for all open channels
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

    def enable_channel_inputs(self, window):
        for supply in self.chs:             # for all supplies
            for i in range(4):               # for all channels
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=True) # disable all dc inputs
            for i in range(self.chs[supply]):  
                if i%2 == 0: j = 0
                else: j = 1
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=False) # reenable available channels

    def disable_inputs(self, window, disabled):           # disable all inputs/other that might need disabling before the sweep start
        for supply in self.addr:    # disable all dc inputs            
            for i in range(4):               
                window['_' + str(self.cur_tab) + '_' + str(supply)
                         + '_' + str(j) + '_' + str(i-j) + '_'].update(disabled=disabled) 

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

class InstrControl():

    def __init__(self):
        self.name = InstrConnect.name
        self.chs = InstrConnect.chs
        self.addr = InstrConnect.addr
        self.DCinputs = ManageInputs.DCinputs
        self.RFinputs = ManageInputs.RFinputs
        self.parent_dir = default_folder


    def update_DC_values(self, rm):   # updates both dc current and voltage on the supply
         for supply in self.chs:             # for all supplies
            for i in range(self.chs[supply]):  # for all channels
                try :
                    dc_supply = rm.open_resource(self.addr(supply))
                    voltage = float(self.DCinputs[supply][i][0])
                    dc_supply.write('V' + str(i+1) + ' ' + str(voltage)) # sends voltage setting, most dc supplies accept this command syntax from what I have seen
                    print('Voltage SET on channel ' + str(i))
                    time.sleep(0.1)
                except Exception as e: 
                    print(type(e))
                    print('-voltage setting not recognized-')
                try:
                    current = float(self.DCinputs[supply][i][1])
                    dc_supply.write('I' + str(i+1) + ' ' + str(current)) # sends current setting
                    print('Current SET on channel ' + str(i))
                    time.sleep(0.1)
                except Exception as e: 
                    print(type(e))
                    print('-current setting not recognized-')

    def export_to_csv(parent_dir, export_data, values):
        flat_data = {}
        flat_data['rf IN power (dBm)'] = export_data['rf_in']['pwr']  # adds data for rf vector supply
        for instr in export_data:             # adds data for dc supplies
            if 'DC' in instr:
                for ch in export_data[instr]:
                    flat_data[str(instr) + ', Channel ' + str(ch) + ' Voltage (V)'] = []
                    flat_data[str(instr) + ', Channel ' + str(ch) + ' Current (A)'] = []
                    for measurement in export_data[instr][ch]:
                        translation_table = dict.fromkeys(map(ord, 'VA'), None)     # add units/characters to remove 
                        voltage = measurement[0].strip().translate(translation_table)
                        current = measurement[1].strip().translate(translation_table)
                        flat_data[str(instr) + ', Channel ' + str(ch) + ' Voltage (V)'].append(voltage)
                        flat_data[str(instr) + ', Channel ' + str(ch) + ' Current (A)'].append(current)
        print(flat_data.keys())
        try:
            flat_data = InstrControl.pad_dict_list(flat_data, '-')
            df = pd.DataFrame(flat_data, columns=flat_data.keys())
            dt_string = get_title(values)
            output_folder = values['_INPUT_']
            df.to_csv(str(parent_dir) +'/' + str(output_folder) + '/' + str(dt_string) + '.csv', header=True)
        except Exception as e:
            print(type(e))
            print('-data export to csv unsuccessful-')
            return False
        
        return True


    def get_name(self, val):
        for key, value in self.name.items():
            if val == value:
                return key

    def get_DC_values(self, dc_supplies, data_out): # gets the data for all dc devices 
        for supply in dc_supplies:
            for ch in range(self.chs[supply]):
                try:
                    current = dc_supplies[supply].query('I' + str(ch) + 'O?')    # this command is for the CPX400DP power supply
                except Exception as e:
                    print(type(e))
                    current = '-'
                try:
                    voltage = dc_supplies[supply].query('V' + str(ch) + 'O?')
                except Exception as e:
                    print(type(e))
                    voltage = '-'
                try:
                    current_values = voltage, current
                    data_out[supply]['ch' + str(ch)].append(current_values)     
                except Exception as e:
                    print(type(e))
                    current_values = '-','-'
                    data_out[supply]['ch' + str(ch)].append(current_values)
                print('supply' + str(supply) + ', channel: ' + str(ch) + \
                 ' V = ', str(voltage),', I = ', str(current))
                    
        return data_out


    def start_POWER_sweep(self, values):  # starts power sweep when start button is pressed
        
        complete = False
        instr_out_data = {'':{'':[]}}   # create all channel data lists
        dc_supplies = {}
        for supply in self.chs:    # for all supplies
            for ch in range(self.chs[supply]):       # for all channels
                instr_out_data[supply][str(ch+1)] = []
        instr_out_data['rf_in']['pwr'] = []
        instr_out_data['rf_out']['pwr'] = []
        print(instr_out_data)   

        try:  # connects to the rf supply if it is not already connected
            rf_supply = rm.open_resource(self.addr['RF']) # this might close
        except Exception as e:                            # may need to reopen resource
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1   # exits function if rf supply is not connected
        try:
            for supply in self.addr:  # connects to the dc supply if it is not already connected
                dc_supplies[supply] = rm.open_resource(self.addr[supply])
        except Exception as e:
            print(type(e))
            print('Connection to ' + str(InstrControl.get_name(supply)) + ' failed')

        InstrControl.toggle_channels(dc_supplies, enabled=1)
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('SOURce1:FREQuency:CW ' + str(self.RFinputs['freq']) + ' GHz')
        rf_supply.write('SOURce1:SWEep:POWer:MODE MANual')
        rf_supply.write('SOURce1:POWer:STARt ' + str(self.RFinputs['start']) + ' dBm')
        rf_supply.write('SOURce1:POWer:STOP ' + str(self.RFinputs['stop']) + ' dBm')
        rf_supply.write('SOURce1:POWer:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:POWer:STEP ' + str(self.RFinputs['step']))
        while complete == False:
            # I need to check for some kind of interupt here during the sweep
            rf_supply.write('SOURce1:POWer:MANual UP')
            time.sleep(0.2)
            try:
                current_rf_power = float(rf_supply.query('SOURce1:POWer:POWer?')) 
                instr_out_data['rf_in']['pwr'].append(current_rf_power) # append current rf power
            except Exception as e:
                current_rf_power = '-'
                instr_out_data['rf_in']['pwr'].append(current_rf_power)
            print('current rf power = ' + str(current_rf_power))
            instr_out_data = InstrControl.get_DC_values(dc_supplies, instr_out_data)
            if current_rf_power >= self.RFinputs['stop']:       # check whether sweep is complete
                complete = True
        InstrControl.toggle_channels(dc_supplies, enabled=0)
        print('-RF Power Sweep Complete-')
        if InstrControl.export_to_csv(self.parent_dir, instr_out_data, values) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccesful')
        return 0

    def toggle_channels(self, dc_supplies, enabled): # toggle on dc channels
        for supply in dc_supplies:
            for ch in range(self.chs[supply]):
                dc_supplies[supply].write('OP' + str(ch) + ' ' + str(enabled))           

    def pad_dict_list(dict_list, padel):
        lmax = 0
        for lname in dict_list.keys():
            lmax = max(lmax, len(dict_list[lname]))
        for lname in dict_list.keys():
            ll = len(dict_list[lname])
            if  ll < lmax:
                dict_list[lname] += [padel] * (lmax - ll)
        return dict_list

def get_title():
        try:
            name_dic = []
            file_string = ''
            date = datetime.datetime.now().strftime('%d_%m_%Y')
            time = datetime.datetime.now().strftime('%H-%M-%S')
            cwfreq = values['_pwr_RF0_0_'] # cw freq
            start = values['_pwr_RF0_1_']   # start
            stop = values['_pwr_RF0_2_']    # stop

            if values['_DATE_'] == True:
                name_dic.append(date)
            if values['_TIME_'] == True:
                name_dic.append(time)
            if values['_CWFREQ_'] == True:
                name_dic.append(cwfreq)
            if values['_SSP_'] == True:
                name_dic.append(start)
                name_dic.append(stop)
            for nam in name_dic:
                file_string = file_string + str(nam) + ' '
            file_string = file_string[1:-1] # remove last space     
        except Exception as e:
            print(type(e))
            print('-file name could not be generated-')
            file_string = 'export data'
        return file_string
        


if __name__ == '__main__':

    frqsuff = ['Hz', 'kHz', 'MHz', 'GHz']
    default_folder = 'C:/Users/AndrewThomas/OneDrive - ' + \
        'CSA Catapult/Documents/Equipment VISA Integration/RF sweep data'
    # standard theme colour
    sg.theme('DarkBlue4')
    BG = BuildGui(window=None)
    setup_col_1 = [[sg.Button('Search Instruments', key='_INSTR.SEARCH_',
                              font='bold 11', button_color='Gray58')],
                   [sg.Table(size=(80,1), values=[['','','']],
                             headings=['Instrument ID', 'VISA Address',
                                       'Instrument Function', 'Channels'],
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
         sg.OptionMenu(values=InstrConnect.name.keys(),
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
         sg.Push()],
        [sg.HorizontalSeparator(key='_SEP.2_')],
        [sg.Text('Select export options:', font='bold 12'), sg.Push()], 
        [sg.Col([[sg.Button('Open Folder'),
            sg.Text('Save in: ' + str(default_folder), key='_FOLDER_')]]),
         sg.Push()],
        [sg.Text('Include in file title:'), sg.Push()],
        [sg.Col([[sg.Checkbox('Date', default=True, k='_DATE_'),
         sg.Checkbox('Time', default=True, k='_TIME_'),
         sg.Checkbox('CW Frequency', default=True, k='_CWFREQ_'),
         sg.Checkbox('Stop and Start Power', default=True, k='_SSP_')]]),
         sg.Push()],
         [sg.Col([[sg.Checkbox('RF Power Level', default=False, disabled=True, k='_RFPL_'),
         sg.Checkbox('Stop and Start frequency', default=False, disabled=True, k='_SSF_')]]),
         sg.Push()],
    
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
    logging_layout = [ 
                    [sg.Text('Logging tab for debugging problems.')],
                    [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True,
                                   expand_y=True, write_only=True, reroute_stdout=True,
                                    reroute_stderr=True, echo_stdout_stderr=True,
                                     autoscroll=True, auto_refresh=True)]
    ]
    
    
    layout = [[sg.TabGroup([[
        sg.Tab('Instrument Setup', setup_layout, element_justification= 'c'),
        sg.Tab('Power Sweep', pwr_layout, visible=True, key='_PWR.TAB_'),
        sg.Tab('Frequency Sweep', frq_layout, visible=False, key='_FRQ.TAB_'),
        sg.Tab('Logging', logging_layout)]],
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
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):  # enable to show all key values
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
                InstrConnect.addr[InstrConnect.name['_INSTR.FUNC_']] \
                 = connected[rowselected][1]    # add instr addr to dic
                InstrConnect.chs[InstrConnect.name['_INSTR.FUNC_']] \
                 = connected[rowselected][3]    # add instr chs to dic
                
                window['_INSTR.TABLE_'].update(values=connected)
                MI.enable_channels(window)
            else:
                sg.popup_error(f'Make sure instrument and functionality '
                                'both selected in order to update table.')
            

        elif event == '_PWR.SWEEP_':
            BG.update_tab(booli=True)
            
        elif event == '_FRQ.SWEEP_':
            BG.update_tab(booli=False)

        elif event == 'Open Folder':
            print('Clicked Open Folder!')
            folder = sg.popup_get_folder('Choose your folder', keep_on_top=True)
            print('User chose folder: ' + str(folder))
            if folder != '':
                sg.popup('You chose: ' + str(folder), keep_on_top=True)
                window['_FOLDER_'].update('save in: ' + str(folder))
                InstrControl.parent_dir = str(folder)
            else: sg.popup('Folder is invalid', keep_on_top=True)

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
                    IC = InstrControl(IC.chs, IC.addr, MI.DCinputs)
                        

    window.close()
