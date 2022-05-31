# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:29:13 2022

@author: AlexanderArnstein
"""

import PySimpleGUI as sg
sg.theme("DarkBlue4")

tab1 =    [[sg.Frame(layout = [
            
                [sg.Button("Combine data files",key="Combine",size=(22,1))]], title="")],
             
            [sg.Frame(layout = [
                
                [sg.Button("GUI1",size=(22,1)), sg.Button("GUI2",size=(22,1)), sg.Button("GUI3",size=(22,1)), sg.Button("GUI4",size=(22,1))]], title="")],
            
            ]

tab2 = [[sg.Text("This is how to use the analysis GUI....")]]

layout =    [[sg.TabGroup([[sg.Tab('Launcher', tab1), sg.Tab('Help', tab2)]],key = "Tabs",enable_events=True,tab_background_color='White',selected_background_color='#0072c6', selected_title_color='White')],
             
             [sg.Button("Ok",size=(7,1)), sg.Button('Cancel',size=(7,1)), sg.Button("Reset",size=(7,1)), sg.Text("Status",key="Status")]]

window = sg.Window("Reliability Test Launcher").Layout(layout)

while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Ok" or event == "Cancel":
        window.close()
        break
    
    if event == "Combine":
        from analysis_file_combiner import file_combiner
        file_combiner()
        
    if event == "GUI1":
        from analysis_GUI_1 import GUI1
        GUI1()
        
    if event == "GUI2":
        from analysis_GUI_2 import GUI2
        GUI2()

window.close()