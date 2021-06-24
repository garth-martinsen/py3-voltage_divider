# vd_gui.py

import PySimpleGUI as sg
import re
import os
import voltage_divider as vdr

# global variables
#max_mw = 0
#path = ''


def get_resistor_file_path(values):
    print("in function: get_resistor_file_path")
    path = sg.popup_get_file("Select correct File",
                             file_types=(('CSV', '*.csv'),),
                             initial_folder=os.getcwd()
                             )
    return path


def get_candidates(values):
    path = values["path"]
    vin1 = values["Vin_1"]
    print(f'get_candidates called. Values for path: {path} and Vin: {vin1}')
    candidates = vdr.compute(vin1, path)
    print(f'Returned {len(candidates)} candidates')
    window["candidate_table"].update(values=candidates)


input_layout = [[
                sg.Text("Vin"), sg.Input("", size=(7, 1), key="Vin_1"),
                sg.Button("Resistors"), 
                sg.Input("", size=(80, 1), key="path"),
                sg.Button("Compute"),
                ]]
# VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")

headings = ["Vin", "V1", "V2", "Deviance", "R1", "R2", "Pow1_mw","Pow2_mw","A2D"]
table_layout = [[sg.Table(values=[], headings=headings, num_rows=6,
                          auto_size_columns=False, key='candidate_table',
                          alternating_row_color='Grey',
                          col_widths=list(map(lambda x:2 * (len(x) + 1), headings)),  # noqa: E501
                          hide_vertical_scroll=True)]]
output_layout = [[sg.Column(table_layout, scrollable=True, size=(800, 110))]]

input_frame = sg.Frame("Inputs", input_layout, size=(5, 1), visible=True)
output_frame = sg.Frame("Outputs", output_layout, size=(5, 1), visible=True)
layout = [[input_frame]], [[output_frame]]


window = sg.Window("Voltage Divider", layout, font="Courier 14")
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == "Resistors":
        path = get_resistor_file_path(values)
        window["path"].update(path)
    elif event == "Compute":
        print(f'Getting ready to call vdr.compute with:{values}')
        get_candidates(values)
