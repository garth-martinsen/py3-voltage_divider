# file: voltage_divider2.py

import re
from collections import namedtuple
import csv

# ----------------namedtuples----------------------------------
VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
DesignGoals = namedtuple("DesignGoals", "vin v2_hi v2_lo max_mw")

# --------------global variables-------------------------------
v2_hi = 4.95  # a2d = 1012
v2_lo = 1.00  # a2d = 205
max_mw = 0   # set in process


def load_resistor_set(path):
    """
    Loads the set of resistors available for use into a set. The best 
    Fit can be used in the selected voltage divider.
    """
    resistorSet = set()
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                resistorSet.add(int(row[0]))
                line_count += 1
        # print(f'Loaded {line_count-1} resistors.')
        return resistorSet


def build_voltage_divider(design_goals, r1, r2):
    """
    Returns a VoltageDivider candidate. This function is only called
    if specs for power dissipation and design_goals are met for r1,r2,
    as determined by function design_meets_specs
    """
    fract = r2 / (r1 + r2)
    vin = design_goals.vin
    v1 = vin * (1 - fract)
    v2 = design_goals.vin * fract
    p1 = int(v1**2 / r1 * 1000)  # mW
    p2 = int(v2**2 / r2 * 1000)  # mW
    a2d = int(f'{v2/5*1023:.0f}')
    dev = design_goals.v2_hi - v2
    # size for display
    vin = float(f'{vin:4.2f}')
    v1 = float(f'{v1:4.2f}')
    v2 = float(f'{v2:4.2f}')
    dev = float(f'{dev:6.4f}')
    # VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
    return VD(vin, v1, v2, dev, r1, r2, p1, p2, a2d)


def get_max_mw(path):
    """
    returns 250 or 500 mw, etc depending on the filename.
    If another set of resistors exist with different power ratings,
    A file should be created with a title reflecting the rating.
    """
    global max_mw
    q = re.findall('quarter', path)
    h = re.findall('half', path)
    if len(q) > 0:
        max_mw = 250
    elif len(h) > 0:
        max_mw = 500
    return max_mw


def design_meets_specs(design_goals, r1, r2):
    """
    A candidate consists of two resistors, r1,r2. There are many candidates,
    but only some meet the specs. This function is used to filter out 
    candidates that do not meet specs. Given the design_goals and r1,r2, this 
    function computes the fraction, then uses that and vin to compute V2, 
    power1, power2 and try these against specs. 
    Returns True if meets specs:
    """
    # print(f'Design Goals: {design_goals}')
    vin = design_goals.vin
    fraction = r2 / (r1 + r2)
    v2 = vin * fraction
    V2_Ok = design_goals.v2_lo <= v2 <= design_goals.v2_hi
    pow1_Ok = ((vin - v2)**2 / r1) * 1000 < design_goals.max_mw
    pow2_OK = (v2**2 / r2 * 1000) < design_goals.max_mw
    return V2_Ok and pow1_Ok and pow2_OK


def find_choices(design_goals, resistorSet):
    """
    Returns a sorted list of 5 VoltageDivider candidates that meet
    design_goals. Resistor pairs that do not meet specs are filtered out.
    Any of the choices returned could be selected,
    but the one with the smallest deviance from desired_v2 should be used 
    as the best design. 
    """

    # list comprehension is used to filter out non-compliant candidates
    choices = [build_voltage_divider(design_goals, r1, r2)
               for r1 in resistorSet
               for r2 in resistorSet
               if design_meets_specs(design_goals, r1, r2)]
    # print(f'Sorting {len(choices)} choices')
    return sorted(list(choices), key=lambda vdr: vdr.Deviance)


def compute(Vin, path):
    """
    Entry point from GUI. Vin = input Voltage to be measured,  # noqa: E101
    path = path to the resistor set csv file. max_mw is computed from path.
    The desired V2 is v2_hi 
    so any value in range (4.65 < v2 < 4.95) meets specs. v2_hi and v2_lo
    are global variables so they are easily changed at the top of the script.
    Returns top 5 candidates
    """
    global v2_hi
    global v2_lo
    max_mw = get_max_mw(path)
    resistor_set = load_resistor_set(path)
    design_goals = DesignGoals(float(Vin), v2_hi, v2_lo, max_mw)
    choices = find_choices(design_goals, resistor_set)
    # print(choices)
    end = min(5, len(choices))
    return choices[0:end]


