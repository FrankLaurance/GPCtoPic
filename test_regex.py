
import re

re_celsius = re.compile(r"-?[1-9]\d*.\d*|0\.\d*[1-9]\d* °C")
m = "Equilibrate at 50.00 °C"
matches = re.findall(re_celsius, m)
print(f"Matches: {matches}")
try:
    if matches:
        val = float(matches[0])
        print(f"Float value: {val}")
except ValueError as e:
    print(f"Error: {e}")
