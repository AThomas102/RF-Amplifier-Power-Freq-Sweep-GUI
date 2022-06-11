
# combine frequency and power sweeps
#
# integrate gate voltage and drain quiescent current, create start/stop sequence for gate & drain 
# 
# move unneccesary functions out of classes 
#
# instr connect class can be removed and simplified
#
# add vrange and current protection on sweeps
#
# add checkbox for OCP
#
#
#
#
# used imports:
import PySimpleGUI as sg
import pandas as pd
import pyvisa as visa
import os
import time
import datetime

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
            #print(name_dic)
            file_string = '_'.join(name_dic)
        except Exception as e:
            print(type(e))
            print('-file name could not be generated-')
            file_string = 'export data'
        return file_string  

def gate_button_update(gate_control):
    if gate_control: 
        active = 'ON'
        window['_GATEP_'].update('Gate ON', button_color='green')
        window['_GATEF_'].update('Gate ON', button_color='green')
    else: 
        active = 'OFF'
        window['_GATEP_'].update('Gate OFF', button_color='red')
        window['_GATEF_'].update('Gate OFF', button_color='red')
    return active

def flatten_data(export_data, sweep_type):
    try:
        flat_data = {}
        flat_data['rf IN power (dBm)'] = export_data['rf_in'][sweep_type]  # adds data for rf vector supply
        for instr in export_data:             # adds data for dc supplies
            if 'DC' in instr:
                for ch in export_data[instr]:
                    flat_data[str(instr) + ', Channel ' + str(ch) + ' Voltage (V)'] = []
                    flat_data[str(instr) + ', Channel ' + str(ch) + ' Current (A)'] = []
                    for measurement in export_data[instr][ch]:
                        current = strip_measurement(measurement[0])
                        voltage = strip_measurement(measurement[1])
                        flat_data[str(instr) + ', Channel ' + str(ch) + ' Voltage (V)'].append(voltage)
                        flat_data[str(instr) + ', Channel ' + str(ch) + ' Current (A)'].append(current)
        #print(flat_data.keys())
        flat_data = pad_dict_list(flat_data, '-')
        return flat_data
    except Exception as e:
        print(type(e))
        return 'nul'

def read_dc_values(chs, dc_supplies, data_out): # gets the data for all dc devices 
    for supply in dc_supplies:
        for ch in range(chs[supply]):
            try:
                current = dc_supplies[supply].query('I' + str(ch+1) + 'O?')    # this command is for the CPX400DP power supply
            except Exception as e:
                print(type(e))
                current = '-'
            try:
                voltage = dc_supplies[supply].query('V' + str(ch+1) + 'O?')
            except Exception as e:
                print(type(e))
                voltage = '-'
            try:
                current_values = voltage, current
                data_out[supply][ch+1].append(current_values)     
            except Exception as e:
                print(type(e))
                current_values = '-','-'
                data_out[supply][ch+1].append(current_values)
            print('supply' + str(supply) + ', channel: ' + str(ch+1) + \
                ' V = ', str(voltage),', I = ', str(current))
                
    return data_out

def tgl_drain_chs(chs, dc_supplies, enabled=1): # toggle on supply drain channels
    try:
        for supply in dc_supplies:
            if supply != 'DC1':
                for ch in range(chs[supply]):
                    dc_supplies[supply].write('OP' + str(ch) + ' ' + str(enabled))
        return True 
    except:
        return False 

def strip_measurement(measurement):
    translation_table = dict.fromkeys(map(ord, 'VA'), None)     # add units/characters to remove 
    out = measurement[0].strip().translate(translation_table)
    return out

def tgl_gate_chs(chs, dc_supplies, enabled=1): # toggle on supply gate channels 
    try:
        for ch in range(chs[dc_supplies['DC1']]):
            dc_supplies[dc_supplies].write('OP' + str(ch) + ' ' + str(enabled))
            on = dc_supplies[dc_supplies].write('OP' + str(ch)) 
            volt = dc_supplies[dc_supplies].write('V' + str(ch) + 'O?') 
            volt = int(strip_measurement(volt))
            on = int(strip_measurement(on))
            if on == 1 and volt >= 4:
                out = True
            return False
        return out
        
    except:
        print('-gate supply toggle error-')
        return False
    
def export_to_csv(flat_data):
    try:
        df = pd.DataFrame(flat_data, columns=flat_data.keys())
        dt_string = get_title()
        if folder == []:
            output_folder = default_folder
        else:
            output_folder = folder
        df.to_csv(str(output_folder) + '/' + str(dt_string) + '.csv', header=True)
        print('exported at: ', str(output_folder))
    except Exception as e:
        print(type(e))
        print('-data export to csv unsuccessful-')
        return False
    return True

class BuildGui:

    def __init__(self, window):
        self.window = window
        self.supply_idx = {'pwr':0,'freq':0}
        self.rfsupply_col_names = {'pwr':['Freq (GHz):', 'Start (dBm):', 'Stop (dBm):', 'Step (dB):', 'Step Time (s)'],'freq':['Start Freq (GHz):', 'Stop Freq (GHz):', 'Step Freq (GHz):', 'Level (dBm):', 'Step Time (s)']}
        self.dcsupply_col_names = ['Voltage (V) 1/2:', 'Current Lim (A) 1/2:',
                                   'Voltage (V) 3/4:', 'Current Lim (A) 3/4:']
        self.default_rf_inputs = {'pwr':['0.5', '-20', '-10', '1', '2'], 'freq':['0.5', '2', '0.1', '-10', '2']}

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
                            [sg.InputText('1', size=(18, 1), justification='l', disabled=disabled, 
                             k=('_' +  str(tab_name) + '_DC' + str(self.supply_idx[tab_name] + 1)
                              + '_' + str(i) + '_' + str(j) + '_'))
                             for j in range(4)] for i in range(2)]
        self.supply_idx[tab_name] = self.supply_idx[tab_name]+1   # useful for iterating the input keys
        power_col_inputs = sg.Col(inputs, size=(800, 60))
        return power_col_inputs

    def rf_supply_col_name(self, tab_name):
        length = len(self.rfsupply_col_names[tab_name])
        names = [[sg.Text(self.rfsupply_col_names[tab_name][j], size=(16, 1),
                  font='bold 10', justification='l')
                  for j in range(length)] for i in range(1)]
        rf_col_names = sg.Col(names, size=(600, 25))
        return rf_col_names
        
    def rf_supply_col_inputs(self, tab_name, disabled=True):
        length = len(self.rfsupply_col_names[tab_name])
        inputs = [[sg.InputText(self.default_rf_inputs[tab_name][j], size=(18, 1),
                   justification='l', disabled=disabled,
                    k=('_' +  str(tab_name) + '_RF' + str(i) + '_' + str(j) + '_'))
                   for j in range(length)] for i in range(1)]
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
    
    name = {'DC Power Supply (1) (Gate Supply Only)':'DC1','DC Power Supply (2)':'DC2',
            'DC Power Supply (3)':'DC3','DC Power Supply (4)':'DC4', 'Vector Signal Generator':'RF1'}
    addr = {'DC1':'','DC2':'','DC3':'','DC4':''}
    chs = {'DC1':0,'DC2':0,'DC3':0,'DC4':0}
    rfaddr = {'RF1':''}

    def __init__(self, rm):
        self.instrlist = rm.list_resources()

    def get_name(self, val):
        try:
            for key, value in self.name.items():
                if val == value:
                    return key
        except:
            return 'None'

    def instr_check(self, rm):
        self.instrlist = rm.list_resources()
        time.sleep(0.1) # give the resource manager time
        connected = []
        names = []
        print(self.instrlist)
        for addr in self.instrlist:
            channels = '-'
            idn =[]
            try:
                rsrc = rm.open_resource(addr)
                idn = rsrc.query('*IDN?').strip()
                for ch in range(4): # check for number of channels
                    value = rsrc.query('V' + str(ch+1) + 'O?')    # for CPX400DP power supply
                    if value:
                        channels = ch+1
            except:
                pass
            if idn in names:
                pass
            elif idn:
                names.append(idn)
                connected.append([idn, addr, channels, ''])
        print(connected)
        return connected

class ManageInputs:

    tabs = ['pwr','freq']
    cur_tab = 'pwr'
    DCinputs = {'DC1':[],'DC2':[],'DC3':[],'DC4':[]}
    RFinputs = {}

    def __init__(self):
        self.chs = InstrConnect.chs
        self.addr = InstrConnect.addr
        
    def get_dc_inputs(self, values):
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

    def dc_input_check(self, values):       # checks all dc current limit and voltage values are in valid range
        for supply in self.chs:             # for all supplies
            # print(self.chs[supply])
            for i in range(self.chs[supply]):  # for all open channels
                if i%2 == 0: j = 0
                else: j = 1
                try:
                    voltage = float(values['_' + str(self.cur_tab) + '_'
                     + str(supply) + '_' + str(j) + '_' + str(i-j) + '_'])
                    current = float(values['_' + str(self.cur_tab) + '_'
                     + str(supply) + '_' + str(j) + '_' + str(i-j+1) + '_'])

                    if  0 <= voltage <= 30 and (100*voltage)%1 == 0:                           
                        print('OK Voltage on channel:', str(i+1))
                    else:
                        print('-Invalid voltage on channel:', str(i+1),
                         ', please use any value from 0-30 V in steps of 0.01-')
                        return False
                    if  0 <= current <= 5 and (100*current)%1 == 0:                           
                        print('OK Current on channel:', str(i+1))
                    else:
                        print('-Invalid current on channel:', str(i+1),
                         ', please use any value from 0-5 A in steps of 0.01-')
                        return False
                except Exception as e:
                    print(type(e))
                    print('-please input a value-')
                    return False  
        print('DC parameters OK')
        return True

    def table_update(self, window):
        rowselected = []
        rowselected = [connected[row] for row in values['_INSTR.TABLE_']]
        if rowselected != []:
            function = values['_INSTR.FUNC_']
            for i in range(len(connected)):
                if connected[i][3] == function:
                    connected[i][3] = ''
            try:
                prev_name = IC.name[rowselected[0][3]]
                IC.addr[prev_name] = ''
                IC.chs[prev_name] = 0
            except:
                pass
            rowselected[0][3] = function
            name = IC.name[function]
            window['_INSTR.TABLE_'].update(values=connected)
            if 'DC Power Supply' in function:
                IC.addr[name] \
                = rowselected[0][1]    # add instr addr to dic
                IC.chs[name] \
                = rowselected[0][2]    # add instr chs to dic
                return 'DC Power Supply'
            elif 'Vector Signal Generator' in function:
                IC.rfaddr[name] \
                = rowselected[0][1]
                return 'Vector Signal Generator'
        else:
            return False

    def enable_channel_inputs(self, window):
        print(self.chs)
        try:    # if not type(int)
            for tab in self.tabs:
                for supply in self.chs:
                    for i in range(4):
                        for j in range(2): 
                            window['_' + str(tab) + '_' + str(supply)
                                    + '_' + str(j) + '_' + str(i) + '_'].update(disabled=True)
                for supply in self.chs: 
                    print(self.chs[supply])
                    for ch in range(self.chs[supply]):  # reenable available channels
                        print(ch)
                        j = ch%2
                        if ch>1: i = 2
                        else: i = 0
                        print(i)
                        print(j)
                        window['_' + str(tab) + '_' + str(supply)
                                + '_' + str(j) + '_' + str(i) + '_'].update(disabled=False) 
                        window['_' + str(tab) + '_' + str(supply)
                                + '_' + str(j) + '_' + str(i+1) + '_'].update(disabled=False) 
        except Exception as e:
            print(type(e))
            print('-Selected instrument not a DC supply-')       # the dc supply does not recognise the voltage read command

    def disable_inputs(self, window, disabled):           # disable all inputs
        for tab in self.tabs:
            for supply in self.addr:               
                for i in range(4):
                    for j in range(2):               
                        window['_' + str(tab) + '_' + str(supply)
                                + '_' + str(j) + '_' + str(i) + '_'].update(disabled=disabled) 

    def get_rf_inputs(self, values):
        self.RFinputs = {}
        print(self.cur_tab)
        if str(self.cur_tab) == 'pwr':
            self.RFinputs['freq'] = float(values['_pwr_RF0_0_'])
            self.RFinputs['start'] = float(values['_pwr_RF0_1_'])
            self.RFinputs['stop'] = float(values['_pwr_RF0_2_'])
            self.RFinputs['step'] = float(values['_pwr_RF0_3_'])
        if  str(self.cur_tab) == 'freq':
            self.RFinputs['start'] = float(values['_freq_RF0_0_'])
            self.RFinputs['stop'] = float(values['_freq_RF0_1_'])
            self.RFinputs['step'] = float(values['_freq_RF0_2_'])
            self.RFinputs['level'] = float(values['_freq_RF0_3_'])
        print(self.RFinputs)
        return self.RFinputs
    
    def rf_input_check(self, values):
        if self.cur_tab == 'pwr':
            try:
                freq = float(values['_pwr_RF0_0_'])
                pwr_start = float(values['_pwr_RF0_1_'])
                pwr_stop = float(values['_pwr_RF0_2_'])
                pwr_step = float(values['_pwr_RF0_3_'])
                if  0.1 <= freq <= 30 and (100*freq)%1 == 0:                           
                    print('OK Frequency')
                else:
                    print('Invalid freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if -80 <= pwr_start <= 30 and (10*pwr_start)%1 == 0:                     
                    print('OK start')
                else:
                    print('Invalid start RF power, please use any value from -80 - 30 dBm in steps of 0.1')
                    return 0
                if -80 <= pwr_stop <= 30 and (10*pwr_stop)%1 == 0:
                    print('OK stop')
                else:
                    print('Invalid stop RF power, please use any value from -80 - 30 dBm')
                    return 0
                if pwr_start < pwr_step:
                    print('OK start and stop')
                else:
                    print('Power stop must be greater than power start')
                    return 0
                if 0.01 <= pwr_step <= 10 and (100*pwr_step)%1 == 0:
                    print('OK step')
                else:
                    print('invalid Step value, please use any value from 0.01-10.0 dB in steps of 0.01')
                    return 0
                print('RF power sweep parameters OK')
                return 1
            except Exception as e:
                print(type(e))
                print('-unable to recognise power sweep RF parameters please check-')
                return 0
        elif self.cur_tab == 'freq':
            try:
                freq_start = float(values['_freq_RF0_0_'])
                freq_stop = float(values['_freq_RF0_1_'])
                freq_step = float(values['_freq_RF0_2_'])
                pwr_level = float(values['_freq_RF0_3_'])

                if  0.1 <= freq_start <= 30 and (100*freq_start)%1 == 0:                           
                    print('OK Start Frequency')
                else:
                    print('Invalid start freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if  0.1 <= freq_stop <= 30 and (100*freq_stop)%1 == 0:                           
                    print('OK Stop Frequency')
                else:
                    print('Invalid stop freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                print(freq_start)
                print(freq_stop)
                print(freq_start < freq_step)
                if freq_start < freq_stop:
                    print('OK Stop and Start Frequency')
                else:
                    print('Frequency stop must be greater than frequency start')
                    return 0
                if 0.01 <= freq_step <= 4 and (100*freq_step)%1 == 0:
                    print('OK frequency step')
                else:
                    print('invalid step value, please use any value from 0.01-4.0 GHz in steps of 0.01')
                    return 0
                if -80 <= pwr_level <= 30 and (10*pwr_level)%1 == 0:
                    print('OK power level')
                else:
                    print('Invalid power level, please use any value from -80 - 30 dBm in steps of 0.01')
                print('RF frequency sweep parameters OK')
                return 1
            except Exception as e:
                print(type(e))
                print('-unable to recognise frequency sweep RF parameters please check-')

class InstrControl(ManageInputs):

    def __init__(self):
        self.chs = InstrConnect.chs
        self.addr = InstrConnect.addr
        self.rfaddr = InstrConnect.rfaddr
        self.DCinputs = ManageInputs.DCinputs
        self.RFinputs = ManageInputs.RFinputs

    def update_drain_values(self):   # updates both dc current and voltage on the supply
        for supply in self.chs:             # for all supplies
            if 'DC1' != str(supply):        # not gate supply
                for i in range(self.chs[supply]):  # for all channels
                    try:
                        dc_supply = rm.open_resource(self.addr[supply])
                    except Exception as e:
                        print(type(e))
                        print('DC supply could not be opened')
                    try:
                        voltage = float(self.DCinputs[supply][i][0])
                        dc_supply.write('V' + str(i+1) + ' ' + str(voltage)) # sends voltage setting, most dc supplies accept this command syntax
                        print('Voltage SET on channel ' + str(i+1))
                        time.sleep(0.1)
                    except Exception as e: 
                        print(type(e))
                        print('-voltage setting not recognized-')
                        return 1
                    try:
                        current = float(self.DCinputs[supply][i][1])
                        dc_supply.write('I' + str(i+1) + ' ' + str(current))
                        print('Current lim set on channel ' + str(i+1))
                        time.sleep(0.1)
                    except Exception as e: 
                        print(type(e))
                        print('-current setting not recognized-')
                        return 1
                    print('DC drain values updated')

    def update_gate_values(self, rm):
        supply = 'DC1'  # gate supply
        for i in range(self.chs[supply]):  # for all channels
            try:
                dc_supply = rm.open_resource(self.addr[supply])
            except Exception as e:
                print(type(e))
                print('DC supply could not be opened')
                return False
            try:
                voltage = float(self.DCinputs[supply][i][0])
                dc_supply.write('V' + str(i+1) + ' ' + str(voltage)) # sends voltage setting, most dc supplies accept this command syntax from what I have seen
                print('Voltage SET on channel ' + str(i+1))
                time.sleep(0.1)
            except Exception as e: 
                print(type(e))
                print('-voltage setting not recognized-')
                return False
            try:
                current = float(self.DCinputs[supply][i][1])
                dc_supply.write('I' + str(i+1) + ' ' + str(current)) # sends current setting
                print('Current lim set on channel ' + str(i+1))
                time.sleep(0.1)
            except Exception as e: 
                print(type(e))
                print('-current setting not recognized-')
                return False
            print('DC gate values updated')
            return True

    def con_dc_sup(self):   # generates resource for all dc supplies 
        dc_supplies = {}
        try:
            for supply in self.addr:  
                if self.addr[supply] != '':
                    print('opening instrument ' + str(supply))
                    dc_supplies[supply] = rm.open_resource(self.addr[supply])
                    print('connection successful')
        except Exception as e: 
            print(type(e))
            print('Connection to ' + str(InstrConnect.get_name(supply)) + ' failed')
            return False
        return dc_supplies   

    def find_quiescent(self):
        vg_init = 5
        InstrControl.update_drain_values(type='G')
        dc_sup = self.con_dc_sup()
        val = self.update_gate_values()
        tgl = tgl_gate_chs(self.chs, dc_sup)
        if dc_sup & val & tgl:
            for chs in range() 
            if tgl_drain_chs(self.chs, dc_sup):
                for i in range(self.chs['DC1']):
                    found, k = False, 1
                    while not(found):
                        gate_voltage = vg_init-k*0.02
                        dc_sup['DC1'].write('V' + str(i+1) + ' ' + str(gate_voltage))
                forcvxc
                    

                        



    def power_sweep(self):  # starts power sweep when start button is pressed
        complete = False 
        instr_out_data = {}   # create all channel data lists
        for supply in self.chs:    # for all supplies
            channels = {}
            for ch in range(self.chs[supply]):       # for all channels
                channels[ch+1] = []
                #print(channels)
            instr_out_data[supply] = channels 
            #print(instr_out_data)
        rfin = {'pwr':[]}
        rfout = {'pwr':[]}
        instr_out_data['rf_in'] = rfin
        instr_out_data['rf_out'] = rfout
        #print(instr_out_data)   

        try:  # connects to the rf supply if it is not already connected
            rf_supply = rm.open_resource(self.rfaddr['RF1']) 
        except Exception as e:                            
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1   # exits function if rf supply is not connected
        dc_supplies = self.con_dc_sup()
        if dc_supplies == False:
            print('Connection to DC supplies failed, sweep failed')
            return 1
        tgl_drain_chs(self.chs, dc_supplies)
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('SOURce1:FREQuency:CW ' + str(self.rf_inputs['freq']) + ' GHz')
        rf_supply.write('SOURce1:SWEep:POWer:MODE MANual')
        rf_supply.write('SOURce1:POWer:STARt ' + str(self.rf_inputs['start']) + ' dBm')
        rf_supply.write('SOURce1:POWer:STOP ' + str(self.rf_inputs['stop']) + ' dBm')
        rf_supply.write('SOURce1:POWer:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:POWer:STEP ' + str(self.rf_inputs['step']))
        while complete == False:
            # I need to check for some kind of interupt here during the sweep
            time.sleep(0.2)
            try:
                current_rf_power = float(rf_supply.query('SOURce1:POWer:POWer?')) 
            except Exception as e:
                current_rf_power = '-'
            instr_out_data['rf_in']['pwr'].append(current_rf_power) # append current rf power
            print('current rf power = ' + str(current_rf_power))
            instr_out_data = read_dc_values(self.chs, dc_supplies, instr_out_data)
            rf_supply.write('SOURce1:POWer:MANual UP')
            if current_rf_power >= self.rf_inputs['stop']:       # check whether sweep is complete
                complete = True
        rf_supply.write('OUTPut:ALL:STATe 0')   # turn off RF
        tgl_drain_chs(self.chs, dc_supplies, enabled=0)
        print('RF Power Sweep Complete')
        #print(instr_out_data)
        flat_data = flatten_data(instr_out_data, 'pwr')
        print(flat_data)
        if flat_data == 'nul':
            print('Export unsuccesful, data manipulation error ')
            return 1
        else:  
            print('Data flatten succesful')
        #out_data = pae_calculation(flat_data)
        if export_to_csv(flat_data) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccesful, data manipulation error ')
        return 0 

         

    def freq_sweep(self):
        complete = False
        instr_out_data = {}   # create all channel data lists
        dc_supplies = {}
        for supply in self.chs:    # for all supplies
            channels = {}
            for ch in range(self.chs[supply]):       # for all channels
                channels[ch+1] = []
                #print(channels)
            instr_out_data[supply] = channels 
            #print(instr_out_data)
        rfin = {'freq':[]}
        rfout = {'pwr':[]}
        instr_out_data['rf_in'] = rfin
        instr_out_data['rf_out'] = rfout
        #print(instr_out_data)   

        try:  # creates rf resource
            rf_supply = rm.open_resource(self.rfaddr['RF1']) 
        except Exception as e:                            
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1   # exits function if rf supply is not connected
        try:    # creates dc resources
            for supply in self.addr:  
                if self.addr[supply] != '':
                    print('opening instrument ' + str(supply))
                    dc_supplies[supply] = rm.open_resource(self.addr[supply])
                    print('connection successful')
        except Exception as e: 
            print(type(e))
            print('Connection to ' + str(InstrConnect.get_name(supply)) + ' failed')
        print(self.rf_inputs)
        tgl_drain_chs(self.chs, dc_supplies)
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('SOURce1:SWEep:FREQuency:MODE MANual')
        rf_supply.write('SOURce1:FREQuency:STARt ' + str(self.rf_inputs['start']) + ' GHz')
        rf_supply.write('SOURce1:FREQuency:STOP ' + str(self.rf_inputs['stop']) + ' GHz')
        rf_supply.write('SOURce1:FREQuency:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:FREQuency:STEP:LINear ' + str(self.rf_inputs['step']) + ' GHz')

        while complete == False:
            time.sleep(0.2)
            try:
                current_rf_freq = float(rf_supply.query('SOURce1:FREQ:FREQ?'))
            except Exception as e:
                current_rf_freq = '-'
            instr_out_data['rf_in']['freq'].append(current_rf_freq)
            print('current rf freq = ' + str(current_rf_freq))
            instr_out_data = read_dc_values(self.chs, dc_supplies, instr_out_data)
            rf_supply.write('SOURce1:FREQuency:MANual UP')
            if current_rf_freq >= self.rf_inputs['stop']*(1_000_000_000):       # check whether sweep is complete
                complete = True
        rf_supply.write('OUTPut:ALL:STATe 0')   # turn off RF
        tgl_drain_chs(self.chs, dc_supplies, enabled=0)
        print('RF Frequency Sweep Complete')
        #print(instr_out_data)
        flat_data = flatten_data(instr_out_data, 'freq')
        print(flat_data)
        if flat_data == 'nul':
            print('Export unsuccesful, data manipulation error ')
            return 1
        else:  
            print('Data flatten succesful')
        #instr_out_data = pae_calculation(flat)
        if export_to_csv(flat_data) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccesful, export error ')
        return 0 

    def test_supplies(self): # turns on all dc channels for 1 second
        try:
            dc_supplies = {}
            for supply in self.addr:  # connects to the dc supply if it is not already connected
                if self.addr[supply] != '':
                    print('opening instrument ' + str(supply))
                    dc_supplies[supply] = rm.open_resource(self.addr[supply])
            tgl_drain_chs(dc_supplies)
            time.sleep(1)
            tgl_drain_chs(dc_supplies, enabled=0)
        except Exception as e:
            print(type(e))
            return 0
        print('error turning on channels')

if __name__ == '__main__':

    frqsuff = ['Hz', 'kHz', 'MHz', 'GHz']
    default_folder = 'C:/Users/AndrewThomas/OneDrive - ' + \
        'CSA Catapult/Documents/Equipment VISA Integration/RF sweep data'
    folder = []
    gate_control = False
    # standard theme colour
    sg.theme('DarkBlue4')
    BG = BuildGui(window=None)
    setup_col_1 = [[sg.Button('Search Instruments', key='_INSTR.SEARCH_',
                              font='bold 11', button_color='Gray58')],
                   [sg.Table(size=(80,1), values=[['','','','']],
                             headings=['Instrument ID', 'VISA Address',
                                       'Channels', 'Instrument Function'],
                             max_col_width=25, text_color='black',
                             background_color='White', auto_size_columns=True,
                             display_row_numbers=False, justification='r',
                             num_rows=3, key='_INSTR.TABLE_', row_height=25,
                             enable_events=True,
                             select_mode=sg.TABLE_SELECT_MODE_BROWSE)]]

    setup_layout = [
        [sg.Col(setup_col_1)], [sg.HorizontalSeparator(key='_SEP.1_')],
        [sg.Text('Select instrument from table and assign functionality:',
                 font='bold 12'), sg.Push()],
        [sg.Text('Instrument ID:', size=(20,1), font='bold 11'),
         sg.Input(size=(28,1), disabled=True, key='_SLCT.INSTR_'),
         sg.Push()],
        [sg.Text('Instrument functionality:', size=(20,1), font='bold 11'),
         sg.OptionMenu(values=InstrConnect.name.keys(),
                       key='_INSTR.FUNC_'),
         sg.Push()],
        [sg.Col([[sg.Button('Update Instrument', key='_UPDATE.INSTR_',
                   font='bold 11', button_color='Gray58')]]),
         sg.Push()],
        [sg.HorizontalSeparator(key='_SEP.2_')],
        [sg.Col([[sg.Text('Sweep mode:', font='bold 12'), sg.Push()],
        [sg.Radio('Power Sweep', 'Sweep', default=True,
                           enable_events=True, key='_PWR.SWEEP_',
                           font='bold 11')],
        [sg.Radio('Frequency Sweep', 'Sweep', default=False,
                  enable_events=True, key='_FRQ.SWEEP_', font='bold 11')],
        [sg.Radio('Power & Frequency Sweep', 'Sweep', default=False,
                  enable_events=True, key='_PRF.SWEEP_', font='bold 11')]], justification='left'),
         sg.Col([[sg.Text('Sweep options:', font='bold 12')],
         [sg.Checkbox('Find quiescent current', default=True, k='_FINDQCUR_')]], vertical_alignment='top'),
         sg.Col([[sg.Text('CH' + str(i+1), s=(1,1), s=(5, 1), p=(2,0),
                  font='bold 10', justification='l')
                  for i in range(4)],
                [sg.InputText('1', size=(6, 1), disabled=True, 
                  k=('_SETUP_QC' + str(i + 1))) for i in range(4)]], vertical_alignment='top', p=(0,2))],
        [sg.HorizontalSeparator(key='_SEP.3_')],
        [sg.Text('Select export options:', font='bold 12'), sg.Push()], 
        [sg.Col([[sg.Button('Open Folder'),
             sg.Push(), sg.Text('Save in: ' + str(default_folder), justification='r', key='_FOLDER_')]]),
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

    freq_layout = [
        [sg.Text('Select frequency sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name('freq')],   
        [BG.rf_supply_col_inputs('freq', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 1: (gate only)', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 2: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 3: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq')],
        [sg.Button('Ok', pad=(5,2), key='_OKF_'),
         sg.Push(),
         sg.Button('Find Quiescent Current', p=(5,2), key ='_FINDQC_P_'),
         sg.Button('Gate OFF', p=(5,2), key='_GATEF_', button_color='red'),
         sg.Button('START',  p=(5,2), key='_STARTF_')], 
        ]

    pwr_layout = [
        [sg.Text('Select power sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name('pwr')],
        [BG.rf_supply_col_inputs('pwr', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 1: (gate only)', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 2: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 3: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr')],
        [sg.Button('Ok', pad=(5,2), key='_OKP_'),
         sg.Push(),
         sg.Button('Find Quiescent Current', p=(5,2), key ='_FINDQC_F_'),
         sg.Button('Gate OFF', p=(5,2), key='_GATEP_', button_color='red'),
         sg.Button('START',  p=(5,2), key='_STARTP_')], 
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
        sg.Tab('Frequency Sweep', freq_layout, visible=False, key='_FRQ.TAB_'),
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
    IC = InstrConnect(rm)
    BG.sep_colour('_SEP.1_','SlateBlue3')
    BG.sep_colour('_SEP.2_','SlateBlue3')
    BG.sep_colour('_SEP.3_','SlateBlue3')

    gate_control = False

    while True: 
        event, values = window.read()  
        print(datetime.datetime.now())
        MI = ManageInputs()
        IK = InstrControl()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        # if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):  # enable to show all key values
        #     print('============ Event = ', event, ' ==============')
        #     print('-------- Values Dictionary (key=value) --------')
        #     for key in values:
        #          print(key, ' = ',values[key])

        if event == '_INSTR.SEARCH_':
            window['_INSTR.TABLE_'].update(values=[['','','','']])
            connected = IC.instr_check(rm)
            window['_INSTR.TABLE_'].update(values=connected)
            
            if len(connected) == 0:
                sg.popup_error(f'No connected instruments detected. Ensure '
                               'instrument connected and search again.')

        elif event == '_UPDATE.INSTR_':
            if values['_SLCT.INSTR_'] != '' and values['_INSTR.FUNC_'] != '':
                device_type =  MI.table_update(window)
                if device_type == 'DC Power Supply':
                    try:
                        MI.enable_channel_inputs(window)
                    except:
                        print('Channel enable failed')
                elif device_type == 'Vector Signal Generator':
                    None
            else:
                sg.popup_error(f'Make sure instrument and functionality '
                                'both selected in order to update table.')
        
        elif event == '_INSTR.TABLE_':
            try:
                rowselected = [connected[row] for row in values[event]]
                instrselected = rowselected[0][0]
                window['_SLCT.INSTR_'].update(instrselected)
            except:
                pass
     
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
            else: sg.popup('Folder is invalid', keep_on_top=True)

        elif event == '_OKF_' or event == '_OKP_':                                           
            print('-------- OK (power tab) --------')                                                               
            try:
                if MI.dc_input_check(values) == True:
                    if MI.rf_input_check(values) == True:
                        MI.get_dc_inputs(values)
                        MI.get_rf_inputs(values)
                        IK.update_drain_values()
                    else:
                        print('RF signal generator input is invalid')
                else:
                    print('DC supply input is invalid')
            except Exception as e:
                print(type(e))
                print('Instrument connect not completed')

        elif event == '_FINDQC_P_' or event == '_FINDQC_F_':
            print('-------- Find Quiescent Current --------')
            try:
                if MI.dc_input_check(values) == True:
                    IK.find_quiescent(rm)
                else:
                    print('Cannot start sweep DC input is invalid')
            except Exception as e:
                print(type(e))
                print('Power sweep start error')


        elif event == '_GATEP_' or event == '_GATEF_':
            gate_control = not(gate_control)
            active = gate_button_update(gate_control, window)
            print('-------- Gate Turned ' + str(active) + ' --------')

        elif event == '_STARTP_' or event == '_STARTF_':
            print('-------- START Sweep --------')
             # toggle_inputs(window, enabled=0)            # might be needed to avoid errors
            try:
                if MI.dc_input_check(values) == True:
                    if MI.rf_input_check(values) == True:
                        MI.get_dc_inputs(values)
                        MI.get_rf_inputs(values)
                        if event == '_STARTP_':
                            IK.power_sweep()
                        elif event == '_STARTF_':
                            IK.freq_sweep()
                    else:
                        print('Cannot start sweep RF is invalid')
                else:
                    print('Cannot start sweep DC input is invalid')
            except Exception as e:
                print(type(e))
                print('Power sweep start error')

    window.close()
