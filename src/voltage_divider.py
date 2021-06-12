
import csv
import os
from collections import namedtuple

"""
Given a voltage, Vin, that is too high to sample with an 
Arduino A2D (5V max). Design a voltage divider that will produce a 
sampling voltage, V2, with a dynamic range : 0 <= V2 < 5 volts. 
The circuit has current flowing from Vin thru R1 and R2 to Ground. 
The resisters should be sized to avoid self destruction due to power 
radiated as heat. Facts: 
The power radiated, Pr,  from a resister, r, is computed by:  
      Pr = Vr**2/r  where Vr=voltage dropped, r = resistance.
Due to Kirkoff's voltage law, the Voltages, V1 and V2, dropped across 
the respective resistors will sum up to Vin. Current, i, 
thru both resistors is : 
      i = Vin/(r1+r2)   because resistors in series, r = r1+r2
V1 and V2 are computed using V = r*i: 
      V1 = r1 * Vin/(r1+r2) 
      V2 = r2 * Vin/(r1+r2) 
To compute the value of Vin just divide V2 by fract 
      Vin = V2 / fract  where fract = r2/(r1+r2)

Usage: prepare files, by wattage, of comma-separated-values (csv) 
(Actually only a single value, the resistance, is needed so no commas 
in the file see data/resistor_quarter.csv for example) 
(eg: resistors_quarter.csv and resistors_half.csv and store them in the data 
directory for quarterWatt and halfWatt resisters respectively. 
In a Python session import the module:
        import voltage_divider as vdr
call vdr.main(path), where path is the path to resistors_<size>.csv file; 
You will be prompted for: Input Voltage (Vin), Sampling Voltage(V2), resistor 
wattage, and how much tolerance from the desired fraction V2/Vin you will 
allow. Depending on the tolerance, you will receive a list of resistor 
combinations that will produce the desired result. Always select one that 
meets the following: V2 < 5.0, or you will saturate the A2D for every 
voltage >5.0 . (You cannot get an A2D count greater than 1023 for a 
10 bit- 5 volt A2D, for any voltage > 5 you will get 1023 until you 
burn out your A2D). If you want to protect your Arduino from this, put
a 5.1V zener in parallel with R2 to ground.
    """


VD = namedtuple("VD", "R1 R2 fraction power1_mw power2_mw diff")  # noqa: E501
DesignGoals = namedtuple("DesignGoals", "Vin V1 V2 resistor_mw target_fraction min_r1 min_r2  tolerance")  # noqa: E221, E501
FinalDesign = namedtuple("FinalDesign", "Vin V1 V2 resistor_mw actual_fraction R1 R2 deviance P1_mw P2_mw Max_A2D_V2")  # noqa: E221, E501


def data_dir():
    csv = os.getcwd()[0:-3]+ 'data'
    print(f'csv files for resistors are in directory: {csv}')
    os.chdir(csv)
    files = os.listdir()
    [print(csv + '/'+ f) for f in files if f.startswith('resistors') and f.endswith('csv')]
    


def get_design_parameters():
    """
Prompts the user for some values, then computes other values.
    Then constructs and returns an instance of DesignGoals.
    """
    vin = float(input('Enter Vin:'))
    # desired voltage input to A2D should be < 5.0
    v2 = float(input('Enter desired V2:'))
    print('Enter wattage of resistors:')
    rw = float(input())  # watts
    print('Enter tolerance on fraction:')
    tol = float(input())

    v1 = vin - v2
    fract = v2 / vin
    # find the minimum lead resistance that will not self destruct.
    r1min = v1**2 / rw  # P=I*E P<= V**2/r, so r >= V**2/P
    # find the minimum load resistance that will not self destruct.
    r2min = v2**2 / rw
    return DesignGoals(vin, v1, v2, rw * 1000, fract, r1min, r2min, tol)


def build_voltage_divider(design_goals, r1, r2):
    """
    Returns a VoltageDivider candidate. This function is only called 
    if specs for power dissipation and design_goals are met for r1,r2, 
    as determined by function fraction_meets_specs
    """
    fract = r2 / (r1 + r2)
    v1 = design_goals.Vin * (1 - fract)
    v2 = design_goals.Vin * fract
    p1 = v1**2 / r1 * 1000  # mW
    p2 = v2**2 / r2 * 1000  # mW
    return VD(r1, r2, fract, p1, p2,
                          fract - design_goals.target_fraction)


def load_resistor_set(path):
    """
Loads the set of resistors available for use into a set. The best Combination 
of two of these will be used in the selected voltage divider. 
"""
    resistorSet = set()
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                resistorSet.add(int(row[0]))
                line_count += 1
        print(f'Processed {line_count} lines.')
        return resistorSet


def fract(r1, r2):
    """
Computes the fraction of the Vin voltage that will be dropped across r2, 
given the inputs of resistance r1 , and of resistance r2. One can use this
to compute voltage drops across each resistor:  V1= Vin * (1-fract) 
V2 = Vin * fract. ( by Kirkoff's Voltage law)
"""
    return r2 / (r1 + r2)


def fraction_meets_specs(design_goals, r1, r2):
    """
    Returns True if the fraction is lessThan 
    design_goals.target_fraction and the abs(diff) is less 
    than design_goals.tolerance allowed.
    """
    diff = design_goals.target_fraction - fract(r1, r2)
    return diff > 0 and abs(diff) < design_goals.tolerance


def find_choices(design_goals, resistorSet):
    """
Returns a sorted list of VoltageDivider candidates that meet 
design_goals and power dissipation specs. Resistors that do not meet 
the Power dissipation limit are filtered out and will not be found in 
any of the candidates. Any of the choices returned could be selected, 
but the one with a fraction closest to and less than the desired 
fraction should be used as the best design. That means there is exactly
one best choice. it will be the first choice in the returned list.
    """
    # list comprehensions are used to filter out small resistors 
    r1_set = [r for r in resistorSet if r > design_goals.min_r1]
    r2_set = [r for r in resistorSet if r > design_goals.min_r2]
    # list comprehension is used to filter out non-compliant candidates
    choices = [build_voltage_divider(design_goals, r1, r2)
               for r1 in r1_set
               for r2 in r2_set
               if fraction_meets_specs(design_goals, r1, r2)]
    return sorted(list(choices), key=lambda vdr: vdr.diff,
                           reverse=True)


def print_formatted_design_parameters(dp):
    """in the display version of designParameter fields limit decimal places: 
    Vin:3,V1:3 V2:3  resistor_mw:0  
    target_fraction:5 min_r1:0 min_r2:0 tolerance:3
    """
    print(DesignGoals(float(f'{dp.Vin:7.2f}'),
                      float(f'{dp.V1:7.2f}'),
                      float(f'{dp.V2:7.2f}'),
                      int(f'{dp.resistor_mw:7.0f}'),
                      float(f'{dp.target_fraction:7.5f}'),
                      int(f'{dp.min_r1:7.0f}'),
                      int(f'{dp.min_r2:7.0f}'),
                      float(f'{dp.tolerance:7.5f}')))


def print_formatted_voltage_divider(vd):
    """in the display version of VoltageDivider fields: R1 R2 fraction 
    power1_mw power2_mw diff, fraction and diff: 5 decimal places 
    and all else are ints"""
    print(VD(int(f'{vd.R1:7.0f}'),
             int(f'{vd.R2:7.0f}'),
             float(f'{vd.fraction:7.5f}'),
             int(f'{vd.power1_mw:7.0f}'),
             int(f'{vd.power2_mw:7.0f}'),
             float(f'{vd.diff:7.5f}')))
# "R1 R2 fraction power1_mw power2_mw diff")


def print_formatted_final_design(bd, dp):
    vin = dp.Vin
    v2 = vin * bd.fraction
    v1 = vin - v2
    a2dcount = v2 / 5 * 1023
    """
    # FinalDesign ... "Vin V1 V2 resistor_mw actual_fraction R1 R2 
    deviance P1_mw P2_mw Max_A2D_V2") 
    """
    fd = FinalDesign(vin, v1, v2, dp.resistor_mw, bd.fraction, bd.R1,
                     bd.R2, bd.diff, bd.power1_mw, bd.power2_mw,
                     a2dcount)
    print(FinalDesign(float(f'{fd.Vin:7.3f}'),
                      float(f'{fd.V1:7.3f}'),
                      float(f'{fd.V2:7.3f}'),
                      int(f'{fd.resistor_mw:7.0f}'),
                      float(f'{fd.actual_fraction:7.5f}'),
                      int(f'{bd.R1:7.0f}'),
                      int(f'{bd.R2:7.0f}'),
                      float(f'{bd.diff:7.5}'),
                      float(f'{fd.P1_mw:7.0f}'),
                      float(f'{fd.P2_mw:7.0f}'),
                      int(f'{a2dcount:7.0f}')))


def main(path):
    """
    Loads resistor set from csv file at path. Computes DesignGoals 
    after getting user input. Builds VoltageDivider Candidates from 
    resistors that meet specs for power dissipation and DesignGoals. 
    Prints out a list of candidates sorted from smallest to largest diff
    andselects the one with the smallest deviation from the 
    desired fraction which will be the one with v2 closest to 5.0v """

    resistorSet = load_resistor_set(path)

    design_goals = get_design_parameters()
    print('****************Candidates****************************')
    choicez = find_choices(design_goals, resistorSet)
    for c in choicez:
        print_formatted_voltage_divider(c)
    print(f' Selecting the best choice from \
        {len(choicez)} Candidates: ')
    bd = choicez[0]
    print('****************Best Design****************************')
    print_formatted_voltage_divider(bd)
    print('From Specs: ')
    print_formatted_design_parameters(design_goals)
    print('Actual Design: ')
    print_formatted_final_design(bd, design_goals)
