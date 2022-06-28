from data.create_data import time_series_to_csv
from config.config import scenario_cfg

from taipy.core import taipy as tp

import datetime as dt
import pandas as pd

cc_data = pd.DataFrame(
    {
        'Date': [dt.datetime(2021, 1, 1)],
        'Cycle': [dt.date(2021, 1, 1)],
        'Cost of Back Order': [0],
        'Cost of Stock': [0]
    })

cc_show_comparison = False
cc_layout = {'barmode': 'stack', 'margin': {"t": 20}}
cc_creation_finished = False


def cc_create_scenarios_for_cycle():
    date = dt.datetime(2021, 1, 1)
    month = date.strftime('%b')
    year = date.strftime('%Y')

    current_month = dt.date.today().strftime('%b')
    current_year = dt.date.today().strftime('%Y')

    while month != current_month or year != current_year:
        date += dt.timedelta(days=15)
        month = date.strftime('%b')
        year = date.strftime('%Y')

        if month != current_month or year != current_year:

            time_series_to_csv(
                nb_months=12,
                mean_A=840,
                mean_B=760,
                std_A=96,
                std_B=72,
                amplitude_A=108,
                amplitude_B=144)

            name = f"Scenario {date.strftime('%d-%b-%Y')}"
            scenario = tp.create_scenario(scenario_cfg, creation_date=date, name=name)
            tp.submit(scenario)


def update_cc_data(state):
    all_scenarios = tp.get_primary_scenarios()

    dates = []
    cycles = []
    costs_of_back_orders = []
    costs_of_stock = []

    all_scenarios_ordered = sorted(
        all_scenarios,
        key=lambda x: x.creation_date.timestamp())  # delete?
    for scenario in all_scenarios_ordered:

        results = scenario.results.read()

        if results is not None:
            date_ = scenario.creation_date
            dates.append(date_)
            cycles.append(dt.date(date_.year, date_.month, 1))

            # creation of sum_costs_of_stock metrics
            bool_costs_of_stock = [c for c in results.columns
                                   if 'Cost' in c and 'Total' not in c and 'Stock' in c]
            sum_costs_of_stock = int(results[bool_costs_of_stock].sum(axis=1)\
                                                                 .sum(axis=0))

            # creation of sum_costs_of_BO metrics
            bool_costs_of_BO = [c for c in results.columns
                                if 'Cost' in c and 'Total' not in c and 'BO' in c]
            sum_costs_of_BO = int(results[bool_costs_of_BO].sum(axis=1)\
                                                           .sum(axis=0))

            costs_of_back_orders.append(sum_costs_of_BO)
            costs_of_stock.append(sum_costs_of_stock)

    state.cc_data = pd.DataFrame({'Date': dates,
                                  'Cycle': cycles,
                                  'Cost of Back Order': costs_of_back_orders,
                                  'Cost of Stock': costs_of_stock})

    state.cc_show_comparison = True


cc_compare_cycles_md = """
# Compare cycles


<center>
<|Compare Cycles|button|on_action={update_cc_data}|>
</center>

<|part|render={cc_show_comparison}|
<|Table|expanded=False|expandable|

<center>
<|{cc_data}|table|width=fit-content|>
</center>

|>

## Evolution of costs

<|{cc_data}|chart|type=bar|x=Cycle|y[1]=Cost of Back Order|y[2]=Cost of Stock|layout={cc_layout}|width=100%|height=600|>
|>

"""
