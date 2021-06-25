# vd_gui.py

import PySimpleGUI as sg
import os
import voltage_divider as vdr
import re

# global variables
# max_mw = 0
# path = ''


def get_max_mw(path):
    """
    returns 250 or 500 mw, etc depending on the filename.
    If another set of resistors exist with different power ratings,
    A file should be created with a title reflecting the rating.
    """
    q = re.findall('quarter', path)
    h = re.findall('half', path)
    if len(q) > 0:
        max_mw = 250
    elif len(h) > 0:
        max_mw = 500
    return max_mw


def get_resistor_file_path(values):
    # print("in function: get_resistor_file_path")
    path = sg.popup_get_file("Select correct File",
                             file_types=(('CSV', '*.csv'),),
                             initial_folder=os.getcwd()
                             )
    if path:
        window["max_mw"].update(get_max_mw(path))
    return path


def get_candidates(values):
    path = values["path"]
    vin1 = values["Vin_1"]
    # print(f'get_candidates called(path: {path} and Vin: {vin1})')
    candidates = vdr.compute(vin1, path)
    # print(f'Returned {len(candidates)} candidates')
    window["candidate_table"].update(values=candidates)


input_layout = [[
                sg.Button("Resistors"),
                sg.Input("", size=(80, 1), key="path"),
                sg.Text("Vin"), sg.Input("", size=(7, 1), key="Vin_1"),
                sg.Button("Compute"),
                ]]
# VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
root = os.getcwd()
headings = ["Vin", "V1", "V2", "Dev", "R1_ohms",
            "R2_ohms", "P1_mw", "P2_mw", "A2D"]
table_layout = [[sg.Table(values=[], headings=headings, num_rows=6,
                          auto_size_columns=False, key='candidate_table',
                          alternating_row_color='Grey',
                          col_widths=list(map(lambda x: 2 * (len(x) + 1), headings)),  # noqa: E501
                          hide_vertical_scroll=True), sg.Text("Max_mw "),
                sg.Input("", size=(5, 1), key="max_mw"), ]]
schematic = [[sg.Image(filename=root + "/Schematic.png",
                       size=(335, 435), visible=True,)]]  # key="Schematic",
output_layout = [[sg.Column(table_layout, scrollable=True, size=(1000, 110))]]

input_frame = sg.Frame("Inputs", input_layout, visible=True)
output_frame = sg.Frame("Outputs", output_layout, visible=True)
layout = [[[[input_frame]], [[output_frame]], [[schematic]]]]

# sg.Debug("Debug")


window = sg.Window("Voltage Divider", layout,
                   font="Courier 14", return_keyboard_events=True,
                   resizable=True)
# sg.show_debugger_window(location=(0, 0))

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == "Resistors":
        path = get_resistor_file_path(values)
        window["path"].update(path)
    elif event in ("Tab:805306377", "Return:603979789"):
        print("Either a tab or returnKey has been entered")
        window["Compute"].click()
    elif event == "Compute":
        # print(f'Getting ready to call vdr.compute with:{values}')
        get_candidates(values)
    # print(event, values)