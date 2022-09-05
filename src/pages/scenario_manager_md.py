from pages.annex_scenario_manager.chart_md import ch_chart_md, ch_choice_chart, ch_show_pie, ch_layout_dict, ch_results
from pages.annex_scenario_manager.parameters_md import pa_parameters_md, pa_param_selector, pa_param_selected, pa_choice_product_param, pa_product_param

from taipy.gui.gui_actions import notify
from taipy.gui import Icon
import taipy as tp

import datetime as dt



def remove_scenario_from_tree(scenario, sm_tree_dict: dict):
    """이 함수는 트리에서 시나리오를 찾아 제거합니다.

    Args:
        scenario (Scenario): the scenario to be deleted from the tree
        sm_tree_dict (dict): the tree dict from which the scenario has to be deleted from

    Returns:
        tree: the tree without the scenario
    """
    # 시나리오가 포함되지 않은 경우 삭제되는 주기 키입니다.
    # 
    cycle_keys_to_pop = []

    # We explore our 2-level tree
    for cycle, scenarios_ in sm_tree_dict.items():
        for scenario_id, scenario_name in scenarios_:
            if scenario_id == scenario.id:
                # 같은 id를 가진 시나리오를 트리에서 제거
                sm_tree_dict[cycle].remove((scenario_id, scenario_name))

                # 비어 있는 경우 삭제할 주기에 주기를 추가합니다.
                if len(sm_tree_dict[cycle]) == 0:
                    cycle_keys_to_pop += [cycle]
                print("------------- Scenario found and deleted -------------")
                break

    # 빈 주기 제거
    for cycle in cycle_keys_to_pop:
        sm_tree_dict.pop(cycle)
    return sm_tree_dict

sm_tree_dict = {}

def create_sm_tree_dict(scenarios, sm_tree_dict: dict = None):
    """이 기능은 시나리오 목록에서 트리 사전을 생성합니다. 트리 수준은 다음과 같습니다.
    연도/월/시나리오
    
    Args:
        scenarios (list): 시나리오 목록
        sm_tree_dict (dict, optional): 모든 시나리오를 수집하는 트리. 기본값은 없음입니다.

    Returns:
        tree: t시나리오를 분류하기 위해 생성된 트리
    """
    print("트리 딕셔너리 생성 중...")
    if sm_tree_dict is None:
        # 아직 초기화되지 않은 경우 트리 딕셔너리를 초기화합니다.
        sm_tree_dict = {}

    # 목록에 있는 모든 시나리오 추가
    for scenario in scenarios:
        # 주기의 이름을 만듭니다.
        date = scenario.creation_date
        year = f"{date.strftime('%Y')}"
        period = f"{date.strftime('%b')}"

        # 아직 추가되지 않은 경우 주기를 추가합니다.
        if year not in sm_tree_dict:
            sm_tree_dict[year] = {}
        if period not in sm_tree_dict[year]:
            sm_tree_dict[year][period] = []

        # 시나리오 ID와 시나리오 이름으로 새 항목 추가
        scenario_name = (
            Icon(
                'images/main.svg',
                scenario.name) if scenario.is_primary else scenario.name)
        sm_tree_dict[year][period] += [(scenario.id, scenario_name)]

    return sm_tree_dict



def create_time_selectors():
    """이 기능은 GUI에 표시될 시간 선택기를 생성하고 모든 시나리오를 수집하는 트리 딕셔너리도 생성합니다.
    

    Returns:
        dict: 모든 시나리오를 수집하는 트리 딕셔너리
        list: 연도 목록
        list: 월 목록
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
    """이 함수는 사용자가 연도 선택기를 변경할 때 호출됩니다. 
    월 선택기에 대해 GUI에 표시된 선택기를 업데이트하고 시나리오 선택기에 대해 동일한 기능을 호출합니다.
    

    Args:
        state (State): 모든 GUI 변수
    """
    state.sm_month_selector = list(
        state.sm_tree_dict[state.sm_selected_year].keys())

    if state.sm_selected_month not in state.sm_month_selector:
        state.sm_selected_month = state.sm_month_selector[0]

    change_scenario_selector(state)


def change_scenario_selector(state):
    """이 함수는 사용자가 월 선택자를 변경할 때 호출됩니다. 시나리오 선택기에 대한 GUI에 표시된 선택기를 업데이트합니다.
   
    

    Args:
        state (State): 모든 GUI 변수
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
# 시나리오 매니저

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

# 시나리오 구성 버튼
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

# 표시할 그래프 선택
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
