# file: vd_gui.py

import PySimpleGUI as sg
import voltage_divider as vdr
import os

#  -----global variables-----
values = dict()
proj_dir = os.getcwd()  #  If your resistor files are not in proj_dir, you need to make changes.


def get_max_mw(path):
    """
    returns 250 or 500 mw, etc depending on the filename.
    If another set of resistors exist with different power ratings,
    A file should be created with a title reflecting the rating.
    """
    if path.find('quarter') > -1:
        max_mw = 250
    elif path.find('half') > -1:
        max_mw = 500
    else:
        max_mw = 0
        msg = path + ' is not a resistor file. Try again by pressing \
        Resistors Button and selecting a resistor csv file.'
        sg.popup_ok_cancel(msg)
    return max_mw


def get_resistor_file_path():
    # print("in function: get_resistor_file_path")
    path = sg.popup_get_file("Select correct File",
                             file_types=(('CSV', '*.csv'),),
                             initial_folder=proj_dir
                             )
    if path:
        window["path"].update(path)
        window["max_mw"].update(get_max_mw(path))
    return path


def get_candidates():
    candidates = vdr.compute(values["Vin_1"], values["path"])
    window["candidate_table"].update(values=candidates)


#  ----------Layout GUI----------------------------

input_group = [[sg.Button("Resistors"),
                sg.Input("", size=(75, 1), key="path"),
                sg.Text("Vin"), sg.Input("", size=(7, 1), enable_events=True, key="Vin_1"),
                sg.Button("Compute")]]

headings = ["Vin", "V1", "V2", "Deviance", "R1_ohms",
            "R2_ohms", "P1_mw", "P2_mw", "A2D"]
table = sg.Table(values=[], headings=headings, num_rows=6,
                 auto_size_columns=False, key='candidate_table',
                 justification='c',
                 alternating_row_color='Grey',
                 col_widths=list(map(lambda x: 2 * (len(x) + 1), headings)),
                 hide_vertical_scroll=True)
output_group = [[table]]

schematic_frm = sg.Frame(
    "Schematic",
    [[sg.Image(filename=proj_dir + "/Schematic.png")]],)

"""
All constraints are readonly, 
future decision: Should the V2 constraints be set in gui or configured as globals?
Using the GUI to set them might be instructive to the new hobbyist to see how they
limit the number of choices for a final design.
"""
limit_frm = sg.Frame("Constraints",
    [[sg.Input(vdr.v2_lo, size=(5, 1), readonly=True,),
      sg.Text("<  V2  <"),
      sg.Input(vdr.v2_hi, size=(5, 1), readonly=True,),
      sg.Text("Max_mw "),
      sg.Input("", size=(5, 1), key="max_mw", readonly=True),
      sg.Button("Exit"), ]])



input_frame = [[sg.Frame("Inputs", input_group)]]
output_frame = [[sg.Frame("Outputs", output_group, element_justification='left')]]
layout = [[input_frame, output_frame, schematic_frm, limit_frm, ]]


window = sg.Window("Voltage Divider", layout, return_keyboard_events=True, 
                   size=(750, 500), finalize=True) #  resizable=True,

"""
 handles all events in the Event loop except sg.WinClosed and 'Exit'
 """
handler = {
    'Resistors': get_resistor_file_path,
    'Tab:805306377': window["Compute"].click,
    'Return:603979789': window["Compute"].click,
    'Compute': get_candidates}

# print(f'----------------------Window size: {window.Size}--------------')

while True:
    event, values = window.read()
    #  print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    else:
        handler.get(event, lambda: None)()  # if event is not in handler, defaults to None() which does nothing 

