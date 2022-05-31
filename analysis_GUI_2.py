# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 16:47:12 2022

@author: AlexanderArnstein
"""

def GUI2():
    import PySimpleGUI as sg
    import numpy as np
    import matplotlib.pyplot as plt
    import csv
    
    sg.theme('DarkBlue4')
    
    col1 = [[sg.Frame(layout = [
                
                [sg.Button("Split by device",disabled=True, size=(22,1))],
                                      
                [sg.Text("Minimum correlation r = ", size=(22,1),justification="left", border_width=3),sg.Input("0.9", size = (7,1),key = "r_min",pad=6),sg.Text(pad=7),sg.Button("Set", key = "r_set",disabled=True, size=(8,1)),sg.Text("Set startpoint (hrs):"), sg.Input("0",size=(5,1),key="start"), sg.Button("Set", key="set_start",disabled=True,size=(8,1))],
                
                [sg.Button("Check linear fit parameters", size=(22,1), key="check LFit", disabled=True)],
                
                [sg.Button("Perform linear fits", key = "tf_lfit",disabled=True, size=(22,1)), sg.Button("Export linear fits", disabled=True, size=(20,1))],
                                
                ], title='Linear Fitting')],
    
            [sg.Frame(layout = [
                 
                [sg.CBox('1',size=(2,1),key=('cb1'),enable_events=True),sg.CBox('2',size=(2,1),key=('cb2'),enable_events=True),sg.CBox('3',size=(2,1),key=('cb3'),enable_events=True),sg.CBox('4',size=(2,1),key=('cb4'),enable_events=True),sg.CBox('5',size=(2,1),key=('cb5'),enable_events=True),sg.CBox('6',size=(2,1),key=('cb6'),enable_events=True),sg.CBox('7',size=(2,1),key=('cb7'),enable_events=True),sg.CBox('8',size=(2,1),key=('cb8'),enable_events=True)],
                
                [sg.CBox('9',size=(2,1),key=('cb9'),enable_events=True),sg.CBox('10',size=(2,1),key=('cb10'),enable_events=True),sg.CBox('11',size=(2,1),key=('cb11'),enable_events=True),sg.CBox('12',size=(2,1),key=('cb12'),enable_events=True),sg.CBox('13',size=(2,1),key=('cb13'),enable_events=True),sg.CBox('14',size=(2,1),key=('cb14'),enable_events=True),sg.CBox('15',size=(2,1),key=('cb15'),enable_events=True),sg.CBox('16',size=(2,1),key=('cb16'),enable_events=True)],
                
                [sg.CBox('17',size=(2,1),key=('cb17'),enable_events=True),sg.CBox('18',size=(2,1),key=('cb18'),enable_events=True),sg.CBox('19',size=(2,1),key=('cb19'),enable_events=True),sg.CBox('20',size=(2,1),key=('cb20'),enable_events=True),sg.CBox('21',size=(2,1),key=('cb21'),enable_events=True),sg.CBox('22',size=(2,1),key=('cb22'),enable_events=True),sg.CBox('23',size=(2,1),key=('cb23'),enable_events=True),sg.CBox('24',size=(2,1),key=('cb24'),enable_events=True)],
                
                [sg.CBox('25',size=(2,1),key=('cb25'),enable_events=True),sg.CBox('26',size=(2,1),key=('cb26'),enable_events=True),sg.CBox('27',size=(2,1),key=('cb27'),enable_events=True),sg.CBox('28',size=(2,1),key=('cb28'),enable_events=True),sg.CBox('29',size=(2,1),key=('cb29'),enable_events=True),sg.CBox('30',size=(2,1),key=('cb30'),enable_events=True),sg.CBox('31',size=(2,1),key=('cb31'),enable_events=True),sg.CBox('32',size=(2,1),key=('cb32'),enable_events=True)],
                
                ],title= "Device Grid", key="Device Grid")],
        
            [sg.Frame(layout = [ 
                
                [sg.Button("Add to plot", disabled = True),sg.Button("Add to extrapolated plot",disabled=True,size=(22,1)), sg.Button("Show plot", key="show plot linear",disabled=True,size=(8,1))],
                
                ],title = "Graph plotting")]]
    
    tab1 = [[sg.Input("Input datafile", key ="datafile",size=(40,1)), sg.FileBrowse(size=(8,1)), sg.Button("Load", size=(8,1))],
            
            [sg.Frame(layout = [[sg.Column(col1)]],title="")]]
    
    tab2 = [[sg.Text("Lock Master Settings"), sg.CBox('', default=True, key = ("Lock"), enable_events=True)],
            
            [sg.Frame(layout = [
           
                [sg.Text("Choose a testing mode: ", size=(22,1)), sg.Spin(values = ("APC","ACC"), size=(6,1), key="Mode", disabled=True), sg.Button("Set", key="set_mode",disabled=True,size=(5,1),pad=16)],
                
                [sg.Text("Default minimum correlation: ", size=(22,1)), sg.Input("0.9", key="r_default", size=(6,1),disabled=True), sg.Text("", size=(1,1)), sg.Button("Set", key="rdefault_set", size=(5,1), disabled=True)],
                
                [sg.Text("Default start point (h): ", size=(22,1)), sg.Input("0",key="start_default", size=(6,1),disabled=True), sg.Text("", size=(1,1)), sg.Button("Set", key="startdefault_set", size=(5,1), disabled=True)],
            
                [sg.Text("Import r_mins and start points: ", size=(22,1)), sg.Input("csv file", key ="paramcsv",size=(17,1)), sg.FileBrowse(size=(8,1),key="parambrowse",disabled=True), sg.Button("Load", key="paramload", size=(8,1),disabled=True)],
                               
            ],title='')],
            ]
    
    tab3 = [[sg.Text("This is how to use the analysis GUI....")]]
    
    layout = [   #[sg.Menu(menu, tearoff=False)],
              
                 [sg.TabGroup([[sg.Tab('Analysis', tab1), sg.Tab('Master Settings', tab2), sg.Tab('Help', tab3)]],key = "Tabs",enable_events=True,tab_background_color='White',selected_background_color='#0072c6', selected_title_color='White')],
                                           
                 [sg.Button("OK",size=(7,1)), sg.Button('Cancel',size=(7,1)), sg.Button("Reset",size=(7,1)), sg.Text("Status",key="Status")]]
                 
    
    window = sg.Window("CSA Catapult - Reliability Test Analyser", icon = "CSA_icon.ico",resizable=True).Layout(layout)
                    
    buttonlist = ["Split by device","set_mode","r_set","set_start","rdefault_set","startdefault_set","parambrowse","paramload","check LFit","Add to plot","show plot linear","tf_lfit"]
       
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
            window.close()
            print("analysis terminated")
            break
        
        if event == 'OK':
            window.close()
            print("analysis complete")
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
                data, headers = importer(values["datafile"],13)
                window["Status"].update("Data imported", text_color="lime green")
                window["Split by device"].update(disabled=False)
                            
                mode = values["Mode"]
                
                for i in range(1,33):
                    r_mins[i] = float(values["r_default"])
                
                for i in range(1,33):
                    startpoints[i] = int(values["start"])
                
            except FileNotFoundError:
                window["Status"].update("No file found at selected filepath",text_color="red")
                
            except IndexError:
                window["Status"].update("Wrong file format", text_color="red")
                
            except UnicodeDecodeError:
                window["Status"].update("Incorrect file format - must be csv", text_color="red")
            
            except Exception:
                window['Status'].update("Unknown error",text_color="red")
    
        if event == "Lock":
            if values["Lock"] == True:
                
                window["set_mode"].update(disabled=True)
                window["Mode"].update(disabled=True)
                window["r_default"].update(disabled=True)
                window["rdefault_set"].update(disabled=True)
                window["start_default"].update(disabled=True)
                window["startdefault_set"].update(disabled=True)
                window["parambrowse"].update(disabled=True)
                window["paramload"].update(disabled=True)
                window["Status"].update("Master settings locked", text_color="lime green")
                            
            if values["Lock"] == False:
                
                window["set_mode"].update(disabled=False)
                window["Mode"].update(disabled=False)
                window["r_default"].update(disabled=False)
                window["rdefault_set"].update(disabled=False)
                window["start_default"].update(disabled=False)
                window["startdefault_set"].update(disabled=False)
                window["parambrowse"].update(disabled=False)
                window["paramload"].update(disabled=False)
                window["Status"].update("Master settings unlocked", text_color="lime green")
                
        if event == "Split by device":
            from analysis_module import device_detect
            from analysis_module import device_split
            
            try:
                devices = device_detect(data,2)
                data_devices = device_split(data,devices,2)
                for i in range(1,33):
                    if i in devices:
                        window["cb"+str(i)].update(text_color = "#66FF00")
                    if i not in devices:
                        window["cb"+str(i)].update(text_color = "red")
                
                window["Status"].update("Data split by device",text_color="lime green")
                window["r_set"].update(disabled=False)
                window["tf_lfit"].update(disabled=False)
                window["check LFit"].update(disabled=False)
                
            except ValueError:
                print("Incorrect file structure - Expecting device numbers in column 3",text_color="red")
    
        for i in range(32):
            if event == "cb"+str(i+1):
                if values["cb"+str(i+1)] == True:
                    D.update({i+1:True})
                if values["cb"+str(i+1)] == False:
                    D.update({i+1:False})     
                       
        if event == "set_mode":
            mode = values["Mode"]
            window["Status"].update(str(mode) + " mode selected",text_color="lime green")
        
        if event == "rdefault_set":
            for i in range(1,33):
                r_mins[i] = float(values["r_default"])
                
            window["r_min"].update(values["r_default"])
                
        if event == "startdefault_set":
            for i in range(1,33):
                startpoints[i] = int(values["start_default"])
            
            window["start"].update(values["start_default"])
        
        if event == "paramload":
            # try:
                from analysis_module import importer
                params, param_headers = importer(values["paramcsv"],1)
                window["Status"].update("r_mins and start points imported", text_color="lime green")
                
                for i in range(len(params)):
                    row = params[i]
                    dev = int(float(row[0]))
                    r_min = float(row[1])
                    start = int(float(row[2]))
                    
                    r_mins[dev] = r_min
                    startpoints[dev] = start
                                                    
            # except FileNotFoundError:
            #     window["Status"].update("No file found at selected filepath",text_color="red")
                
            # except IndexError:
            #     window["Status"].update("Wrong file format", text_color="red")
                
            # except UnicodeDecodeError:
            #     window["Status"].update("Incorrect file format - must be csv", text_color="red")
            
            # except Exception:
            #     window['Status'].update("Unknown error",text_color="red")
        
        if event == "r_set":
            r_min = float(values["r_min"])
            window["Status"].update("Minimum r set to " + str(r_min),text_color="lime green")
            window["set_start"].update(disabled=False)
                            
        if event == "set_start":
            from analysis_module import LFit
        
            devs = []
            for i in D:
                if D[i] == True:
                    devs.append(i)
            
            if len(devs) == 0 or len(devs) > 1:
                window["Status"].update("Please select exactly one device",text_color="red")
            
            if len(devs) == 1:
                dev = int(float(devs[0]))
                i = devices.index(dev)
                dev_data = data_devices[i]
                
                x = []
                y = []
                for i in range(len(dev_data)):
                    row = dev_data[i]
                    x.append(float(row[0]))
                    if mode == "APC":
                        y.append(float(row[4]))
                    if mode == "ACC":
                        y.append(row[6])
                    
                start = int(values["start"])
            
                startpoints[dev] = start
                r_mins[dev] = r_min
        
                window["Status"].update("Start point for device " + str(dev) + " set to " + str(start),text_color="lime green")
    
                x2, y2, Y2, e, r, alpha, B, rejrate, numdelete = LFit(x,y,start,r_min)
                
                if r >= 0:
                    eol = 1.5
                else:
                    eol = 0.5
                
                Y0 = Y2[0]
                tf = (eol*Y0 - alpha)/B    
                
                plt.plot(x2,y2, linestyle = '-', marker = '.', label = 'Device {}'.format(dev))
                plt.plot(x2,Y2,color='r', label = 'Linear fit')
                
                plt.plot(x2,y2,color = 'white',alpha=0, label = 'r = {} \n tf = {} h'.format(np.round(r,3),int(round(tf,0))))
                plt.xlabel('Time (h)')
                if mode == "APC":
                    plt.ylabel('Current (mA)')
                if mode == "ACC":
                    plt.ylabel('Power (mW)')
                    
                plt.legend()
                plt.grid()
                plt.show()
                
                print("r = ", r)
                print("tf = ", tf)
                print("TEST cycles deleted = ", numdelete)
                print("Rejection rate = ", round(rejrate,2), " %")
                window["Add to plot"].update(disabled=False)
                window["Add to extrapolated plot"].update(disabled=False)
                window["show plot linear"].update(disabled=False)
            
        if event == "check LFit":
            colLabels = ["Device", "r_min", "start point"]
            cellText = []
            for i in range(1,33):
                r = r_mins[i]
                s = startpoints[i]
                cellText.append([i,r,s])
                
            fig, ax = plt.subplots()
            ax.set_axis_off()
            ax.table(cellText = cellText, colLabels=colLabels, cellLoc="center", loc="upper left")
            
            plt.show()
        
        if event == "tf_lfit":  
            from analysis_module import tf_linearfit
            mode = values["Mode"]
            xs, ys, Ys, es, rs, tfs, alphas, Bs = tf_linearfit(data_devices, startpoints, r_mins, mode)
                       
            LFit_data = []
            LFit_results = []
            for i in range(len(xs)):
                devx = xs[i]
                devy = ys[i]
                devY = Ys[i]
                deve = es[i]
                
                LFit_data.append([])
                LFit_results.append([devices[i],tfs[i],rs[i],alphas[i],Bs[i]])
                for j in range(len(devx)):
                    valuex = devx[j]
                    valuey = devy[j]
                    valueY = devY[j]
                    valuee = deve[j]
                    
                    LFit_data[i].append([valuex,devices[i],valuey,valueY,valuee])
            
            window["Status"].update("Linear fits completed",text_color="lime green")
            window["Export linear fits"].update(disabled=False)
        
        if event == "Export linear fits":
            from datetime import datetime
            Date = str(datetime.now())
            date_reformat = "{}{}{}{}{}".format(Date[8:10],Date[5:7],Date[2:4],Date[11:13],Date[14:16])
            file_reformat = values["datafile"].split(".csv")[0]
            
            metadata = [["Date/Time of analysis", Date], ["Mode", mode], ["Minimum r coefficents", r_mins],["Startpoints", startpoints]]
            
            if mode =="APC":
                headers_out1 = ["Elapsed_time (h)", "Device", "Current (mA)", "Linear Fit Current (mA)", "Y_error (mA)"]
            if mode =="ACC":
                headers_out1 = ["Elapsed_time (h)", "Device", "Power (mW)", "Linear Fit Power (mW)", "Y_error (mW)"]
            
            headers_out2 = ["Device", "Time to Failure (h)", "Correlation Coefficient, r", "Y-Intercept", "Slope"]
            
            
            with open('{}_LFit_data_{}.csv'.format(file_reformat, date_reformat), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(metadata)
                writer.writerows([[]])
                writer.writerows([["Data"], headers_out1])
                
                for i in range(len(LFit_data)):                
                    device = LFit_data[i]
                    writer.writerows(device)
            
            with open('{}_LFit_results_{}.csv'.format(file_reformat, date_reformat), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(metadata)
                writer.writerows([[]])
                writer.writerows([["Results"], headers_out2])
                
                writer.writerows(LFit_results)
            
            window["Status"].update("Data and results exported to current working directory", text_color = "lime green")
            
        # if event == "Add to plot":
            
        #     devs = []
        #     for i in D:
        #         if D[i] == True:
        #             devs.append(i)
            
        #     colors = sns.color_palette("hls",len(devs))
            
        #     for i in range(len(devs)):
        #         devindex = devices.index(devs[i])
                
        #         B = Bs[devindex]
        #         alpha = alphas[devindex]
        #         r = rs[devindex]
                
        #         devx = xs[devindex]
                
        #         devy = ys[devindex]
        #         firsty = devy[0]
        #         devy = [j/firsty for j in devy]
                
        #         devY = Ys[devindex]
    
        #         plt.plot(devx,devy,color= colors[i], linestyle = '-', marker = '.', label = 'Device {}'.format(devs[i]))
        #         #plt.plot(devx,devY, color =colors[i])
                
        #     plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
        #     plt.grid()
        #     plt.xlabel('Time (h)')
        #     if mode == "APC":
        #         plt.ylabel('Normalised Current (arb. units)')
        #     if mode == "ACC":
        #         plt.ylabel('Normalised Power (arb. units)')
        
        
        # if event == "Add to extrapolated plot":
            
        #     devs = []
        #     for i in D:
        #         if D[i] == True:
        #             devs.append(i)
            
        #     colors = sns.color_palette("hls",len(devs))
            
        #     for i in range(len(devs)):
        #         devindex = devices.index(devs[i])
                
        #         B = Bs[devindex]
        #         alpha = alphas[devindex]
        #         r = rs[devindex]
                
                
        #         devx = xs[devindex]
        #         firstx = devx[0]
                
        #         devY = Ys[devindex]
        #         firstY = devY[0]
                
        #         #devx = [i/firstx for i in devx]
        #         devY = [j/firstY for j in devY]
                
        #         Yextrapolate = []
        #         Xextrapolate = []
        #         if r>0:
        #             eol = 1.5
        #             if max(devY) < eol:
        #                 deltaX = (eol - alpha)/B - max(devx)
        #                 Xdivision = deltaX/1000
        #                 for k in range(0,1001):
        #                     Xextrapolate.append(max(devx)+ k*Xdivision)
        #                     Yextrapolate.append(Xextrapolate[k]*B + alpha)
        #                 plt.plot(Xextrapolate,Yextrapolate,color=colors[i],linestyle='dashed')
                        
        #         if r<0:
        #             eol = 0.5
        #             if min(devY) > eol:
        #                 deltaX = (eol - alpha)/B - max(devx)
        #                 Xdivison = deltaX/1000
        #                 for k in range(1,1001):
        #                     Xextrapolate.append(max(devx) + k*Xdivision)
        #                     Yextrapolate.append(Xextrapolate[k]*B + alpha)
                    
        #                 plt.plot(Xextrapolate,Yextrapolate,color=colors[i],linestyle='dashed')
                
                
        #         #plt.plot(xs[devindex],ys[devindex], linestyle = '-', marker = '.', label = 'Device {}'.format(devs[i]))
        #         plt.plot(devx,devY,color= colors[i], label = 'Device {}'.format(devs[i]))
                
        #     plt.legend(ncol=2, loc = 'center left', bbox_to_anchor=(1,0.5))
        #     plt.grid()
        #     plt.xlabel('Time (h)')
        #     if mode == "APC":
        #         plt.ylabel('Normalised Current (arb. units)')
        #     if mode == "ACC":
        #         plt.ylabel('Normalised Power (arb. units)')
        
        
        # if event == "show plot linear":
            
        #     plt.show()
            
    window.close()
   
    return

GUI2()