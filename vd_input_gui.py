# vd_input_gui.py

import voltage_divider as vdr
import PySimpleGUI as sg
import re


def populate(window, filename):
    """
    This is a throw-away method. I am using it to perfect my layout.
    """
    window.read()
    window['path_1'](filename)
    window['Stage_1']('Design Goals:')

    Vin = float(window['Vin_1'].get())
    V2 = float(window['V2_1'].get())
    fract0 = V2/Vin
    fract1 = float(f'{fract0:6.5f}')
    tol = float(window['Tol_1'].get())
    v=re.findall('quarter',filename)
    u=re.findall('half',filename)
    if len(v) >0:
        r_mw = 250
    elif len(u)>0:
        r_mw=500
    window['Vin_1'](Vin)
    window['V1_1'](Vin - V2)
    window['V2_1'](V2)
    window['fract_1'](fract1)
    window['Tol_1'](tol)
    window['Resistors_1']('')
    window['R_mW_1'](r_mw)
    window['Stage_2']('Final Product:')
    """
    window['Vin_2'](25)
    window['V1_2']( 20.243)
    window['V2_2'](4.757)
    window['fract_2'](0.19028)
    window['Dev_2'](-0.00572)
    window['R1_R2_2'](f'(2000,470)')
    window['P1_P2_2']('(208,48)')
    window['a2d_2'](973)

    """


def load_data(fd):
    """
    FinalDesign = namedtuple("FinalDesign", "Vin V1 V2 resistor_mw actual_fraction R1 R2 deviance P1_mw P2_mw Max_A2D_V2")  # noqa: E221, E501

    """
    V1 = float(f'{fd.V1:6.3f}')
    V2 = float(f'{fd.V2:6.3f}')
    fract = float(f'{fd.actual_fraction:6.5f}')
    Dev = float(f'{fd.deviance:6.5f}')
    R1 = int(f'{fd.R1:6.0f}')
    R2 = int(f'{fd.R2:6.0f}')
    P1 = int(f'{fd.P1_mw:4.0f}')
    P2 = int(f'{fd.P2_mw:4.0f}')
    Pow = (P1,P2)
    Res =(R1,R2)
    a2d = int(f'{fd.Max_A2D_V2:4.0f}')

    window['Vin_2'](fd.Vin)
    window['V1_2'](V1)
    window['V2_2'](V2)
    window['fract_2'](fract)
    window['Dev_2'](Dev)
    window['Resistors_ohms_2'](Res)
    window['Power_mw_2'](Pow)
    window['a2d_2'](a2d)
  


mydata=0
sg.theme('Dark Brown 1')

select_path =[[sg.Text("Path to resistor*.csv file: "), sg.Input(size=(70,1),key='path_1')]]


headings1 = ["Stage", "Vin", "V1", "V2", "fract", "Tol", "Resistors", "R_mW",  ]
header1 = [[ [ sg.Text(f'{h:^13}', size=(14, 1)) for h in headings1] ]]
headings2 = ["Stage", "Vin", "V1", "V2", "fract", "Dev", "Resistors_ohms", "Power_mw",  ]
header2 = [[ [ sg.Text(f'{h:^13}', size=(14, 1)) for h in headings2] ]]

input_rows1 = [[sg.Input(size=(15, 1), key=col + '_1', pad=(0, 0),)
               for col in headings1]for row in range(1)]
input_rows2 = [[sg.Input(size=(15, 1), key=col + '_2', pad=(0, 0),)
               for col in headings2]for row in range(1)]
a2d_row = [[sg.Text("A2d count when Vin at target: "), sg.Input(size=(15,1), key="a2d_2")]]

layout = [[select_path]]
layout += header1 + input_rows1
layout += header2 + input_rows2
layout += [[a2d_row]]
layout += [[sg.Button('Defaults'), sg.Button('Compute'), sg.Button('Exit')]]

window = sg.Window("Voltage Divider", layout, font='Courier 12')
window.read()
filename = sg.popup_get_file('Path to resistor*.csv file: ', 
                            initial_folder = "/Users/garth/Programming/python3/VD2/data",)

populate(window, filename)
while True:
    event, values = window.read()
    print('Got return values from voltage_divider: ', mydata)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Compute':
        # TODO remove when vdr.compute(...) is working
        pathname = str(window['path_1'].get())
        vin1=  float(window['Vin_1'].get())
        v2=    float(window['V2_1'].get())
        tol=   float(window['Tol_1'].get())
        r_mw = int(window['R_mW_1'].get())
        print('Calling vdr.compute() with args: ',pathname, ',',
               vin1,',', v2,',', tol,',', r_mw)
        print(type(pathname),type(vin1),type(v2),type(tol),type(r_mw))
        
        mydata = vdr.compute(pathname, vin1, v2, tol, r_mw)

        if mydata:
            load_data(mydata)
       

    print(event, values)


print(event, values)

window.close()



