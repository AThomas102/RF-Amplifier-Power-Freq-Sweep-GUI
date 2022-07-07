# 
# ---------------------- RF SWEEP GUI ----------------------
# An instrument GUI designed for automatic RF amplifier testing,
# by safe turn on of device at 5v then finding quiescent voltage
# then stepping through RF supply input frequency and power then 
# of pae and export to csv.
# General instrument check and assignment functions means furthur
# device test procedures can be easily developed on differant tabs. 
# Currently only tested for SMW200A Signal Generator, but can be
# easily used for alternative generators by changing the serial
# visa commands to compatible ones. These can be found in the 
# respective instrument manual.
# VISA: https://pyvisa.readthedocs.io/en/1.5-docs/index.html
# PySimpleGUI: https://pysimplegui.readthedocs.io/en/latest/
# instruments:
# https://resources.aimtti.com/manuals/CPX400DP_Instruction_Manual-Iss1.pdf
# https://www.rohde-schwarz.com/webhelp/SMW_HTML_UserManual_en/Content/welcome_page.htm
# https://www.rohde-schwarz.com/webhelp/NRPxxSN_HTML_UserManual_en/Content/welcome.htm
#
# ------------------------- notes --------------------------    
# Optimizing current functionality is recommended 
# before implementing furthur capabilities. 
# e.g generalized sweep function, standard visa commands only..
# used imports:
import PySimpleGUI as sg
import pandas as pd
import pyvisa as visa
import os
import time
import datetime

# pad the flattened data columns for csv export
def pad_dict_list(dict_list, padel):
        lmax = 0
        for lname in dict_list.keys():
            lmax = max(lmax, len(dict_list[lname]))
        for lname in dict_list.keys():
            ll = len(dict_list[lname])
            if  ll < lmax:
                dict_list[lname] += [padel] * (lmax - ll)
        return dict_list

# returns length of decimal
def dec_count(num):
    string = str(num)
    if "." in string:
        return len(string.split(".")[1].rstrip("0"))
    else:
        return 0

# returns title filestring for export
def get_title(rfinputs):
        try:
            name_dic = []
            file_string = ''
            date = datetime.datetime.now().strftime('%d_%m_%Y')
            time = datetime.datetime.now().strftime('%H-%M-%S')
   
            if values['_DATE_'] == True:
                name_dic.append(date)
            if values['_TIME_'] == True:
                name_dic.append(time)
            if cur_tab == 'pwr':
                cwfreq = str(rfinputs['freq'])
                name_dic.append(cwfreq)
                if values['_SSP_'] == True:
                    pstart = str(rfinputs['pstart'])
                    pstop = str(rfinputs['pstop'])
                    name_dic.append(pstart)
                    name_dic.append(pstop)
            if cur_tab == 'freq':
                level = str(rfinputs['level'])
                name_dic.append(level)
                if values['_SSF_'] == True:
                    fstart = str(rfinputs['fstart'])
                    fstop = str(rfinputs['fstop'])
                    name_dic.append(fstart)
                    name_dic.append(fstop)
            if cur_tab == 'pwrfreq':
                if values['_SSP_'] == True:
                    pstart = str(rfinputs['pstart'])
                    pstop = str(rfinputs['pstop'])
                    name_dic.append(pstart)
                    name_dic.append(pstop)
                if values['_SSF_'] == True:
                    fstart = str(rfinputs['fstart'])
                    fstop = str(rfinputs['fstop'])
                    name_dic.append(fstart)
                    name_dic.append(fstop)
            #print(name_dic)
            file_string = '_'.join(name_dic)
        except Exception as e:
            print(type(e))
            print('-file name could not be generated-')
            file_string = 'export data'
        return file_string  

# updates visible sweep tab and other widgets                
def update_tab(tab):
    b1, b2, b3 = False, False, False
    if tab == '_PWR.SWEEP_': b1=True
    elif tab == '_FRQ.SWEEP_': b2=True
    elif tab == '_PWRFRQ.SWEEP_': b3=True

    window['_SSF_'].update(disabled=b1)
    window['_SSP_'].update(disabled=b2)

    window['_PWR.TAB_'].update(visible=b1)
    window['_FRQ.TAB_'].update(visible=b2)
    window['_PWRFRQ.TAB_'].update(visible=b3)
    return cur_tab

# simply updates gate button widgets
def gate_button_update(gate_control):
    if gate_control: 
        active = 'ON'
        window['_GATEP_'].update('Gate ON', button_color='green')
        window['_GATEF_'].update('Gate ON', button_color='green')
        window['_GATEPF_'].update('Gate ON', button_color='green')
    else: 
        active = 'OFF'
        window['_GATEP_'].update('Gate OFF', button_color='red')
        window['_GATEF_'].update('Gate OFF', button_color='red')
        window['_GATEPF_'].update('Gate OFF', button_color='red')
    return active

# queries all available visa instrument resources with 
# idn command and checks dc supplies for number of channels.
def instr_check():
    connected = []
    names = []
    instrlist = rm.list_resources()
    time.sleep(0.1) # give the resource manager time
    
    print(instrlist)
    for addr in instrlist:
        channels = '-'
        idn = []
        try:
            rsrc = rm.open_resource(addr)
            rsrc.timeout = 250
            idn = rsrc.query('*IDN?').strip()
            for ch in range(4): # check for number of channels
                value = rsrc.query('V' + str(ch+1) + 'O?')   
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

# updates quiescent current table visibility
def tog_qcur(visible=False):
    for ch in range(4):
        window['_SETUP_QC' + str(ch+1)].update(visible=visible)
        window['_TEXT_QC' + str(ch+1)].update(visible=visible)
    window['_FINDQC_P_'].update(visible=visible)
    window['_FINDQC_F_'].update(visible=visible)
    window['_FINDQC_PF_'].update(visible=visible)    

# calculates power added efficiency from the instrument measurements and users in/out feed losses
def pae_calculation(in_data, in_loss, out_loss, level='-'): 
    out_data = in_data
    out_data['pae'] = []
    for reading in range(len(in_data['DC1'][1])):
        sup_pwrs = []
        for instr in in_data:
            if 'DC' in instr and 'DC1' != instr:
                ch_pwrs = []
                for ch in in_data[instr]: # all ch powers into channel list
                    measurement = in_data[instr][ch][reading]
                    current = strip_reading(measurement[0])     
                    voltage = strip_reading(measurement[1])
                    try:
                        ch_pwr = float(current) * float(voltage)
                    except:
                        ch_pwr = '-'
                    ch_pwrs.append(ch_pwr)
                sup_pwrs.append(sum(ch_pwrs)) # all channel powers in supply list
        total_dc_pwr = sum(sup_pwrs)    # all supply powers into drain total
        try:
            if 'pwr' in in_data['rf_in']:
                rf_in_dbm = float(in_data['rf_in']['pwr'][reading])
            else:
                rf_in_dbm = level
        except:
            rf_in_dbm = '-'
        try:
            rf_out_dbm = float(in_data['rf_out']['pwr'][reading])
        except:
            rf_out_dbm = '-'
        try:
            real_rf_in = 0.001*(10**((rf_in_dbm - float(in_loss))/10))
            real_rf_out = 0.001*(10**((rf_out_dbm + float(out_loss))/10))
            # print(real_rf_out)
            # print(real_rf_in)
            # print(total_dc_pwr)
            pae = 100*(real_rf_out - real_rf_in)/total_dc_pwr
        except Exception as e:
            print(type(e))
            pae = '-'
        out_data['pae'].append(pae)
    return out_data

# flattens data dic for excel export
def flatten_data(export_data, inloss, outloss):
    try:
        flat_data = {}
        try:
            if export_data['rf_in']['pwr']:
                flat_data['rf IN power (dBm)'] = []
                flat_data['rf AMP IN power (dBm)'] = []
                for i in range(len(export_data['rf_in']['pwr'])):
                    val = float(export_data['rf_in']['pwr'][i])
                    flat_data['rf IN power (dBm)'].append(val)  # adds data for rf vector supply
                    flat_data['rf AMP IN power (dBm)'].append(val - float(inloss))
        except:
            pass
        try:
            flat_data['rf IN freq (Hz)'] = export_data['rf_in']['freq']  # adds data for rf vector supply
        except:
            pass
        try:
            if export_data['rf_out']['pwr']:
                flat_data['rf OUT power (dBm)'] = []
                flat_data['rf AMP OUT power (dBm)'] = []
                for j in range(len(export_data['rf_out']['pwr'])):
                    val = float(export_data['rf_out']['pwr'][j])
                    flat_data['rf OUT power (dBm)'].append(val)
                    flat_data['rf AMP OUT power (dBm)'].append(val + float(outloss))
        except:
            pass
        for instr in export_data:             # adds data for dc supplies
            if 'DC' in instr:
                if 'DC1' in instr: type = 'Gate'
                else: type = ''
                for ch in export_data[instr]:
                    flat_data[str(instr) + ' ' + type + ', Channel ' + str(ch) + ' Voltage (V)'] = []
                    flat_data[str(instr) + ' ' + type + ', Channel ' + str(ch) + ' Current (A)'] = []
                    for measurement in export_data[instr][ch]:
                        voltage = strip_reading(measurement[0])
                        current = strip_reading(measurement[1])
                        flat_data[str(instr) + ' ' + type + ', Channel ' 
                        + str(ch) + ' Current (A)'].append(current)
                        flat_data[str(instr) + ' ' + type + ', Channel ' 
                        + str(ch) + ' Voltage (V)'].append(voltage)
                        
        #print(flat_data.keys())
        try:
            flat_data['Power Added Efficiency (%)'] = export_data['pae']
        except:
            pass
        flat_data = pad_dict_list(flat_data, '-')
        return flat_data
    except Exception as e:
        print(type(e))
        return 'nul'

# returns full name from supply dic
def get_name(val):
        try:
            for key, value in names.items():
                if val == value:
                    return key
        except:
            return 'None'

# NPR40S power sensor will only respond to this query above -50 dBm threshold
def read_power_sensor(rf_sens, instr_out_data):
    try:
        rf_sens.write('*TRG')
        rf_sens.write('FETCh?')
        result = str(rf_sens.read_raw())
        pwr_lvl = result[2:len(result)-3]    # strip the byte
    except Exception as e:
        print(type(e))
        # restart device
        rf_sens.write('*RST')
        rf_sens.write('UNIT:POW DBM')
        rf_sens.write('INITiate:CONTinuous ON')
        pwr_lvl = '-'
    print('supply RF2, rf OUT = ' + pwr_lvl + ' dBm')
    instr_out_data['rf_out']['pwr'].append(pwr_lvl)
    return instr_out_data

# reads a given channel and supply
def read_chanl_current(dc_supplies, supply, ch):
    current = 0
    try:
        current = dc_supplies[supply].query('I' + str(ch) + 'O?')
        current = strip_reading(current)    
    except Exception as e:
        print(type(e))
        return '-'
    return current

# gets the data for all dc devices 
def read_dc_supplies(dc_supplies, data_out): 
    for supply in dc_supplies:
        for i in range(dcchs[supply]): 
            try: 
                ocp = dc_supplies[supply].query('OP' + str(i+1) + '?')
            except:
                ocp = '-'
            if ocp == '1':   
                print('Over current reached, ' + 
                        str(supply) + ', channel ' + str(i+1) + ' is disabled')
            try:
                current = dc_supplies[supply].query('I' + str(i+1) + 'O?')    # this command is for the CPX400DP power supply
            except Exception as e:
                print(type(e))
                current = '-'
            try:
                voltage = dc_supplies[supply].query('V' + str(i+1) + 'O?')
            except Exception as e:
                print(type(e))
                voltage = '-'
            try:
                current_values = voltage, current
                data_out[supply][i+1].append(current_values)     
            except Exception as e:
                print(type(e))
                current_values = '-','-'
                data_out[supply][i+1].append(current_values)
            print('supply ' + str(supply) + ', channel: ' + str(i+1) + \
                ', V = ', str(voltage.strip()),', I = ', str(current.strip()))         
    return data_out

# strips a measurement reading of characters and blank space
def strip_reading(value):
    translation_table = dict.fromkeys(map(ord, 'VA'), None)     # add units/characters to remove 
    # out = measurement[0].strip().translate(translation_table)
    out = value.strip().translate(translation_table)
    return out
    
def export_to_csv(flat_data, rfinputs):
    try:
        df = pd.DataFrame(flat_data, columns=flat_data.keys())
        dt_string = get_title(rfinputs)
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

# class only for building and updating gui widgets
class BuildGui:

    def __init__(self):
        self.supply_idx = {'pwr':0,'freq':0, 'pwrfreq':0}
        self.rfsupply_col_names = {'pwr':['Freq (GHz):', 'Start (dBm):', 'Stop (dBm):', 'Step (dB):', 'Step Time (s)'],'freq':['Level (dBm):', 'Start Freq (GHz):', 'Stop Freq (GHz):', 'Step Freq (GHz):', 'Step Time (s)'], 'pwrfreq':['Start Freq (GHz):', 'Stop Freq (GHz):', 'Step Freq (GHz):', 'Start Power (dBm):', 'Stop Power (dBm):', 'Step Power (dBm):', 'Step Time (s)']}
        self.dcsupply_col_names = ['Volts(V) 1/2:', 'Cur Lim(A) 1/2:',
                                   'Volts(V) 3/4:', 'Cur Lim(A) 3/4:']
        self.default_rf_inputs = {'pwr':['0.5', '-20', '-10', '2', '2'], 'freq':['-10', '0.1', '1', '0.2', '1'], 'pwrfreq':['17', '21', '1', '0', '10', '2', '1']}

    # change separator colour
    def sep_colour(self, sepname, sepcolour):
        style_name = sepname + 'Line.TSeparator'
        button_style = sg.ttk.Style()
        button_style.theme_use(window.TtkTheme)
        button_style.configure(style_name, background = sepcolour)
        window[sepname].Widget.configure(style = style_name)

    # power supply column titles
    def power_supply_col_name(self):
        names = [[sg.Text('Channel:', size=(8,1), font='normal 9')] 
                            + [sg.Text(self.dcsupply_col_names[j],
                           size=(12, 1), font='normal 9', justification='l') 
                           for j in range(4)] for i in range(1)]
        pwr_col_names = sg.Col(names, size=(500, 25))
        return pwr_col_names

    # power supply table inputs
    def power_supply_col_inputs(self, tab_name, disabled=True):
        inputs = [[sg.Text(str(i+1) + '/' + str(i+3), size=(8,1), font='normal 9', justification='c')] + 
                            [sg.InputText('0.001', size=(14, 1), font='normal 9', justification='l', disabled=disabled, 
                             k=('_' +  str(tab_name) + '_DC' + str(self.supply_idx[tab_name] + 1)
                              + '_' + str(i) + '_' + str(j) + '_'))
                             for j in range(4)] for i in range(2)]
        self.supply_idx[tab_name] = self.supply_idx[tab_name]+1   # useful for iterating the input keys
        power_col_inputs = sg.Col(inputs, size=(500, 60))
        return power_col_inputs

    # rf supply inputs titles
    def rf_supply_col_name(self, tab_name):
        length = len(self.rfsupply_col_names[tab_name])
        names = [[sg.Text(self.rfsupply_col_names[tab_name][j], size=(16, 1),
                  font='bold 10', justification='l')
                  for j in range(length)] for i in range(1)]
        rf_col_names = sg.Col(names, size=(1200, 25))
        return rf_col_names

    # rf supply table inputs
    def rf_supply_col_inputs(self, tab_name, disabled=True):
        length = len(self.rfsupply_col_names[tab_name])
        inputs = [[sg.InputText(self.default_rf_inputs[tab_name][j], size=(18, 1),
                   justification='l', disabled=disabled,
                    k=('_' +  str(tab_name) + '_RF' + str(i) + '_' + str(j) + '_'))
                   for j in range(length)] for i in range(1)]
        rf_col_inputs = sg.Col(inputs, size=(1200, 30))
        return rf_col_inputs

# for updating/checking user inputs in the sweep tab tables
class ManageInputs:

    tabs = ['pwr','freq','pwrfreq']
    dcinputs = {'DC1':[],'DC2':[],'DC3':[],'DC4':[]}
    rfinputs = {}

    def __init__(self):
        None

    # returns user inputed dc inputs      
    def get_dc_inputs(self):
        try:
            for supply in dcchs:
                if dcchs[supply] > 0:    # get channel 1 voltage & current
                    ch1 = [[round(float(values['_' + cur_tab + '_' + supply + '_0_0_']), 2),
                    round(float(values['_' + cur_tab + '_' + supply + '_0_1_']), 2)]] 
                    self.dcinputs[supply] = ch1                  
                if dcchs[supply] > 1:        # for 2 channel supplies
                    ch2 = [round(float(values['_' + cur_tab + '_' + supply + '_1_0_']), 2),
                    round(float(values['_' + cur_tab + '_' + supply + '_1_1_']), 2)]
                    if ch2 == [0,0]:
                        None
                    self.dcinputs[supply].append(ch2)
                if dcchs[supply] > 2:        # for 3 channel supplies
                    ch3 = [round(float(values['_' + cur_tab + '_' + supply + '_0_2_']), 2),
                    round(float(values['_' + cur_tab + '_' + supply + '_0_3_']), 2)]
                    self.dcinputs[supply].append(ch3)
                if dcchs[supply] > 3:        # for 4 channel supplies
                    ch4 = [round(float(values['_' + cur_tab + '_' + supply + '_1_2_']), 2),
                    round(float(values['_' + cur_tab + '_' + supply + '_1_3_']), 2)]
                    self.dcinputs[supply].append(ch4)
            print(self.dcinputs)
        except Exception as e:
            print(type(e))
            print('cannot read dc values')
        return self.dcinputs 

    # checks user dc inputs against set ranges
    def dc_input_check(self):       
        for supply in self.dcinputs:             # for all supplies
            for i in range(len(self.dcinputs[supply])):  # for all open channels
                if i == 0: print('Checking ' + str(get_name(supply)))
                try:
                    voltage = float(self.dcinputs[supply][i][0])
                    current = float(self.dcinputs[supply][i][1])
                    if  0 <= voltage <= 30 and dec_count(voltage) < 3:                           
                        print('OK Voltage on channel', str(i+1))
                    else:
                        print('-Invalid voltage on channel', str(i+1), 
                            ', please use any value from 0-30 V in steps of 0.01-')
                        return False
                    if  0 <= current <= 5 and dec_count(current) < 3:                           
                        print('OK Current on channel', str(i+1))
                    else:
                        print('-Invalid current on channel', str(i+1), 
                            ', please use any value from 0-5 A in steps of 0.01-')
                        return False
                except Exception as e:
                    print(type(e))
                    print('-please input a valid number value on channel', str(i+1))
                    return False
        for j in range(dcchs['DC1']): 
            try: 
                qcurrent = float(values['_SETUP_QC' + str(j+1)])
                if 0 <= qcurrent <= 1000 and dec_count(qcurrent) == 0:    
                    print('OK quiescent current limit on channel', str(j+1))
                else:
                    print('quiescent current out of range on channel', str(j+1))
                    return False
            except:
                    print('-please input a valid quiescent current value on channel ' + str(j+1) + '-')
                    return False
        return True

    # updates the available instrument table and adds chs and names to dics
    def table_update(self):
        rowselected = []
        rowselected = [connected[row] for row in values['_INSTR.TABLE_']]
        if rowselected != []:
            function = values['_INSTR.FUNC_']
            for i in range(len(connected)):
                if connected[i][3] == function:
                    connected[i][3] = ''
            try:
                prev_name = names[rowselected[0][3]]
                dcaddr[prev_name] = ''
                dcchs[prev_name] = 0
            except:
                pass
            rowselected[0][3] = function
            name = names[function]
            window['_INSTR.TABLE_'].update(values=connected)
            if 'DC Power Supply' in function:
                dcaddr[name] \
                = rowselected[0][1]    # add instr addr to dic
                dcchs[name] \
                = rowselected[0][2]    # add instr chs to dic
                return 'DC Power Supply'
            for type in rf_supply_types:
                if type in function:
                    rfaddr[name] \
                    = rowselected[0][1] # add instr rfaddr to dic
                    return type
        else:
            return False

    # enables correct dc channels for dc supply
    def tog_dc_chs(self):
        #print(dcchs)
        try:    
            for tab in self.tabs:
                for supply in dcchs:
                    for i in range(4):
                        for j in range(2): 
                            window['_' + str(tab) + '_' + str(supply)
                                    + '_' + str(j) + '_' + str(i) + '_'].update(disabled=True)

                for supply in dcchs: 
                    for ch in range(dcchs[supply]):  # reenable available channels
                        j = ch%2
                        if ch>1: i = 2
                        else: i = 0
                        window['_' + str(tab) + '_' + str(supply)
                                + '_' + str(j) + '_' + str(i) + '_'].update(disabled=False) 
                        window['_' + str(tab) + '_' + str(supply)
                                + '_' + str(j) + '_' + str(i+1) + '_'].update(disabled=False) 
                    
        except Exception as e:
            print(type(e))
            print('-Selected instrument not a DC supply-')       # the dc supply does not recognise the voltage read command

    # enables qcur tables matching gate channels
    def tog_qcur_chs(self):
        for i in range(4):
            window['_SETUP_QC' + str(i+1)].update(disabled=True)
        for i in range(dcchs['DC1']):
            window['_SETUP_QC' + str(i+1)].update(disabled=False)

    # 
    def get_rf_inputs(self):
        self.rfinputs = {}
        try:
            if cur_tab == 'pwr':
                self.rfinputs['freq'] = float(values['_pwr_RF0_0_'])
                self.rfinputs['pstart'] = float(values['_pwr_RF0_1_'])
                self.rfinputs['pstop'] = float(values['_pwr_RF0_2_'])
                self.rfinputs['pstep'] = float(values['_pwr_RF0_3_'])
                self.rfinputs['tstep'] = float(values['_pwr_RF0_4_'])
            if  cur_tab == 'freq':
                self.rfinputs['level'] = float(values['_freq_RF0_0_'])
                self.rfinputs['fstart'] = float(values['_freq_RF0_1_'])
                self.rfinputs['fstop'] = float(values['_freq_RF0_2_'])
                self.rfinputs['fstep'] = float(values['_freq_RF0_3_'])
                self.rfinputs['tstep'] = float(values['_freq_RF0_4_'])
            if cur_tab == 'pwrfreq':
                self.rfinputs['fstart'] = float(values['_pwrfreq_RF0_0_'])
                self.rfinputs['fstop'] = float(values['_pwrfreq_RF0_1_'])
                self.rfinputs['fstep'] = float(values['_pwrfreq_RF0_2_'])
                self.rfinputs['pstart'] = float(values['_pwrfreq_RF0_3_'])
                self.rfinputs['pstop'] = float(values['_pwrfreq_RF0_4_'])
                self.rfinputs['pstep'] = float(values['_pwrfreq_RF0_5_'])
                self.rfinputs['tstep'] = float(values['_pwrfreq_RF0_6_'])   
            self.rfinputs['inloss'] = float(values['IN_LOSS'])
            self.rfinputs['outloss'] = float(values['OUT_LOSS'])
        except Exception as e:
            print(type(e))
            print('-rf inputs are not valid numerals-')
            return self.rfinputs
        # print(self.rfinputs)
        return self.rfinputs

    # checks rf inputs are in valid range
    def rf_input_check(self):
        if cur_tab == 'pwr':
            try:
                freq = self.rfinputs['freq']
                pwr_start = self.rfinputs['pstart']
                pwr_stop = self.rfinputs['pstop']
                pwr_step = self.rfinputs['pstep']
                if  0.1 <= freq <= 30 and dec_count(freq) < 3:                           
                    print('OK Frequency')
                else:
                    print('Invalid freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if -80 <= pwr_start <= 30 and dec_count(pwr_start) < 3:                     
                    print('OK start')
                else:
                    print('Invalid start RF power, please use any value from -80 - 30 dBm in steps of 0.1')
                    return 0
                if -80 <= pwr_stop <= 30 and dec_count(pwr_stop) < 3:
                    print('OK stop')
                else:
                    print('Invalid stop RF power, please use any value from -80 - 30 dBm')
                    return 0
                if pwr_start < pwr_stop:
                    print('OK start and stop')
                else:
                    print('Power stop must be greater than power start')
                    return 0
                if 0.01 <= pwr_step <= 10 and dec_count(pwr_step) < 3:
                    print('OK step')
                else:
                    print('invalid Step value, please use any value from 0.01-10.0 dB in steps of 0.01')
                    return 0
            except Exception as e:
                print(type(e))
                print('-unable to recognise power sweep RF parameters please check-')
                return 0

        if cur_tab == 'freq':
            try:
                pwr_level = self.rfinputs['level']
                freq_start = self.rfinputs['fstart']
                freq_stop = self.rfinputs['fstop']
                freq_step = self.rfinputs['fstep']
                if  0.1 <= freq_start <= 30 and dec_count(freq_start) < 3:                           
                    print('OK Start Frequency')
                else:
                    print('Invalid start freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if  0.1 <= freq_stop <= 100 and dec_count(freq_stop) < 3:                           
                    print('OK Stop Frequency')
                else:
                    print('Invalid stop freq, please use any value from 0.1-100 GHz in steps of 0.01')
                    return 0
                if freq_start < freq_stop:
                    print('OK Stop and Start Frequency')
                else:
                    print('Frequency stop must be greater than frequency start')
                    return 0
                if 0.01 <= freq_step <= 4 and dec_count(freq_step) < 3:
                    print('OK frequency step')
                else:
                    print('invalid step value, please use any value from 0.01-4.0 GHz in steps of 0.01')
                    return 0
                if -80 <= pwr_level <= 30 and dec_count(pwr_level) < 3:
                    print('OK power level')
                else:
                    print('Invalid power level, please use any value from -80 - 30 dBm in steps of 0.01')
                    return 0
            except Exception as e:
                print(type(e))
                print('-unable to recognise frequency sweep RF parameters please check-')
                return 0
        if cur_tab == 'pwrfreq':
            try:
                freq_start = self.rfinputs['fstart']
                freq_stop = self.rfinputs['fstop']
                freq_step = self.rfinputs['fstep']
                pwr_start = self.rfinputs['pstart']
                pwr_stop = self.rfinputs['pstop']
                pwr_step = self.rfinputs['pstep']
                if  0.1 <= freq_start <= 30 and dec_count(freq_start) < 3:                           
                    print('OK Start Frequency')
                else:
                    print('Invalid start freq, please use any value from 0.1-30 GHz in steps of 0.01')
                    return 0
                if  0.1 <= freq_stop <= 100 and dec_count(freq_stop) < 3:                           
                    print('OK Stop Frequency')
                else:
                    print('Invalid stop freq, please use any value from 0.1-100 GHz in steps of 0.01')
                    return 0
                if freq_start < freq_stop:
                    print('OK Stop and Start Frequency')
                else:
                    print('Frequency stop must be greater than frequency start')
                    return 0
                if 0.01 <= freq_step <= 4 and dec_count(freq_step) < 3:
                    print('OK frequency step')
                else:
                    print('invalid step value, please use any value from 0.01-4.0 GHz in steps of 0.01')
                    return 0
                if -80 <= pwr_start <= 30 and dec_count(pwr_start) < 3:                     
                    print('OK start')
                else:
                    print('Invalid start RF power, please use any value from -80 - 30 dBm in steps of 0.1')
                    return 0
                if -80 <= pwr_stop <= 30 and dec_count(pwr_stop) < 3:
                    print('OK stop')
                else:
                    print('Invalid stop RF power, please use any value from -80 - 30 dBm')
                    return 0
                if pwr_start < pwr_stop:
                    print('OK start and stop')
                else:
                    print('Power stop must be greater than power start')
                    return 0
                if 0.01 <= pwr_step <= 10 and dec_count(pwr_step) < 3:
                    print('OK step')
                else:
                    print('invalid Step value, please use any value from 0.01-10.0 dB in steps of 0.01')
                    return 0
            except Exception as e:
                print(type(e))
                print('-unable to recognise power/frequency sweep RF parameters please check-')
                return 0
        try:
            time_step = float(self.rfinputs['tstep'])
            if 0.01 <= time_step <= 20 and dec_count(time_step) < 3:
                print('OK', cur_tab, 'time step')
            else:
                print('Invalid time step, please use any value from 0.01 - 20 s in steps of 0.01')
                return 0
            print('RF frequency sweep parameters OK')
        except Exception as e:
            print(type(e))
            print('Invalid time step')
            return 0
        try:
            in_loss = self.rfinputs['inloss'] 
            out_loss = self.rfinputs['outloss'] 
        except Exception as e:
            print(type(e))
            print('Invalid feed values, use 0 if unknown')
            return 0
        return 1

# for instrument control, updates collects instrument data
class InstrControl:

    def __init__(self):
        self.dcinputs = MI.dcinputs
        self.rfinputs = MI.rfinputs
        self.vg_init = 5.00 # quiescent current check start voltage
        self.ig_lim = 0.01
        self.dc_sups = {}

    # updates only the drain dc supplies, does not turn on supply
    def update_drain_values(self):   # updates both dc current and voltage on the supply
        totchs = 0   
        for supply in dcchs:             # for all supplies
            if 'DC1' != str(supply):        # not gate supply
                for i in range(dcchs[supply]):  # for all channels
                    totchs += 1
                    try:
                        dc_supply = rm.open_resource(dcaddr[supply])
                    except Exception as e:
                        print(type(e))
                        print('DC supply could not be opened')
                    try:
                        voltage = float(self.dcinputs[supply][i][0])
                        dc_supply.write('V' + str(i+1) + ' ' + str(voltage)) # sends voltage setting, most dc supplies accept this command syntax
                        print('Voltage SET on channel ' + str(i+1) + ' ' + str(supply))
                        time.sleep(0.1)
                    except Exception as e: 
                        print(type(e))
                        print('-voltage setting not recognized-')
                        return False
                    try:
                        current = float(self.dcinputs[supply][i][1])
                        dc_supply.write('I' + str(i+1) + ' ' + str(current))
                        dc_supply.write('OCP' + str(i+1) + ' ' + str(current))
                        print('Current lim SET on channel ' + str(i+1) + ' ' + str(supply))
                        time.sleep(0.1)
                    except Exception as e: 
                        print(type(e))
                        print('-current setting not recognized-')
                        return False
        if totchs == 0:
            print('-no drain channels available-')
            return False
        print('DC drain supplies updated')
        return True

    # updates only the gate dc supply, does not turn on supply
    def update_gate_values(self, default=False):
        supply = 'DC1'  # gate supply
        if dcchs[supply] == 0:
            print('-no gate channels available-')
            return False
        for i in range(dcchs[supply]):  # for all channels
            try:
                dc_supply = rm.open_resource(dcaddr[supply])
            except Exception as e:
                print(type(e))
                print('DC supply could not be opened')
                return False
            try:
                if default: voltage = self.vg_init
                else: voltage = float(self.dcinputs[supply][i][0])
                dc_supply.write('V' + str(i+1) + ' ' + str(voltage)) # sends voltage setting, most dc supplies accept this command syntax from what I have seen
                print('Voltage SET on channel ' + str(i+1) + ' ' + str(supply))
                time.sleep(0.1)
            except Exception as e: 
                print(type(e))
                print('-voltage setting not recognized-')
                return False
            try:
                if default: current = self.ig_lim
                else: current = float(self.dcinputs[supply][i][1])
                dc_supply.write('I' + str(i+1) + ' ' + str(current)) # sends current setting
                print('Current lim set on channel ' + str(i+1) + ' ' + str(supply))
                time.sleep(0.1)
            except Exception as e: 
                print(type(e))
                print('-current setting not recognized-')
                return False
        print('DC gate supply updated')
        return True

    # generates dc supply resources for sweep 
    def con_dc_sup(self):   
        self.dc_sups = {}
        try:
            for supply in dcaddr:  
                if dcaddr[supply] != '':
                    print('opening instrument', str(supply))
                    self.dc_sups[supply] = rm.open_resource(dcaddr[supply])
        except Exception as e: 
            print(type(e))
            print('Connection to ' + str((supply)) + ' failed')
            return False
        return True   

    # generates rf diode sensor resource for sweep 
    def start_rf_sensor(self):
        print('opening instrument RF2')
        if rfaddr['RF2'] == '':
            print('Diode power sensor not available')
            return True
        try:
            self.rf_sensor = rm.open_resource(rfaddr['RF2'])
            self.rf_sensor.write('*RST')
            self.rf_sensor.write('INITiate:CONTinuous ON')
            self.rf_sensor.write('UNIT:POW DBM')
            units = strip_reading(self.rf_sensor.query('UNIT:POW?'))
            if units != 'DBM':
                print("'UNIT:POW DBM' not recognised")
                return False
            else:
                return True
        except Exception as e:
            print(type(e))
            return False

    # raises or lowers the gate from 5 V, disabling/enabling device, depending on call. 
    # not required if quiescent voltage already found.
    def change_gate_chs(self, enabled=1):
        try:
            for i in range(dcchs['DC1']):
                if enabled: # lower the gate voltage from 5 v to user input
                    voltage = self.dcinputs['DC1'][i][0]
                    self.dc_sups['DC1'].write('V' + str(i+1) + ' ' + str(voltage))
                    return True
                else: # raise the gate voltage to 5 v
                    j = dcchs['DC1'] - i - 1 # start with last channel
                    self.dc_sups['DC1'].write('V' + str(j+1) + ' 5')
                    time.sleep(0.5)
                    result = round(float(strip_reading(self.dc_sups['DC1'].query('V' + str(j+1) + 'O?'))))
                    if result != 5:
                        return False
            return True
        except:
            return False

    # safely toggles drain current up to user value in steps of 5v
    # -a current check could be implemented-
    def tgl_drain_chs(self, enabled=1):
        step = 5.00    # voltage increase step
        try:
            for supply in self.dc_sups:
                if supply != 'DC1':
                    for i in range(dcchs[supply]):
                        if enabled: # turn on sequence
                            input = float(self.dcinputs[supply][i][0])
                            for l in range(0, 6):
                                val = l*step
                                if val > input:
                                    val = input
                                print('setting drain to: ' + str(val) + ' V on channel ' + str(i+1))
                                self.dc_sups[supply].write('V' + str(i+1) + ' ' + str(val))
                                time.sleep(0.2)
                                self.dc_sups[supply].write('OP' + str(i+1) + ' ' + str(1))
                                time.sleep(1)
                                if val == input:
                                    break
                        else:   # turn off
                            j = dcchs[supply] - i - 1    # start with last channel
                            input = float(self.dcinputs[supply][j][0])
                            for k in range(0, 6):
                                val = input-k*step
                                if val <= 0:
                                    val = 0
                                print('setting drain to: ' + str(val) + ' V on channel ' + str(j+1))
                                self.dc_sups[supply].write('V' + str(j+1) + ' ' + str(val))
                                time.sleep(1)
                                if val == 0:
                                    break
                            self.dc_sups[supply].write('OP' + str(j+1) + ' ' + str(0))
                            on = self.dc_sups[supply].query('OP' + str(j+1) + '?')
                            if on == 1: 
                                return False
            return True 
        except:
            return False 

    # toggle on supply gate channels at 5 v   
    def tgl_gate_chs(self, enabled=1):  
        try:
            # print(self.dc_sups)
            for supply in self.dc_sups: # disable all drain channels
                if supply != 'DC1':
                    for i in range(dcchs[supply]):
                            self.dc_sups[supply].write('OP' + str(i+1) + ' ' + str(0))
            for i in range(dcchs['DC1']):
                self.dc_sups['DC1'].write('V' + str(i+1) + ' 5')
                self.dc_sups['DC1'].write('OP' + str(i+1) + ' ' + str(enabled))
                on = self.dc_sups['DC1'].query('OP' + str(i+1) + '?') 
                on = int(strip_reading(on))
                if on == enabled: out = True
                else: out = False
            return out        
        except:
            print('-gate supply toggle error-')
            return False

    # safe dc supply turn off
    def supply_turn_off(self):
        print('supply turn off started')
        if self.change_gate_chs(enabled=0):
            if self.tgl_drain_chs(enabled=0):
                self.tgl_gate_chs(enabled=0)
            else:
                print('drain turn off error, manual correction required')
        else:
            print('gate raise to 5 V error, manual correction required')

    # finds quiescent current of device by stepping gate voltage down from 5 v
    def find_quiescent(self): 
        try:
            if dcchs['DC1'] == 0 or dcchs['DC2'] == 0:
                print('Please select a supply for DC supply 1 and DC supply 2')
                return False
            if not(self.con_dc_sup()):
                print('unable to connect to dc supplies')
                return False
            elif not(self.update_gate_values(default=True)):
                print('unable to update gate dc supply 1')
                return False
            elif not(self.update_drain_values()):
                print('unable to update drain dc supplies')
                return False
            if not(self.tgl_gate_chs()):
                print('unable to turn on gate dc supply 1')
                return False
            if self.tgl_drain_chs():
                try:
                    for i in range(dcchs['DC1']):
                        cur_lim = round(float(values['_SETUP_QC' + str(i+1)]))/1000
                        if cur_lim == 0:
                            break
                        found = False 
                        k = 1.0
                        inc = 0.2 # initial increment voltage
                        gate_voltage = self.vg_init
                        print('-- testing channel ' + str(i+1) + ' --')
                        while not(found):
                            event, not_used = window.read(timeout=100)
                            if event in stop_events:
                                print('interupt during test, turning off drain dc supplies')
                                self.supply_turn_off()
                                return False
                            gate_voltage = gate_voltage-inc
                            print('setting gate voltage to: ' + str(round(gate_voltage, 2)) + ' V')
                            self.dc_sups['DC1'].write('V' + str(i+1) + ' ' + str(gate_voltage))
                            time.sleep(2)
                            total_current = 0.00
                            for supply in dcchs:
                                if supply != 'DC1':
                                    for j in range(dcchs[supply]):
                                        current = read_chanl_current(self.dc_sups, supply, (j+1))
                                        total_current += float(current)
                            if total_current >= (cur_lim/10):
                                inc = 0.01     # reduce increment after close to quiescent 
                            print("total DC current = " + str(total_current) + " A")
                            if total_current >= cur_lim:
                                s = i%2
                                if i>1: t = 2
                                else: t = 0
                                window['_freq_DC1_' + str(s) + '_' + str(t) + '_'].update(round(gate_voltage, 2))          
                                window['_pwr_DC1_' + str(s) + '_' + str(t) + '_'].update(round(gate_voltage, 2))
                                window['_pwrfreq_DC1_' + str(s) + '_' + str(t) + '_'].update(round(gate_voltage, 2))
                                print('quiescent reached on channel', str(i+1), '=', str(round(gate_voltage, 2)), 'V')
                                found = True
                            if gate_voltage <= 1.0:
                                print('Gate voltage checked down to 1 V, quiescent current could not be found, please try again')
                                self.supply_turn_off()
                                return False
                        time.sleep(1)   # time between tests
                except Exception as e:
                    print(type(e))
                    print('find quiescent current failed') 
                    self.supply_turn_off()
                    return False 
            else:
                print('unable to turn on dc drain supplies')
                self.supply_turn_off()
                return False
        except Exception as e:
            print(type(e))
            print('Find quiescent current unsuccessful')
            return False
        return True

    # rf level sweep, commands might not follow SCPI standards 
    # confirmed functionality for R&S SMW200A vector signal analyzer only            
    def power_sweep(self):  
        complete = False 
        instr_out_data = {}   # create all channel data lists
        self.rfinputs = MI.rfinputs
        freq = self.rfinputs['freq']
        pstart = self.rfinputs['pstart']
        pstop = self.rfinputs['pstop']
        pstep = self.rfinputs['pstep']
        tstep = self.rfinputs['tstep']
        inloss = self.rfinputs['inloss']
        outloss = self.rfinputs['outloss']
        for supply in dcchs:    # for all supplies
            channels = {}
            for ch in range(dcchs[supply]):  # for all channels
                channels[ch+1] = []
            instr_out_data[supply] = channels 
        rfin = {'pwr':[]}
        rfout = {'pwr':[]}
        instr_out_data['rf_in'] = rfin
        instr_out_data['rf_out'] = rfout
        #print(instr_out_data)   

        try:  # creates a resource for rf supply
            print('opening instrument RF1')
            rf_supply = rm.open_resource(rfaddr['RF1']) 
        except Exception as e:                            
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1 
        if self.con_dc_sup() == False:
            print('Connection to DC supplies failed, sweep failed')
            return 1
        if self.start_rf_sensor() == False:
            print('Connection to rf diode sensor failed, sweep failed')
            return 1 
        if not(qcuractive): 
            if self.tgl_gate_chs() == False:
                print('gate turn on failed, sweep failed')
                return 1
            if self.tgl_drain_chs() == False:
                print('drain turn on failed, sweep failed')
                return 1 
            if self.change_gate_chs() == False:
                print('gate change failed, sweep failed')
                return 1
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('TRIGger1:FSWeep:SOURce SINGle')
        rf_supply.write('SOURce1:FREQuency:CW ' + str(freq) + ' GHz')
        rf_supply.write('SOURce1:SWEep:POWer:MODE MANual')
        rf_supply.write('SOURce1:POWer:STARt ' + str(pstart) + ' dBm')
        rf_supply.write('SOURce1:POWer:STOP ' + str(pstop) + ' dBm')
        rf_supply.write('SOURce1:POWer:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:POWer:STEP ' + str(pstep))
        rf_supply.write('SOURce1:SWEep:FREQuency:EXECute')
        time.sleep(1)
        while complete == False:
            event, not_used = window.read(timeout=100)  
            if event in stop_events:
                print('interupt during test, sweep cancelled')
                rf_supply.write('OUTPut:ALL:STATe 0')
                self.supply_turn_off()
                return False
            time.sleep(tstep)
            try:
                current_rf_power = strip_reading(rf_supply.query('SOURce1:POWer:POWer?')) 
            except Exception as e:
                current_rf_power = '999'    # false reading
            instr_out_data['rf_in']['pwr'].append(current_rf_power) # append current rf power
            print('supply RF1, rf IN = ' + str(current_rf_power) + ' dBm')
            if rfaddr['RF2'] != '':
                instr_out_data = read_power_sensor(self.rf_sensor, instr_out_data)
            instr_out_data = read_dc_supplies(self.dc_sups, instr_out_data)
            if float(current_rf_power) >= pstop:       # check whether sweep is complete
                complete = True
            else:
                rf_supply.write('SOURce1:POWer:MANual UP')

        rf_supply.write('OUTPut:ALL:STATe 0')   # turn off RF
        self.supply_turn_off()  # turn off dc
        print('RF Power Sweep Complete')
        # print(instr_out_data)
        instr_out_data = pae_calculation(instr_out_data, inloss, outloss)
        print('PAE calculated and appended')
        flat_data = flatten_data(instr_out_data, inloss, outloss)
        # print(flat_data)
        if flat_data == 'nul':
            print('Export unsuccessful, data manipulation error ')
            return 1
        else:  
            print('Data flatten successful')
        if export_to_csv(flat_data, self.rfinputs) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccessful, export error ')
        return 0  

    # rf freq sweep
    # confirmed functionality for R&S SMW200A vector signal analyzer only   
    def freq_sweep(self):
        complete = False
        instr_out_data = {}   # create all channel data lists
        self.rfinputs = MI.rfinputs
        # print(self.rfinputs)
        level = self.rfinputs['level']
        fstart = self.rfinputs['fstart']
        fstop = self.rfinputs['fstop']
        fstep = self.rfinputs['fstep']
        tstep = self.rfinputs['tstep']
        inloss = self.rfinputs['inloss']
        outloss = self.rfinputs['outloss']
        for supply in dcchs:    
            channels = {}
            for ch in range(dcchs[supply]):       
                channels[ch+1] = []
            instr_out_data[supply] = channels 
        rfin = {'freq':[]}
        rfout = {'pwr':[]}
        instr_out_data['rf_in'] = rfin
        instr_out_data['rf_out'] = rfout
        #print(instr_out_data)   
        try:  
            rf_supply = rm.open_resource(rfaddr['RF1']) 
        except Exception as e:                            
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1   
        if self.con_dc_sup() == False:
            print('Connection to DC supplies failed, sweep failed')
            return 1
        if self.start_rf_sensor() == False:
            print('Connection to rf diode sensor failed, sweep failed')
            return 1 
        if not(qcuractive): 
            if self.tgl_gate_chs() == False:
                print('gate turn on failed, sweep failed')
                return 1
            if self.tgl_drain_chs() == False:
                print('drain turn on failed, sweep failed')
                return 1 
            if self.change_gate_chs() == False:
                print('gate change failed, sweep failed')
                return 1
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('TRIGger1:FSWeep:SOURce SINGle')
        rf_supply.write('SOURce1:POWer:POWer ' + str(level))
        rf_supply.write('SOURce1:SWEep:FREQuency:MODE MANual')
        rf_supply.write('SOURce1:FREQuency:STARt ' + str(fstart) + ' GHz')
        rf_supply.write('SOURce1:FREQuency:STOP ' + str(fstop) + ' GHz')
        rf_supply.write('SOURce1:FREQuency:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:FREQuency:STEP:LINear ' + str(fstep) + ' GHz')
        rf_supply.write('SOURce1:SWEep:FREQuency:EXECute')
        time.sleep(1)
        while complete == False:
            event, not_used = window.read(timeout=100)  
            if event in stop_events:
                self.supply_turn_off()
                print('interupt during test, sweep cancelled')
                return False
            time.sleep(tstep)
            try:
                current_rf_freq = strip_reading(rf_supply.query('SOURce1:FREQ:FREQ?'))
            except Exception as e:
                current_rf_freq = '999999999999'    # false reading
            instr_out_data['rf_in']['freq'].append(current_rf_freq)
            print('supply RF1, rf freq = ' + str(current_rf_freq))
            if rfaddr['RF2'] != '':
                instr_out_data = read_power_sensor(self.rf_sensor, instr_out_data)
            instr_out_data = read_dc_supplies(self.dc_sups, instr_out_data)
            if float(current_rf_freq) >= fstop*(1_000_000_000):       # check whether sweep is complete
                complete = True
            else:
                rf_supply.write('SOURce1:FREQuency:MANual UP')
        rf_supply.write('OUTPut:ALL:STATe 0')   # turn off RF
        self.supply_turn_off()
        print('RF Frequency Sweep Complete')
        #print(instr_out_data)
        instr_out_data = pae_calculation(instr_out_data, inloss, outloss, level=level)
        print('PAE calculated and appended')
        flat_data = flatten_data(instr_out_data, inloss, outloss)
        print(flat_data)
        if flat_data == 'nul':
            print('Export unsuccessful, data manipulation error ')
            return 1
        else:  
            print('Data flatten successful')
        if export_to_csv(flat_data, self.rfinputs) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccessful, export error ')
        return 0 

    # rf level/freq sweep
    # confirmed functionality for R&S SMW200A vector signal analyzer only   
    def pwrfreq_sweep(self):
        complete = False
        instr_out_data = {}   # create all channel data lists
        self.rfinputs = MI.rfinputs
        fstart = self.rfinputs['fstart']
        fstop = self.rfinputs['fstop']
        fstep = self.rfinputs['fstep']
        pstart = self.rfinputs['pstart']
        pstop = self.rfinputs['pstop']
        pstep = self.rfinputs['pstep']
        tstep = self.rfinputs['tstep'] 
        inloss = self.rfinputs['inloss']
        outloss = self.rfinputs['outloss']
        new_freq = fstart
        for supply in dcchs:    # for all supplies
            channels = {}
            for ch in range(dcchs[supply]):       # for all channels
                channels[ch+1] = []
                #print(channels)
            instr_out_data[supply] = channels 
            #print(instr_out_data)
        rfin = {'pwr':[], 'freq':[]}
        rfout = {'pwr':[]}
        instr_out_data['rf_in'] = rfin
        instr_out_data['rf_out'] = rfout
        #print(instr_out_data)   

        try:  # creates rf resource
            rf_supply = rm.open_resource(rfaddr['RF1']) 
        except Exception as e:                            
            print(type(e))
            print('Connection to RF supply failed, sweep failed')
            return 1   # exits function if rf supply is not connected
        #print(self.rfinputs)
        if self.con_dc_sup() == False:
            print('Connection to DC supplies failed, sweep failed')
            return 1
        if self.start_rf_sensor() == False:
            print('Connection to rf diode sensor failed, sweep failed')
            return 1
        if not(qcuractive): 
            if self.tgl_gate_chs() == False:
                print('gate turn on failed, sweep failed')
                return 1
            if self.tgl_drain_chs() == False:
                print('drain turn on failed, sweep failed')
                return 1 
            if self.change_gate_chs() == False:
                print('gate change failed, sweep failed')
                return 1
        rf_supply.write('*RST')
        rf_supply.write('*CLS')
        rf_supply.write('TRIGger1:FSWeep:SOURce SINGle')
        rf_supply.write('SOURce1:FREQuency:CW ' + str(fstart) + ' GHz')
        rf_supply.write('SOURce1:SWEep:POWer:MODE MANual')
        rf_supply.write('SOURce1:POWer:STARt ' + str(pstart) + ' dBm')
        rf_supply.write('SOURce1:POWer:STOP ' + str(pstop) + ' dBm')
        rf_supply.write('SOURce1:POWer:MODE SWEep')
        rf_supply.write('Output1:STATe 1')
        rf_supply.write('SOURce1:SWEep:POWer:STEP ' + str(pstep))
        rf_supply.write('SOURce1:SWEep:FREQuency:EXECute')
        time.sleep(1)
        while complete == False:
            event, not_used = window.read(timeout=100)  
            if event in stop_events:
                self.supply_turn_off()
                print('interupt during test, sweep cancelled')
                return False
            time.sleep(tstep)
            try:
                current_rf_freq = strip_reading(rf_supply.query('SOURce1:FREQ:FREQ?'))
                current_rf_power = strip_reading(rf_supply.query('SOURce1:POWer:POWer?'))
            except Exception as e:
                current_rf_freq = '999999999999'
                current_rf_power = '999' 
            instr_out_data['rf_in']['freq'].append(current_rf_freq)
            instr_out_data['rf_in']['pwr'].append(current_rf_power)
            print('supply RF1, rf IN freq/pwr = ', strip_reading(current_rf_freq),
                     '/', strip_reading(current_rf_power))
            if rfaddr['RF2'] != '':
                instr_out_data = read_power_sensor(self.rf_sensor, instr_out_data)
            instr_out_data = read_dc_supplies(self.dc_sups, instr_out_data)
            if float(current_rf_power) >= pstop:
                if float(current_rf_freq) >= fstop*(1_000_000_000):
                    complete = True
                else:
                    new_freq += fstep 
                    rf_supply.write('SOURce1:FREQuency:CW ' + str(new_freq) + ' GHz')
                    rf_supply.write('SOURce1:POWer:MANual ' + str(pstart) + ' dBm')
                    time.sleep(1)
            else:
                rf_supply.write('SOURce1:POWer:MANual UP')
        rf_supply.write('OUTPut:ALL:STATe 0')
        self.supply_turn_off()
        print('RF Power/Frequency Sweep Complete')
        #print(instr_out_data)
        instr_out_data = pae_calculation(instr_out_data, inloss, outloss)
        print('PAE calculated and appended')
        flat_data = flatten_data(instr_out_data, inloss, outloss)
        # print(flat_data)
        if flat_data == 'nul':
            print('Export unsuccessful, data manipulation error')
            return 1
        else:  
            print('Data flatten successful')
        if export_to_csv(flat_data, self.rfinputs) == True:
            print('Export to CSV successful')
        else:
            print('Export unsuccessful, export error ')
        return 0

if __name__ == '__main__':

    frqsuff = ['Hz', 'kHz', 'MHz', 'GHz']
    default_folder = 'C:/Users/AndrewThomas/OneDrive - ' + \
        'CSA Catapult/Documents/Equipment VISA Integration/RF sweep data'
    validfolder = True
    names = {'DC Power Supply (1) (Gate Supply)':'DC1','DC Power Supply (2)':'DC2',
            'DC Power Supply (3)':'DC3','DC Power Supply (4)':'DC4', 'Vector Signal Generator':'RF1', 'Diode Power Sensor':'RF2', 'Signal & Spectrum Analyzer':'RF3'}
    rf_supply_types = ['Vector Signal Generator', 'Diode Power Sensor', 'Signal & Spectrum Analyzer']
    stop_events = '_STOPP_', '_STOPF_', '_STOPPF_', '_STOPLOG_'
    cur_tab = 'pwr'
    dcaddr = {'DC1':'','DC2':'','DC3':'','DC4':''}
    dcchs = {'DC1':0,'DC2':0,'DC3':0,'DC4':0}
    rfaddr = {'RF1':'', 'RF2':''}
        
    qcuractive = True
    folder = []
    gate_control = False
    stop_control = False
    # gui theme colour
    sg.theme('DarkBlue4')
    BG = BuildGui()

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
        [sg.Col(setup_col_1)],
        [sg.HorizontalSeparator(key='_SEP.1_')],
        [sg.Text('Select instrument from table and assign functionality:',
                 font='bold 12'), sg.Push()],
        [sg.Text('Instrument ID:', size=(20,1), font='bold 11'),
         sg.Input(size=(28,1), disabled=True, key='_SLCT.INSTR_'),
         sg.Push()],
        [sg.Text('Instrument functionality:', size=(20,1), font='bold 11'),
         sg.OptionMenu(values=names.keys(),
                       key='_INSTR.FUNC_'),
         sg.Push()],
        [sg.Col([[
            sg.Button('Update Instrument', key='_UPDATE.INSTR_',
                    font='bold 11', button_color='Gray58')]]),
         sg.Push()],
        [sg.HorizontalSeparator(key='_SEP.2_')],
        [sg.Col([
            [sg.Text('Sweep mode:', font='bold 12'), sg.Push()],
            [sg.Radio('Power Sweep', 'Sweep', default=True,
                    enable_events=True, key='_PWR.SWEEP_',
                    font='bold 11')],
            [sg.Radio('Frequency Sweep', 'Sweep', default=False,
                    enable_events=True, key='_FRQ.SWEEP_', font='bold 11')],
            [sg.Radio('Power & Frequency Sweep', 'Sweep', default=False,
                    enable_events=True, key='_PWRFRQ.SWEEP_', font='bold 11')]],
                    justification='left'),
         sg.Col([
            [sg.Text('Sweep options:', font='bold 12')],
            [sg.Checkbox('Find quiescent current', default=True, k='_FINDQCUR_', 
                    enable_events=True)],
            [sg.Text('ch' + str(i+1) + ' (mA)', s=(8, 1), p=(1,0),
                    font='bold 8', justification='l', k= '_TEXT_QC' + str(i+1))
                    for i in range(4)],
            [sg.InputText(0, size=(7, 1), disabled=True, font='bold 8', 
                    k=('_SETUP_QC' + str(i + 1))) for i in range(4)]], 
         vertical_alignment='top'),
         sg.Col([
            [sg.Text('Input Feed Loss (dB)', s=(18, 1), font='bold 10')],
            [sg.InputText(4, size=(15, 1), font='bold 10', k='IN_LOSS')],
            [sg.Text('Output Feed Loss (dB)', s=(18, 1), font='bold 10')],
            [sg.InputText(30, size=(15, 1), font='bold 10', k='OUT_LOSS')]
         ])],
        [sg.HorizontalSeparator(key='_SEP.3_')],
        [sg.Text('Select export options:', font='bold 12'), sg.Push()], 
        [sg.Col([
            [sg.Button('Open Folder'),
            sg.Push(), 
            sg.Text('Save in: ' + str(default_folder), justification='r', key='_FOLDER_')]]),
         sg.Push()],
        [sg.Text('Include in file title:'), sg.Push()],
        [sg.Col([[
            sg.Checkbox('Date', default=True, k='_DATE_'),
            sg.Checkbox('Time', default=True, k='_TIME_'),
            sg.Checkbox('Stop and Start Power', default=False, k='_SSP_'),
            sg.Checkbox('Stop and Start Frequency', default=False, disabled=True, k='_SSF_')]]),
        sg.Push()],
        ]

    pwr_layout = [
        [sg.Text('Select power sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name('pwr')],
        [BG.rf_supply_col_inputs('pwr', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 1: (gate only)', 
                   font='bold 12', s=(50,1)),
         sg.VerticalSeparator(),
         sg.Text('Select power sweep parameters for DC supply 2: ', 
                   font='bold 12')],
        [BG.power_supply_col_name(),
        BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr', disabled=False), 
        BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 3: ', 
                   font='bold 12', s=(50,1)),
         sg.VerticalSeparator(),
         sg.Text('Select power sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [BG.power_supply_col_name(), BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwr'), BG.power_supply_col_inputs('pwr')],
        [sg.HorizontalSeparator()],
        [sg.Button('Ok', pad=(5,4), key='_OKP_'),
         sg.Push(),
         sg.Button('Gate OFF', p=(5,4), key='_GATEP_', button_color='red'),
         sg.Button('START',  p=(5,4), key='_STARTP_')], 
        [sg.Push(),
        sg.Button('STOP', p=(5,4), key='_STOPP_', button_color='red')]
    ]
    
    freq_layout = [
        [sg.Text('Select frequency sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name('freq')],   
        [BG.rf_supply_col_inputs('freq', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 1: (gate only)', 
                   font='bold 12', s=(52,1)),
         sg.VerticalSeparator(),
         sg.Text('Select frequency sweep parameters for DC supply 2: ',
                   font='bold 12')],
        [BG.power_supply_col_name(), BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq', disabled=False), 
        BG.power_supply_col_inputs('freq')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select frequency sweep parameters for DC supply 3: ', 
                   font='bold 12', s=(52,1)),
         sg.VerticalSeparator(),
         sg.Text('Select frequency sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [BG.power_supply_col_name(), BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('freq'), BG.power_supply_col_inputs('freq')],
        [sg.HorizontalSeparator()],
        [sg.Button('Ok', pad=(5,4), key='_OKF_'),
         sg.Push(),
         sg.Button('Gate OFF', p=(5,4), key='_GATEF_', button_color='red'),
         sg.Button('START',  p=(5,4), key='_STARTF_')],
        [sg.Push(),
        sg.Button('STOP', p=(5,4), key='_STOPF_', button_color='red')]
        ]

    pwrfreq_layout = [
        [sg.Text('Select power sweep parameters for vector signal '
                 'generator:', font='bold 12')],
        [BG.rf_supply_col_name('pwrfreq')],
        [BG.rf_supply_col_inputs('pwrfreq', disabled=False)],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 1: (gate only)', 
                   font='bold 12', s=(50,1)),
         sg.VerticalSeparator(),
         sg.Text('Select power sweep parameters for DC supply 2: ', 
                   font='bold 12')],
        [BG.power_supply_col_name(), BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwrfreq', disabled=False), 
        BG.power_supply_col_inputs('pwrfreq')],
        [sg.HorizontalSeparator()],
        [sg.Text('Select power sweep parameters for DC supply 3: ', 
                   font='bold 12', s=(50,1)),
         sg.VerticalSeparator(),
         sg.Text('Select power sweep parameters for DC supply 4: ', 
                   font='bold 12')],
        [BG.power_supply_col_name(), BG.power_supply_col_name()],
        [BG.power_supply_col_inputs('pwrfreq'), BG.power_supply_col_inputs('pwrfreq')],
        [sg.HorizontalSeparator()],
        [sg.Button('Ok', pad=(5,4), key='_OKPF_'),
         sg.Push(),
         sg.Button('Gate OFF', p=(5,4), key='_GATEPF_', button_color='red'),
         sg.Button('START',  p=(5,4), key='_STARTPF_')],
        [sg.Push(),
        sg.Button('STOP', p=(5,4), key='_STOPPF_', button_color='red')] 
    ]

    logging_layout = [ 
        [sg.Text('Logging tab for debugging problems.')],
        [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True,
                        expand_y=True, write_only=True, reroute_stdout=True,
                        reroute_stderr=True, echo_stdout_stderr=True,
                        autoscroll=True, auto_refresh=True)],
        [sg.Push(),
        sg.Button('STOP Sweep', p=(5,4), key='_STOPLOG_', button_color='red')] 
    ]
    
    layout = [[sg.TabGroup([[
        sg.Tab('Instrument Setup', setup_layout, element_justification= 'c'),
        sg.Tab('Power Sweep', pwr_layout, visible=True, key='_PWR.TAB_'),
        sg.Tab('Frequency Sweep', freq_layout, visible=False, key='_FRQ.TAB_'),
        sg.Tab('Power/Frequency Sweep', pwrfreq_layout, visible=False, key='_PWRFRQ.TAB_'),
        sg.Tab('Logging', logging_layout)]],
                           tab_location='centertop', title_color='White',
                           tab_background_color='Gray',
                           selected_title_color='White',
                           selected_background_color='Purple',
                           border_width=5)]]

    window = sg.Window('RF Amplifier Frequency/Power Sweep',
                       layout, grab_anywhere=True, resizable=True,
                       margins=(0,0), finalize=True, location=(0,0),
                       scaling=1.5, element_padding=(4, 2))
    
    window.set_min_size(window.size)
    os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries '
                                 'Suite\\bin')
    rm = visa.ResourceManager('ktvisa32')
    BG = BuildGui()
    BG.sep_colour('_SEP.1_','SlateBlue3')
    BG.sep_colour('_SEP.2_','SlateBlue3')
    BG.sep_colour('_SEP.3_','SlateBlue3')

    gate_control = False

    while True: 
        event, values = window.read()  
        MI = ManageInputs()
        IK = InstrControl()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):  
            print('============ Event = ', event, ' ==============')
            # print('-------- Values Dictionary (key=value) --------') # enable to show all key values
            # for key in values:
            #      print(key, ' = ',values[key])

        if event == '_INSTR.SEARCH_':
            window['_INSTR.TABLE_'].update(values=[['','','','']])
            connected = instr_check()
            window['_INSTR.TABLE_'].update(values=connected)
            
            if len(connected) == 0:
                sg.popup_error(f'No connected instruments detected. Ensure '
                               'instrument connected and search again.')

        elif event == '_UPDATE.INSTR_':
            if values['_SLCT.INSTR_'] != '' and values['_INSTR.FUNC_'] != '':
                device_type =  MI.table_update()
                if device_type == 'DC Power Supply':
                    try:
                        MI.tog_dc_chs()
                        MI.tog_qcur_chs()
                    except Exception as e:
                        print('Channel enable failed')
            else:
                sg.popup_error(f'Make sure instrument and functionality '
                                'both selected in order to update table.')

        elif event == '_FINDQCUR_':
            qcuractive = values[event]

        elif event == '_INSTR.TABLE_':
            try:
                rowselected = [connected[row] for row in values[event]]
                instrselected = rowselected[0][0]
                window['_SLCT.INSTR_'].update(instrselected)
            except:
                pass
     
        elif event in '_PWR.SWEEP_':
            update_tab(event)
            cur_tab = 'pwr'
        elif event == '_FRQ.SWEEP_':
            update_tab(event)
            cur_tab = 'freq'
        elif event == '_PWRFRQ.SWEEP_':
            update_tab(event)
            cur_tab = 'pwrfreq'

        elif event == 'Open Folder':
            print('Clicked Open Folder!')
            folder = sg.popup_get_folder('Choose your folder', keep_on_top=True)
            print('User chose folder: ' + str(folder))
            if folder != '':
                sg.popup('You chose: ' + str(folder), keep_on_top=True)
                window['_FOLDER_'].update('Save in: ' + str(folder))
                validfolder = False
            else: 
                sg.popup('Folder is invalid', keep_on_top=True)
                validfolder = False

        elif event == '_OKF_' or event == '_OKP_' or event == '_OKPF_':                                           
            print('-------- OK --------')  
            print(cur_tab)                                                             
            try:
                MI.get_dc_inputs()
                MI.get_rf_inputs()
                if MI.dc_input_check() == True:
                    if MI.rf_input_check() == True:
                        IK.update_gate_values()
                        IK.update_drain_values()
                    else:
                        print('RF signal generator input is invalid')
                else:
                    print('DC supply input is invalid')
            except Exception as e:
                print(type(e))
                print('Instrument connect not completed')

        elif event == '_GATEP_' or event == '_GATEF_' or event == '_GATEPF_':
            gate_control = not(gate_control)
            IK.con_dc_sup()
            if IK.tgl_gate_chs(enabled=int(gate_control)):
                active = gate_button_update(gate_control)
                print('Gate Turned', str(active))
        elif event == '_STARTP_' or event == '_STARTF_' or event == '_STARTPF_':
            print('-------- START Sweep --------')
            stop_control = not(stop_control)
            MI.get_dc_inputs()
            MI.get_rf_inputs()
            if gate_control:
                gate_control = not(gate_control)
                gate_button_update(gate_control)
                # IK.tgl_gate_chs(enabled=int(gate_control)) # turn off gate before start

            if validfolder:
                if MI.dc_input_check() == True:
                    if MI.rf_input_check() == True:
                        IK.update_drain_values()
                        IK.update_gate_values()
                        ready = False
                        if qcuractive: 
                            if IK.find_quiescent():
                                print('quiescent currents found')
                                # now in quiescent state
                                ready = True
                        else:
                            print('find quiescent currents disabled, using voltage values from DC1 table')
                            ready = True
                        if event == '_STARTP_' and ready:
                            IK.power_sweep()
                        elif event == '_STARTF_' and ready:
                            IK.freq_sweep()
                        elif event == '_STARTPF_' and ready:
                            IK.pwrfreq_sweep()
                        else:
                            print('sweep cancelled')
                    else:
                        print('RF input is invalid, sweep cancelled')
                else:
                    print('DC input is invalid, sweep cancelled')
            else: 
                print('Invalid folder, please pick an export folder before starting sweep')
            stop_control = not(stop_control)

    window.close()
