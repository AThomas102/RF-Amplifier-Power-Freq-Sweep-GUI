# -*- coding: utf-8 -*-
"""
Created on Thu May 26 17:12:15 2022

@author: AlexanderArnstein
"""

import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
import csv

sg.theme('DarkBlue4')

spin_list = tuple([str(i) for i in range(1,100)])

col1 = [[sg.Frame(layout = [
            
            [sg.Text("Data sets (temperatures) to analyse: ", size=(28,1)), sg.Spin(values=spin_list, size=(4,1), key="ds_spin", pad=6), sg.Button("Set", size=(8,1), key="set_ds_num")],
            
            [sg.Text("Choose data set: ", size=(14,1)), sg.Combo(values=(), size=(20,1), readonly=True, key="ds_combo")],
            
            [sg.Input("Input datafile", key ="datafile",size=(40,1)), sg.FileBrowse(size=(8,1)), sg.Button("Load", size=(8,1))],
            
            [sg.Text("Set SOAK temperature (°C) : ", size=(28,1)), sg.Input("", size=(6,1), key="soak_temp"), sg.Button("Set",size=(8,1), key="set_soak")]
                            
            ], title='Importing')],

        [sg.Frame(layout = [
             
            [sg.CBox('1',size=(2,1),key=('cb1'),enable_events=True),sg.CBox('2',size=(2,1),key=('cb2'),enable_events=True),sg.CBox('3',size=(2,1),key=('cb3'),enable_events=True),sg.CBox('4',size=(2,1),key=('cb4'),enable_events=True),sg.CBox('5',size=(2,1),key=('cb5'),enable_events=True),sg.CBox('6',size=(2,1),key=('cb6'),enable_events=True),sg.CBox('7',size=(2,1),key=('cb7'),enable_events=True),sg.CBox('8',size=(2,1),key=('cb8'),enable_events=True)],
            
            [sg.CBox('9',size=(2,1),key=('cb9'),enable_events=True),sg.CBox('10',size=(2,1),key=('cb10'),enable_events=True),sg.CBox('11',size=(2,1),key=('cb11'),enable_events=True),sg.CBox('12',size=(2,1),key=('cb12'),enable_events=True),sg.CBox('13',size=(2,1),key=('cb13'),enable_events=True),sg.CBox('14',size=(2,1),key=('cb14'),enable_events=True),sg.CBox('15',size=(2,1),key=('cb15'),enable_events=True),sg.CBox('16',size=(2,1),key=('cb16'),enable_events=True)],
            
            [sg.CBox('17',size=(2,1),key=('cb17'),enable_events=True),sg.CBox('18',size=(2,1),key=('cb18'),enable_events=True),sg.CBox('19',size=(2,1),key=('cb19'),enable_events=True),sg.CBox('20',size=(2,1),key=('cb20'),enable_events=True),sg.CBox('21',size=(2,1),key=('cb21'),enable_events=True),sg.CBox('22',size=(2,1),key=('cb22'),enable_events=True),sg.CBox('23',size=(2,1),key=('cb23'),enable_events=True),sg.CBox('24',size=(2,1),key=('cb24'),enable_events=True)],
            
            [sg.CBox('25',size=(2,1),key=('cb25'),enable_events=True),sg.CBox('26',size=(2,1),key=('cb26'),enable_events=True),sg.CBox('27',size=(2,1),key=('cb27'),enable_events=True),sg.CBox('28',size=(2,1),key=('cb28'),enable_events=True),sg.CBox('29',size=(2,1),key=('cb29'),enable_events=True),sg.CBox('30',size=(2,1),key=('cb30'),enable_events=True),sg.CBox('31',size=(2,1),key=('cb31'),enable_events=True),sg.CBox('32',size=(2,1),key=('cb32'),enable_events=True)],
            
            ],title= "Device Grid", key="Device Grid")],
    
        [sg.Frame(layout = [ 
            
            []
            
            ],title = "Graph plotting")]]

tab1 = [[sg.Frame(layout = [[sg.Column(col1)]],title="")]]

tab2 = [[sg.Text("Lock Master Settings"), sg.CBox('', default=True, key = ("Lock"), enable_events=True)],
        
        [sg.Frame(layout = [
       
            []            
                           
        ],title='')],
        ]

tab3 = [[sg.Text("This is how to use the analysis GUI....")]]

layout = [   #[sg.Menu(menu, tearoff=False)],
          
             [sg.TabGroup([[sg.Tab('Analysis', tab1), sg.Tab('Master Settings', tab2), sg.Tab('Help', tab3)]],key = "Tabs",enable_events=True,tab_background_color='White',selected_background_color='#0072c6', selected_title_color='White')],
                                       
             [sg.Button("OK",size=(7,1)), sg.Button('Cancel',size=(7,1)), sg.Button("Reset",size=(7,1)), sg.Text("Status",key="Status")]]
             

window = sg.Window("CSA Catapult - Reliability Test Analyser", icon = "CSA_icon.ico",resizable=True).Layout(layout)
                
buttonlist = []

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
    
    if event == "set_ds_num":
        end = int(values["ds_spin"])
        combo_list = tuple(str(i) for i in range(1,end+1))
        datasets = [[] for i in range(1,end+1)]
        
        window["ds_combo"].update(values=combo_list)
        
    if event == "Load":
        try:
            from analysis_module import importer
            data, headers = importer(values["datafile"],7)
            window["Status"].update("Data imported", text_color="lime green")
                                                
        # except FileNotFoundError:
        #     window["Status"].update("No file found at selected filepath",text_color="red")
            
        # except IndexError:
        #     window["Status"].update("Wrong file format", text_color="red")
            
        # except UnicodeDecodeError:
        #     window["Status"].update("Incorrect file format - must be csv", text_color="red")
        
        except Exception:
            window['Status'].update("Unknown error",text_color="red")    
        
    
    if event == "set_soak":
        soak_T = float(values["soak_temp"])
        print(soak_T)