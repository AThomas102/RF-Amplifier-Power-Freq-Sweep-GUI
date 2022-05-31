# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 16:35:11 2022

@author: AlexanderArnstein
"""

def GUI1():
    import PySimpleGUI as sg
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    import csv
    
    sg.theme('DarkBlue4')
    
    col1 = [[sg.Frame(layout = [
                           
                [sg.Button("Split SOAK and TEST",disabled=True, size=(22,1))],
                
                [sg.Button("Split by device",disabled=True, size=(22,1))],
    
                [sg.Button("Split into TEST cycles",disabled=True, size=(22,1))],
                
                [sg.Button("Average TEST cycle data", key = "average",disabled=True, size=(22,1)), sg.Button("Export averages", disabled = True, size = (20,1))],
                             
                ],title='Data Processing')],
        
        [sg.Frame(layout = [
                     
                    [sg.CBox('1',size=(2,1),key=('cb1'),enable_events=True),sg.CBox('2',size=(2,1),key=('cb2'),enable_events=True),sg.CBox('3',size=(2,1),key=('cb3'),enable_events=True),sg.CBox('4',size=(2,1),key=('cb4'),enable_events=True),sg.CBox('5',size=(2,1),key=('cb5'),enable_events=True),sg.CBox('6',size=(2,1),key=('cb6'),enable_events=True),sg.CBox('7',size=(2,1),key=('cb7'),enable_events=True),sg.CBox('8',size=(2,1),key=('cb8'),enable_events=True)],
                    
                    [sg.CBox('9',size=(2,1),key=('cb9'),enable_events=True),sg.CBox('10',size=(2,1),key=('cb10'),enable_events=True),sg.CBox('11',size=(2,1),key=('cb11'),enable_events=True),sg.CBox('12',size=(2,1),key=('cb12'),enable_events=True),sg.CBox('13',size=(2,1),key=('cb13'),enable_events=True),sg.CBox('14',size=(2,1),key=('cb14'),enable_events=True),sg.CBox('15',size=(2,1),key=('cb15'),enable_events=True),sg.CBox('16',size=(2,1),key=('cb16'),enable_events=True)],
                    
                    [sg.CBox('17',size=(2,1),key=('cb17'),enable_events=True),sg.CBox('18',size=(2,1),key=('cb18'),enable_events=True),sg.CBox('19',size=(2,1),key=('cb19'),enable_events=True),sg.CBox('20',size=(2,1),key=('cb20'),enable_events=True),sg.CBox('21',size=(2,1),key=('cb21'),enable_events=True),sg.CBox('22',size=(2,1),key=('cb22'),enable_events=True),sg.CBox('23',size=(2,1),key=('cb23'),enable_events=True),sg.CBox('24',size=(2,1),key=('cb24'),enable_events=True)],
                    
                    [sg.CBox('25',size=(2,1),key=('cb25'),enable_events=True),sg.CBox('26',size=(2,1),key=('cb26'),enable_events=True),sg.CBox('27',size=(2,1),key=('cb27'),enable_events=True),sg.CBox('28',size=(2,1),key=('cb28'),enable_events=True),sg.CBox('29',size=(2,1),key=('cb29'),enable_events=True),sg.CBox('30',size=(2,1),key=('cb30'),enable_events=True),sg.CBox('31',size=(2,1),key=('cb31'),enable_events=True),sg.CBox('32',size=(2,1),key=('cb32'),enable_events=True)],
                    
                    ],title= "Device Grid", key="Device Grid")],
            
        [sg.Frame(layout = [ 
                
                [sg.Button("Check temperature cycling",disabled=True,size=(22,1))],
                
                [sg.Button("Add to power plot",disabled=True,size=(22,1)),sg.Button("Add to current plot",disabled=True,size=(22,1)),sg.Button("Show plot",disabled=True,size=(8,1)), sg.Button("Plot all", key = "plot all 1",disabled=True,size=(8,1))],
                
                [sg.Button("Check TEST lengths",disabled=True,size=(22,1))],
                
                [sg.Button("Check total outlier deletions", disabled=True, size = (22,1)), sg.Button("Check device outlier deletions", disabled=True, size = (22,1))],
                            
                ],title = "Graph plotting")]]
    
    tab1 = [[sg.Input("Input datafile", key ="datafile",size=(40,1)), sg.FileBrowse(size=(8,1)), sg.Button("Load", size=(8,1))],
            [sg.Frame(layout = [[sg.Column(col1)]],title="")]]
    
    tab2 = [[sg.Text("Lock Master Settings"), sg.CBox('', default=True, key = ("Lock"), enable_events=True)],
            [sg.Frame(layout = [
            [sg.Text("Auto-delete blank data?",size=(17,1)), sg.CBox('', default=True, key = "auto-delete", disabled=True,enable_events=True, pad=(7)),sg.Button("Delete blank data", disabled=True,size=(14,1)), sg.Text("number of blank rows = ",size=(18,1)), sg.Text("", key = "num blank",size=(2,1)), sg.Text("percentage of data blank = "), sg.Text("", key = "percent blank")],
            [sg.Text("Test Temperature (°C):",size=(22,1)), sg.Input("25",size=(6,1),key="Temp_Test",disabled=True),sg.Text(size=(7,1),pad=7), sg.Text("Threshold (%):",size=(16,1)), sg.Input("10",size=(5,1), key = "Temp_Threshold",disabled=True), sg.Button("Set", key="Set_Temp",disabled=True,size=(5,1)), sg.Text("Min ="), sg.Text("", key="Min",size=(6,1),pad=7), sg.Text("Max ="), sg.Text("",key = "Max",size=(5,1))],
            [sg.Text("Choose a testing mode: ", size=(22,1)), sg.Spin(values = ("APC","ACC"), size=(6,1), key="Mode", disabled=True), sg.Button("Set", key="set_mode",disabled=True,size=(5,1),pad=10)], 
            [sg.Text("Spotscan length (mins):",size=(22,1)), sg.Input("5", size=(6,1), key="spot_time", disabled=True),sg.Text(pad=6), sg.Button("Set", key="spot_time_set",disabled=True,size=(5,1))],
            [sg.Text("Set APC target (mW): ",size=(22,1),key="mode_text"), sg.Input("4", key = "target", size=(6,1), disabled=True), sg.Text(size=(8,1)),sg.Text("Set tolerance (%): ",size=(15,1),pad=8), sg.Input("1", key = "tolerance", size=(5,1),disabled = True), sg.Button("Set",key="const,tol",disabled=True,size=(5,1))],
            [sg.Text("Averaging threshold (%): ", size=(22,1)), sg.Input("10",size = (6,1), key="avging_threshold", disabled=True),sg.Text(pad=6), sg.Button("Set", key = "set_avg_threshold", disabled=True,size=(5,1))],
            ],title='')],
            ]
    
    tab3 = [[sg.Text("This is how to use the analysis GUI....")]]
    
    layout = [           
                 [sg.TabGroup([[sg.Tab('Analysis', tab1), sg.Tab('Master Settings', tab2), sg.Tab('Help', tab3)]],key = "Tabs",enable_events=True,tab_background_color='White',selected_background_color='#0072c6', selected_title_color='White')],
                                           
                 [sg.Button("OK",size=(7,1)), sg.Button('Cancel',size=(7,1)), sg.Button("Reset",size=(7,1)), sg.Text("Status",key="Status")]]
                 
    
    window = sg.Window("CSA Catapult - Reliability Test Analyser", icon = "CSA_icon.ico",resizable=True).Layout(layout)
    
    buttonlist = ["Delete blank data","Set_Temp","Check temperature cycling","Split SOAK and TEST","Split by device","Add to power plot","Add to current plot","Show plot","plot all 1","spot_time_set","Split into TEST cycles","Check TEST lengths","set_mode","const,tol","average","Export averages","Check total outlier deletions","Check device outlier deletions"]
        
    startpoints = {}
    r_mins = {}
    D = {}
    for i in range(1,33):
        startpoints[i] = 0
        r_mins[i] = 0
        D.update({i:False})
    
    print("analysis initiated")
    while True:
        
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == 'Cancel' and sg.popup_yes_no('Are you sure?') == "Yes":
            print("analysis terminated")
            window.close()
            break
        
        if event == 'OK':  
            print("analysis complete")
            window.close()
            break
        
        if event == "Reset":
            for i in range(len(buttonlist)):
                button = buttonlist[i]
                window[button].update(disabled=True)
                for j in range(1,33):
                    window["cb"+str(j)].update(text_color = "white")
        
        if event == "Load":
            try:
                from analysis_module import importer 
                data, headers = importer(values["datafile"],1)
                window["Status"].update("Data imported",text_color="lime green")
                
                if values["auto-delete"] == True:
                    from analysis_module import blank_delete
                    data_noblank, counter_blank, percent_blank = blank_delete(data)
                    window["num blank"].update(counter_blank)
                    window["percent blank"].update(percent_blank)
                    window["Check temperature cycling"].update(disabled=False)
                    window["Split SOAK and TEST"].update(disabled=False)
                    window["Status"].update("Data imported and blank data deleted",text_color="lime green")
                    
                Temp_Test = float(values['Temp_Test'])
                Temp_Threshold = float(values['Temp_Threshold'])
                Min = str(str(np.round(Temp_Test*(1-Temp_Threshold/100),2)) + str(" °C"))
                Max = str(str(np.round(Temp_Test*(1+Temp_Threshold/100),2)) + str(" °C"))
                window["Max"].update(Max)
                window["Min"].update(Min)
                
                spot_time = float(values["spot_time"])
                
                mode = values["Mode"]
                
                constant_set = float(values["target"])
                tolerance = float(values["tolerance"])
                
                avging_threshold = float(values["avging_threshold"])
                
            except FileNotFoundError:
                window["Status"].update("No file found at selected filepath",text_color="red")
                
            except IndexError:
                window["Status"].update("Incorrect file format", text_color="red")
                
            except UnicodeDecodeError:
                window["Status"].update("Incorrect file format - must be csv", text_color="red")
            
            except Exception:
                window['Status'].update("Unknown error",text_color="red")
    
        if event == "Lock":
            if values["Lock"] == True:
                
                window["auto-delete"].update(disabled=True)
                
                window["Set_Temp"].update(disabled=True)
                window["Temp_Test"].update(disabled=True)
                window["Temp_Threshold"].update(disabled=True)
                
                window["set_mode"].update(disabled=True)
                window["Mode"].update(disabled=True)
                
                window["spot_time"].update(disabled=True)
                window["spot_time_set"].update(disabled=True)
                
                window["target"].update(disabled=True)
                window["tolerance"].update(disabled=True)
                window["const,tol"].update(disabled=True)
                
                window["avging_threshold"].update(disabled=True)
                window["set_avg_threshold"].update(disabled=True)
                
            if values["Lock"] == False:
                
                window["auto-delete"].update(disabled=False)
                
                window["Temp_Test"].update(disabled=False)
                window["Temp_Threshold"].update(disabled=False)
                window["Set_Temp"].update(disabled=False)
                
                window["set_mode"].update(disabled=False)
                window["Mode"].update(disabled=False)
                
                window["spot_time"].update(disabled=False)
                window["spot_time_set"].update(disabled=False)
                
                window["target"].update(disabled=False)
                window["tolerance"].update(disabled=False)
                window["const,tol"].update(disabled=False)            
                
                window["avging_threshold"].update(disabled=False)
                window["set_avg_threshold"].update(disabled=False)
        
        if event == "auto-delete":
            if values["auto-delete"] == True:
                window["Delete blank data"].update(disabled=True)
                
            if values["auto-delete"] == False:
                window["Delete blank data"].update(disabled=False)
            
        if event == "Set_Temp":
            Temp_Test = float(values['Temp_Test'])
            Temp_Threshold = float(values['Temp_Threshold'])
            Min = str(str(np.round(Temp_Test*(1-Temp_Threshold/100),2)) + str(" °C"))
            Max = str(str(np.round(Temp_Test*(1+Temp_Threshold/100),2)) + str(" °C"))
            window["Max"].update(Max)
            window["Min"].update(Min)
            window["Status"].update("Temperature set",text_color="lime green")
             
        if event == "Delete blank data":
            from analysis_module import blank_delete
            try:
                data_noblank, counter_blank, percent_blank = blank_delete(data)
                window["num blank"].update(counter_blank)
                window["percent blank"].update(percent_blank)
                window["Status"].update("Blank rows deleted",text_color="lime green")
                window["Check temperature cycling"].update(disabled=False)
                window["Split SOAK and TEST"].update(disabled=False)        
            except NameError:
                window["Status"].update("Please load a file first",text_color="red")
                
        if event == "Check temperature cycling":
            from analysis_module import temp_cycling
            temp_cycling(data_noblank, Temp_Test, Temp_Threshold)
            window["Status"].update("Temperature cycling check",text_color="lime green")
            
        if event == "Split SOAK and TEST":
            from analysis_module import soak_remove
            test_data, soak_data = soak_remove(data_noblank, Temp_Test, Temp_Threshold)
            window["Status"].update("TEST and SOAK data split",text_color="lime green")
            window["Split by device"].update(disabled=False)
                
        if event == "Split by device":
            
            from analysis_module import device_detect
            from analysis_module import device_split
            
            devices = device_detect(test_data,4)
            #colors = sns.color_palette("hls",len(devices))
    
            for i in range(1,33):
                if i in devices:
                    window["cb"+str(i)].update(text_color = "#66FF00")
                if i not in devices:
                    window["cb"+str(i)].update(text_color = "red")
            
            test_devices = device_split(test_data, devices,4)
            
            window["Status"].update("Data split by device",text_color="lime green")
            window["plot all 1"].update(disabled=False)
            window["Add to current plot"].update(disabled=False)
            window["Add to power plot"].update(disabled=False)
            window["Split into TEST cycles"].update(disabled=False)
         
        if event == "plot all 1":
            from analysis_module import plot_all_1
            times, currents, powers = plot_all_1(test_devices, devices)
            colors = sns.color_palette("hls",len(devices))
            
            for i in range(len(currents)):
        
                dummy = currents[i]
                first = dummy[0]
                currents[i] = [k/first for k in currents[i]]
            
                plt.plot(times[i],currents[i], color = colors[i], label = 'Device {}'.format(devices[i]), linestyle = '-', marker = '.')
                         
            plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
            plt.grid()
            plt.xlabel('Time (h)')
            plt.ylabel('Normalised Current')
            plt.show()
        
            for i in range(len(powers)):
            
                dummy = powers[i]
                first = dummy[0]
                powers[i] = [k/first for k in powers[i]]
            
                plt.plot(times[i],powers[i], color = colors[i], label = 'Device {}'.format(devices[i]), linestyle = '-', marker = '.')
        
            plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
            plt.grid()
            plt.xlabel('Time (h)')
            plt.ylabel('Normalised Power')
            plt.show()
            
            window["Status"].update("All devices plotted",text_color = "lime green")
            
        for i in range(32):
            if event == "cb"+str(i+1):
                if values["cb"+str(i+1)] == True:
                    D.update({i+1:True})
                if values["cb"+str(i+1)] == False:
                    D.update({i+1:False})     
                    
        if event == "Add to current plot":
            
            devs = []
            for i in D:
                if D[i] == True:
                    devs.append(i)
            
            if len(devs) > 0:
                try:
                    window["Status"].update("Devices added = " + str(devs),text_color="lime green")
                    window["Show plot"].update(disabled=False)
            
                    colors = sns.color_palette("hls",len(devs))
            
                    from analysis_module import plot_all_1
                    times, currents, powers = plot_all_1(test_devices, devices)
                                    
                    for i in range(len(devs)):
                        devindex = devices.index(devs[i])
                        
                        plt.plot(times[devindex],currents[devindex], color=colors[i], label = 'Device {}'.format(devs[i]), linestyle = '-', marker = '.')
                    
                    plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
                    plt.grid()
                    plt.xlabel('Time (h)')
                    plt.ylabel('Current (mA)')
                
                except ValueError:
                    window["Status"].update("Invalid device selection",text_color="red")
                    window["Show plot"].update(disabled=True)
                
            if len(devs) == 0:
                window["Status"].update("No devices selected",text_color="red")
                window["Show plot"].update(disabled=True)
       
        if event == "Add to power plot":
            
            devs = []
            for i in D:
                if D[i] == True:
                    devs.append(i)
            
            if len(devs) > 0:
                try:
                    window["Status"].update("Devices added = " + str(devs),text_color="lime green")
                    window["Show plot"].update(disabled=False)
                    
                    colors = sns.color_palette("hls",len(devs)) 
                   
                    from analysis_module import plot_all_1
                    times, currents, powers = plot_all_1(test_devices, devices)
                    
                    for i in range(len(devs)):
                        devindex = devices.index(devs[i])
                        
                        plt.plot(times[devindex],powers[devindex], color=colors[i], label = 'Device {}'.format(devs[i]), linestyle = '-', marker = '.')
                    
                    plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
                    plt.grid()
                    plt.xlabel('Time (h)')
                    plt.ylabel('Power (mW)')
                
                except ValueError:
                    window["Status"].update("Invalid device selection",text_color="red")
                    window["Show plot"].update(disabled=True)
                
            if len(devs) == 0:
                window["Status"].update("No devices selected",text_color="red")
                window["Show plot"].update(disabled=True)
        
        if event == "Show plot":
            if len(devs) == 0:
                window["Status"].update("No devices selected",text_color="red")
            if len(devs) > 0:
                plt.show()
                window["Status"].update("Devices plotted =" + str(devs), text_color="lime green")
                window["Show plot"].update(disabled=True)
       
        if event == "spot_time_set":
            spot_time = float(values["spot_time"])
            window["Status"].update("Spotscan length set to " + str(spot_time) + " mins",text_color="lime green")
        
        if event == "Split into TEST cycles":
            from analysis_module import tc_split
            time_col, indices, test_devices_cycles = tc_split(test_devices, spot_time)
            window["Status"].update("Device data split by TEST cycle",text_color="lime green")
            window["Check TEST lengths"].update(disabled=False)
            window["average"].update(disabled=False)
            
            from analysis_module import time_function
            soak_times = time_function(time_col, indices)
        
        if event == "Check TEST lengths":
            from analysis_module import tc_length
            lengths, uniquelengths, lengthfrequencies = tc_length(test_devices_cycles)
            
            plt.bar(uniquelengths,lengthfrequencies, edgecolor = 'black')
            plt.xlabel('Number of spotscans per TEST cycle')
            plt.ylabel('Frequency')
            plt.grid()
            plt.show()
            
            plt.plot(soak_times[0],lengths[0], marker = '.')
            plt.grid()
            plt.xlabel('Time (h)')
            plt.ylabel('Number of spotscans per TEST cycle')
            plt.show()
            
            window["Status"].update("TEST length check",text_color="lime green")
         
        if event == "set_mode":
            mode = values["Mode"]
            window["Status"].update(str(mode) + " mode selected",text_color="lime green")
            if mode == "APC":
                window["mode_text"].update("Set APC target (mW): ")
            if mode == "ACC":
                window["mode_text"].update("Set ACC target (mA): ")
                
        if event == "const,tol":
            constant_set = float(values["target"])
            tolerance = float(values["tolerance"])
            window["Status"].update("Target and tolerance set",text_color="lime green")
            window["average"].update(disabled=False)
        
        if event == "set_avg_threshold":
            avging_threshold = float(values["avging_threshold"])
            window["Status"].update("Averaging threshold set to: " + str(avging_threshold),text_color="lime green")
        
        if event == "average":
            from analysis_module import statistics
            
            averages = statistics(mode, test_devices_cycles, soak_times, avging_threshold,constant_set,tolerance)
            window["Status"].update("TEST cycles averaged",text_color="lime green")
            window["Export averages"].update(disabled=False)
            window["Check total outlier deletions"].update(disabled=False)
            
        if event == "Check total outlier deletions":
            counter_tol = []
            counter_avging = []
            counter_cycles = []
            device_list = []
            for i in range(len(averages)):
                device = averages[i]
                for j in range(len(device)):
                    tc = device[j]
                    device_list.append(tc[2])
                    counter_tol.append(tc[8])
                    counter_avging.append(tc[9])
                    counter_cycles.append(tc[10])
                    
            dcis = [0]
            for i in range(len(device_list)-1):          
                if device_list[i+1] != device_list[i]:
                    device_change_index = i+1
                    dcis.append(device_change_index)
            dcis.append(len(device_list))
            
            totals_tol = []
            totals_avging = []
            totals_cycles = []
    
            for i in range(len(dcis)-1):
                index1 = dcis[i]
                index2 = dcis[i+1]
                totals_tol.append(np.sum(counter_tol[index1:index2]))
                totals_avging.append(np.sum(counter_avging[index1:index2]))
                totals_cycles.append(np.sum(counter_cycles[index1:index2]))  
            
            device_list = list(np.unique(device_list))
            dev_array = np.array(device_list)
            w = 0.2
            
            plt.figure(num=None, figsize=(8,4), dpi=80, facecolor='w', edgecolor='k')
            plt.bar(dev_array-w, totals_tol, width = w, label = "Spotscans outside power tolerance")
            plt.bar(dev_array, totals_avging, width = w, label = "Spotscans outside averaging threshold")
            plt.bar(dev_array+w, totals_cycles, width = w, label = "Entire TEST cycles deleted")
            plt.xticks(dev_array)
            plt.xlabel("Device")
            plt.ylabel("Total deletions")
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.show()
            
            window["Status"].update("Total outlier deletion check",text_color="lime green")
            window["Check device outlier deletions"].update(disabled=False)
        
        if event == "Check device outlier deletions":
            
            devs = []
            for i in D:
                if D[i] == True:
                    devs.append(i)
            
            if len(devs) == 0 or len(devs) > 1:
                window["Status"].update("Please select exactly one device to check",text_color = "red")
                
            if len(devs) == 1:
                try:
                    dev = float(devs[0])
                    i = devices.index(dev)
                    dev_data = averages[i]
                    time = []
                    counter_tol = []
                    counter_avging = []
                    counter_cycles = []
                    for j in range(len(dev_data)):
                        tc = dev_data[j]
                        time.append(np.round(tc[0],0))
                        counter_tol.append(tc[8])
                        counter_avging.append(tc[9])
                        counter_cycles.append(tc[10])
                    
                    time_array = np.array(time)
                    
                    plt.figure(num=None, figsize=(8,4), dpi=80, facecolor='w', edgecolor='k')
                    plt.plot(time_array, counter_tol, label = "Spotscans outside power tolerance", linestyle = '-', marker = '.')
                    plt.plot(time_array, counter_avging, label = "Spotscans outside averaging threshold", linestyle = '-', marker = '.')
                    plt.plot(time_array, counter_cycles, label = "Entire TEST cycles deleted", linestyle = '-', marker = '.')
                    plt.xlabel("Time")
                    plt.ylabel("Deletions")
                    plt.title("Device {} outlier deletions".format(int(dev)))
                    plt.legend()
                    plt.grid()
                    plt.tight_layout()
                    plt.show()
                    
                    window["Status"].update("Device outlier deletion check",text_color="lime green")
                
                except ValueError:
                    window["Status"].update("Invalid device selection",text_color="red")
            
        if event == "Export averages":
    
            from datetime import datetime
            Date = str(datetime.now())
            date_reformat = "{}{}{}{}{}".format(Date[8:10],Date[5:7],Date[2:4],Date[11:13],Date[14:16])
            file_reformat = values["datafile"].split(".csv")[0]
            
            if values["Mode"] == "APC":
                unit = "mW"
            if values["Mode"] == "ACC":
                unit = "mA"
            
            metadata = [["Date/Time of analysis", Date], ["Auto-delete", str(values["auto-delete"])], ["Percentage blank data (%)", str(percent_blank)], ["Test temperature set (C)", values["Temp_Test"]], ["Temperature threshold set (%)", values["Temp_Threshold"]], ["Mode", values["Mode"]], ["Spot time set (mins)", values["spot_time"]], ["{} target {}".format(values["Mode"], unit), values["target"]], ["{} tolerance (%)".format(values["Mode"]), values["tolerance"]], ["Averaging threshold (%)", values["avging_threshold"]]]
            
            headers_out = ["Elapsed_time (h)","Timestamp","Device","Temperature (C)","Current (mA)","Photocurrent (mA)","Optical Power (mW)","Voltage (V)","Spotscans out of tolerance","Spotscans out of averging threshold","Entire cycles deleted"]
            with open('{}_averages_{}.csv'.format(file_reformat,date_reformat), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(metadata)
                writer.writerows([[]])
                writer.writerows([["Data"], headers_out])
                for i in range(len(averages)):
                    device = averages[i]
                    writer.writerows(device)
            
            window["Status"].update("Averages exported to current working directory",text_color="lime green")
    
    window.close()
    
    return

#GUI1()