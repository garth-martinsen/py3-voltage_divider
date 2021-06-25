# py3-voltage_divider
A **python3** script with **GUI** to select the best choice of resistors to meet power-dissipation and voltage dividing specs. 
This would be useful if one wanted to measure a voltage which exceeds the allowable A2D input voltage (Arduino Micro Controller?).
It requires the user to provide a **csv file** containing resistor values for each wattage level eg: **quarter_watt.csv** and half_watt.csv. Each
file contains the resistance values on hand with that wattage.
The GUI is started with **python vd_gui.py** . **User selects** the resistor csv file by wattage which sets the Resistor max_mw to the proper value in mW.
Then the **User enters** the input voltage, Vin. A **RETURN or a TAB** will trigger the call to the model in voltage_divider.py, which returns a list of candidate designs. The **GUI** displays the sorted list in a **Table with appropriate headers**.
5 candidate designs. The top candidate is the closest fit for a v2 voltage <= 4.95 volts. Resistor power dissipation levels are displayed to ensure
that they do not exceed the max_mw displayed. (No hot or exploding resistors!). List comprehensions are used to generate all possible pairs. A "meets_specs
function is used to filter out pairs. A lambda function is used to sort the candidates that meet power and divider specs in the order of best fit for
the target v2. **Equations used in model:** Power_dissipated =Vr**2/r, v2= vin * r2/(r1+r2)
An **image of the schematic** for a Simple Voltage divider is displayed to give the table values meaning.
![image](https://user-images.githubusercontent.com/6226186/123393078-99d77180-d552-11eb-819e-d7f9e5c6373c.png)

