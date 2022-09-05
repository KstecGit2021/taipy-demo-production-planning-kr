import pandas as pd
import json

with open('data/fixed_variables_default.json', "r") as f:
    fixed_variables_default = json.load(f)

# Taipy Core의 코드는 아직 실행되지 않았습니다. csv 파일을 이런 식으로 읽습니다.
da_initial_demand = pd.read_csv('data/time_series_demand.csv')
da_initial_demand = da_initial_demand[['Year', 'Month', 'Demand_A', 'Demand_B']].astype(int)

da_initial_demand.columns = [col.replace('_', ' ') 
                            for col in da_initial_demand.columns]

da_initial_variables = pd.DataFrame({key: [fixed_variables_default[key]]
                                    for key in fixed_variables_default.keys() if 'Initial' in key})

# 아래 코드는 열 이름의 형식을 올바르게 지정하는 것입니다.
da_initial_variables.columns = [col.replace('_', ' ').replace('one', '1').replace('two', '2').replace('initial ', '')
                                for col in da_initial_variables.columns]
da_initial_variables.columns = [col[0].upper() +
                                col[1:] for col in da_initial_variables.columns]


da_data_visualisation_md = """
# 데이터 시각화

<|Expand here|expanded=False|expandable|

<|layout|columns=1 1 1|columns[mobile]=1|
<|
## 초기 재고

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Stock' in col]]}|table|show_all|width=445px|>
</center>
|>

<|
## 초기 생산

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Production' in col]]}|table|show_all|width=445px|>
</center>
|>

<|
## 구매한 자료

<center>
<|{da_initial_variables[[col for col in da_initial_variables.columns if 'Purchase' in col]]}|table|show_all|width=445px|>
</center>
|>
|>


## 다가오는 달의 수요

<center>
<|{da_initial_demand.round()}|table|width=fit-content|show_all|height=fit-content|>
</center>
|>

## 수요의 진화

<|{da_initial_demand}|chart|x=Month|y[1]=Demand A|y[2]=Demand B|width=100%|>
"""
