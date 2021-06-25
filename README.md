# py3-voltage_divider
A python3 script with GUI to select the best choice of resistors to meet power-dissipation and voltage dividing specs. 
This would be useful if one wanted to measure a voltage which exceeds the allowable A2D input voltage (Arduino Micro Controller?).
It requires the user to provide a csv file containing resistor values for each wattage level eg: quarter_watt.csv and half_watt.csv. Each
file contains the resistance values on hand with that wattage.
The GUI is started with python vd_gui.py . User selects the resistor file by wattage which sets the Resistor max_mw to the proper value in mW.
Then the User enters the input voltage, Vin. A RETURN or a TAB will trigger the call to the model, voltage_divider.py, and display a list of the top
5 candidate designs. The top candidate is the closest fit for a v2 voltage <= 4.95 volts. Resistor power dissipation levels are displayed to ensure
that they do not exceed the max_mw displayed. (No hot or exploding resistors!). List comprehensions are used to generate all possible pairs. A "meets_specs
function is used to filter out pairs. A lambda function is used to sort the candidates that meet power and divider specs in the order of best fit for
the target v2.
An image of the schematic for a Simple Voltage divider is displayed to give the table values meaning.
