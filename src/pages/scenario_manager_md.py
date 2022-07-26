from pages.annex_scenario_manager.chart_md import ch_chart_md, ch_choice_chart, ch_show_pie, ch_layout_dict, ch_results
from pages.annex_scenario_manager.parameters_md import pa_parameters_md, pa_param_selector, pa_param_selected, pa_choice_product_param, pa_product_param

from taipy.gui.gui_actions import notify
from taipy.gui import Icon
import taipy as tp

import datetime as dt



def remove_scenario_from_tree(scenario, sm_tree_dict: dict):
    """This function finds the scenario in the tree and removes it

    Args:
        scenario (Scenario): the scenario to be deleted from the tree
        sm_tree_dict (dict): the tree dict from which the scenario has to be deleted from

    Returns:
        tree: the tree without the scenario
    """
    # This will be the cycle keys that will be dropped if they contain no
    # scenario
    cycle_keys_to_pop = []

    # We explore our 2-level tree
    for cycle, scenarios_ in sm_tree_dict.items():
        for scenario_id, scenario_name in scenarios_:
            if scenario_id == scenario.id:
                # Remove the scenario that has the same id from the tree
                sm_tree_dict[cycle].remove((scenario_id, scenario_name))

                # Add the cycle to the cycles to drop if it is empty
                if len(sm_tree_dict[cycle]) == 0:
                    cycle_keys_to_pop += [cycle]
                print("------------- Scenario found and deleted -------------")
                break

    # Remove the empty cycles
    for cycle in cycle_keys_to_pop:
        sm_tree_dict.pop(cycle)
    return sm_tree_dict

sm_tree_dict = {}

def create_sm_tree_dict(scenarios, sm_tree_dict: dict = None):
    """This function creates a tree dict from a list of scenarios. The levels of the tree are:
    year/month/scenario

    Args:
        scenarios (list): a list of scenarios
        sm_tree_dict (dict, optional): the tree gathering all the scenarios. Defaults to None.

    Returns:
        tree: the tree created to classify the scenarios
    """
    print("Creating tree dict...")
    if sm_tree_dict is None:
        # Initialize the tree dict if it is not already initialized
        sm_tree_dict = {}

    # Add all the scenarios that are in the list
    for scenario in scenarios:
        # Create a name for the cycle
        date = scenario.creation_date
        year = f"{date.strftime('%Y')}"
        period = f"{date.strftime('%b')}"

        # Add the cycle if it was not already added
        if year not in sm_tree_dict:
            sm_tree_dict[year] = {}
        if period not in sm_tree_dict[year]:
            sm_tree_dict[year][period] = []

        # Append a new entry with the scenario id and the scenario name
        scenario_name = (
            Icon(
                'images/main.svg',
                scenario.name) if scenario.is_primary else scenario.name)
        sm_tree_dict[year][period] += [(scenario.id, scenario_name)]

    return sm_tree_dict



def create_time_selectors():
    """This function creates the time selectors that will be displayed on the GUI and it is also creating 
    the tree dict gathering all the scenarios.

    Returns:
        dict: the tree dict gathering all the scenarios
        list: the list of years
        list: the list of months
    """
    all_scenarios = tp.get_scenarios()
    all_scenarios_ordered = sorted(
        all_scenarios,
        key=lambda x: x.creation_date.timestamp())

    sm_tree_dict = create_sm_tree_dict(all_scenarios_ordered)

    if sm_current_year not in list(sm_tree_dict.keys()):
        sm_tree_dict[sm_current_year] = {}
    if sm_current_month not in sm_tree_dict[sm_current_year]:
        sm_tree_dict[sm_current_year][sm_current_month] = []

    sm_year_selector = list(sm_tree_dict.keys())
    sm_month_selector = list(sm_tree_dict[sm_selected_year].keys())

    return sm_tree_dict, sm_year_selector, sm_month_selector


def change_sm_month_selector(state):
    """This function is called when the user changes the year selector. It updates the selector shown on the GUI
    for the month selector and is calling the same function for the scenario selector.
    

    Args:
        state (State): all the GUI variables
    """
    state.sm_month_selector = list(
        state.sm_tree_dict[state.sm_selected_year].keys())

    if state.sm_selected_month not in state.sm_month_selector:
        state.sm_selected_month = state.sm_month_selector[0]

    change_scenario_selector(state)


def change_scenario_selector(state):
    """This function is called when the user changes the month selector. It updates the selector shown on the GUI
    for the scenario selector.
    

    Args:
        state (State): all the GUI variables
    """
    state.scenario_selector = list(
        state.sm_tree_dict[state.sm_selected_year][state.sm_selected_month])
    state.scenario_selector_two = state.scenario_selector.copy()
    if len(state.scenario_selector) > 0:
        state.selected_scenario = state.scenario_selector[0][0]

    if (state.sm_selected_month != sm_current_month or state.sm_selected_year !=
            sm_current_year) and state.sm_show_config_scenario:
        notify(state, "info", "This scenario is historical, you can't modify it")
        state.sm_show_config_scenario = False


sm_scenario_manager_md = """
# Scenario Manager

<|layout|columns=8 4 4 3|columns[mobile]=1|
<layout_scenario|
<|layout|columns=1 1 3|columns[mobile]=1|
<|
Year

<|{sm_selected_year}|selector|lov={sm_year_selector}|dropdown|width=100%|on_change=change_sm_month_selector|>
|>

<|
Month

<|{sm_selected_month}|selector|lov={sm_month_selector}|dropdown|width=100%|on_change=change_scenario_selector|>
|>

<|
Scenario

<|{selected_scenario}|selector|lov={scenario_selector}|dropdown|value_by_id|width=18rem|>
|>
|>
|layout_scenario>

<graph|
**Graph**
<br/>
<|{sm_graph_selected}|selector|lov={sm_graph_selector}|dropdown|>
|graph>

<toggle_chart|
<center>
Pie/Line chart
<|{ch_show_pie}|toggle|lov={ch_choice_chart}|value_by_id|active={not 'Product ' in sm_graph_selected}|>
</center>
|toggle_chart>

<button_configure_scenario|
<br/>
<br/>
<|{sm_show_config_scenario_name}|button|on_action=show_config_scenario_action|active={sm_selected_month == sm_current_month and sm_selected_year == sm_current_year}|>
|button_configure_scenario>
|>

<|part|render={sm_show_config_scenario}|
""" + pa_parameters_md + """
|>

<|part|render={not(sm_show_config_scenario)}|
""" + ch_chart_md + """
|>
"""

# Button for configuring scenario
sm_show_config_scenario_name = "Hide configuration"
sm_show_config_scenario = True


def show_config_scenario_action(state):
    state.sm_show_config_scenario = not state.sm_show_config_scenario
    state.sm_show_config_scenario_name = "Hide configuration" if state.sm_show_config_scenario else "Configure scenario"


sm_current_month = dt.date.today().strftime('%b')
sm_current_year = dt.date.today().strftime('%Y')

sm_selected_year = sm_current_year
sm_selected_month = sm_current_month

sm_tree_dict, sm_year_selector, sm_month_selector = create_time_selectors()

# Choose the graph to display
sm_graph_selector = [
    'Costs',
    'Purchases',
    'Productions',
    'Stocks',
    'Back Order',
    'Product RP1',
    'Product RP2',
    'Product FPA',
    'Product FPB']
sm_graph_selected = sm_graph_selector[0]
