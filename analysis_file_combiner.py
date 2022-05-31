# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 11:04:00 2022

@author: AlexanderArnstein
"""

def file_combiner():
    import PySimpleGUI as sg
    sg.theme("DarkBlue4")
    
    tab1 = [    [sg.Input("Input data file 1", key ="datafile1",size=(40,1)), sg.FileBrowse(size=(8,1)), sg.Button("Load",key="Load1", size=(8,1))],
            
                [sg.Text("+",size=(56,1),justification="center")],
            
                [sg.Input("Input data file 2", key ="datafile2",size=(40,1)), sg.FileBrowse(size=(8,1)), sg.Button("Load",key="Load2", size=(8,1))],
                
                [sg.Button("Combine data files", key="Combine", size=(22,1))],
                
                [sg.Button("Export data file", key= "Export", size=(22,1))],
                
                ]
    
    tab2 = [[sg.Text("Add some information on how to use this GUI")]]
    
    layout = [[sg.TabGroup([[sg.Tab("Combiner", tab1)], [sg.Tab("Help", tab2)]])],
              
              [sg.Button("Ok",size=(7,1)), sg.Button('Cancel',size=(7,1)), sg.Button("Reset",size=(7,1)), sg.Text("Status",key="Status")]]
    
    window = sg.Window("Reliability Test file combiner").Layout(layout)
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == "Ok" or event == "Cancel":
            window.close()
            break
        
        if event == "Load1":
            from analysis_module import importer
            data1, headers1 = importer(values["datafile1"],1)
            window["Status"].update("Data file 1 imported",text_color="lime green")
    
        if event == "Load2":
            from analysis_module import importer
            data2, headers2 = importer(values["datafile2"],1)
            window["Status"].update("Data file 2 imported",text_color="lime green")
        
        if event == "Combine":
            from analysis_module import time_to_int
            from analysis_module import time_to_string
            
            time_col1 = []
            
            for i in range(len(data1)):
                row = data1[i]
                time = row[2]
                
                time = time_to_int(time)
                time_col1.append(time)
                    
            end_time = time_col1[-1]
            
            for i in range(len(data2)):        
                row = data2[i]
                time = row[2]
                
                time = time_to_int(time)
                time = time + end_time
                time = time_to_string(time)
                
                row[2] = time
                data2[i] = row
                
            data3 = data1 + data2
            
            window["Status"].update("Data files combined",text_color="lime green")
            
        if event == "Export":
            import csv
            from datetime import datetime
            
            data_out = headers1 + data3
            
            Date = str(datetime.now())
            date_reformat = "{}{}{}{}{}".format(Date[8:10],Date[5:7],Date[2:4],Date[11:13],Date[14:16])
            file_reformat = values["datafile1"].split(".csv")[0]
            
            with open("{}_combined_{}.csv".format(file_reformat,date_reformat), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(data_out)
                
            window["Status"].update("Combined files exported to current working directory",text_color="lime green")     
           
    window.close()
    
    return