#!/usr/bin/env python
"""
| *author:* Johannes Röttenbacher
| *created:* 22.05.2023

Investigate temperature measurements towards their dependency on velocity.
Hypothesis: Higher speeds cause a better air flow through the MeteoTracker resulting in better readings of the temperature sensor.
Strategy: Use measurements during the late afternoon (15 - 16 local time) on a clear sky day with little to no wind and compare them according to the recording speed.
Maybe a more windy/well mixed day would be better for this scenario with overcast sky to avoid local heating effects of the city landscape.
Do both and check if there are differences.


"""
# %% import modules
import meteohautnah as mh
import pandas as pd
import numpy as np

# %% read in data


# %% select date and time