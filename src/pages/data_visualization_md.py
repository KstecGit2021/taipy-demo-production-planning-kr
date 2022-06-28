import pandas as pd
import json

with open('data/fixed_variables_default.json', "r") as f:
    fixed_variables_default = json.load(f)

# no code from Taipy Core has been executed yet, we read the csv file this way
da_initial_demand = pd.read_csv('data/time_series_demand.csv')
da_initial_demand = da_initial_demand[['Year', 'Month', 'Demand_A', 'Demand_B']].astype(int)

da_initial_demand.columns = [col.replace('_', ' ') 
                            for col in da_initial_demand.columns]

da_initial_variables = pd.DataFrame({key: [fixed_variables_default[key]]
                                    for key in fixed_variables_default.keys() if 'Initial' in key})

# The code below is to correctly format the name of the columns
da_initial_variables.columns = [col.replace('_', ' ').replace('one', '1').replace('two', '2').replace('initial ', '')
                                for col in da_initial_variables.columns]
da_initial_variables.columns = [col[0].upper() +
                                col[1:] for col in da_initial_variables.columns]


da_data_visualisation_md = """
# Data Visualization

<|Expand here|expanded=False|expandable|

<|layout|columns=1 1 1|columns[mobile]=1|
<|
## Initial stock

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Stock' in col]]}|table|show_all|width=445px|>
</center>
|>

<|
## Initial Production

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Production' in col]]}|table|show_all|width=445px|>
</center>
|>

<|
## Incoming Purchased Material

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Purchase' in col]]}|table|show_all|width=445px|>
</center>
|>
|>


## Demand of the upcoming months

<center>
<|{da_initial_demand.round()}|table|width=fit-content|show_all|height=fit-content|>
</center>
|>

## Evolution of the demand

<|{da_initial_demand}|chart|x=Month|y[1]=Demand A|y[2]=Demand B|width=100%|>
"""
