# 데이터를 처리하기 위한 파이썬의 기본 패키지
from login.login import *
import pandas as pd

# 타이피 코어 import
import taipy as tp

# 내 파이썬 코드의 백엔드 가져오기 | 시나리오를 생성하려면 원본 파이프라인_cfg 및 시나리오_cfg가 필요합니다.
# fixed_variables_default는 고정 변수의 기본값으로 사용됩니다.
from config.config import fixed_variables_default, scenario_cfg, pipeline_cfg
from taipy.core.config.config import Config


# Taipy 프론트엔드에 유용한 기능 가져오기
from taipy.gui import Gui, Markdown, notify, Icon

# 내 파이썬 코드의 프론트엔드 가져오기 | 페이지 가져오기: compare_scenario_md 페이지, 시나리오_매니저_md 페이지, 데이터베이스_md 페이지
# *는 때때로 이 코드의 함수 및/또는 변수가 필요하기 때문에 사용됩니다.
# 
from pages.compare_cycles_md import *
from pages.compare_scenario_md import *
from pages.databases_md import *
from pages.data_visualization_md import *

# 임시 파일을 생성하기 위해 import
import pathlib


# 이 경로는 Datasouces 페이지에서 테이블을 다운로드할 수 있는 임시 파일을 만드는 데 사용됩니다.
# 
tempdir = pathlib.Path(".tmp")
tempdir.mkdir(exist_ok=True)
PATH_TO_TABLE = str(tempdir / "table.csv")

Config.configure_global_app(clean_entities_enabled=True)
tp.clean_all_entities()

cc_create_scenarios_for_cycle()

from pages.scenario_manager_md import *


###############################################################################
# 로그인
###############################################################################


def on_change_user_selector(state):
    global user_selector
    if state.selected_user == 'Create new user':
        state.login = ''
        state.dialog_new_account = True
    elif state.selected_user in [user[0] for user in user_selector]:
        state.login = state.selected_user

        if state.selected_user in state.user_in_session:
            state.dialog_user = False

            reinitialize_state_after_login(state)
        else:
            state.dialog_login = True

    else:
        notify(state, "Warning", "Unexpected error")


def reinitialize_state_after_login(state):
    scenarios = [s for s in tp.get_scenarios(
    ) if 'user' in s.properties and state.login == s.properties['user']]
    state.scenario_counter = len(scenarios)
    state.cs_show_comparaison = False
    state.password = ''
    update_scenario_selector(state, scenarios)

    if state.dialog_new_account:
        state.selected_scenario = None
        notify(state, 'info', 'Creating a new session')
        state.dialog_new_account = False
    else:
        if state.scenario_counter != 0:
            state.selected_scenario = state.scenario_selector[0][0]

        notify(state, 'info', 'Restoring your session')


def validate_login(state, id, action, payload):
    global user_selector, users

    # if the button pressed is "Cancel"
    if payload['args'][0] != 1:
        state.dialog_login = False
        state.dialog_new_account = False
    else:
        if state.dialog_new_account:
            if state.login in [user[0] for user in user_selector]:
                notify(state, 'error', 'This user already exists')
            elif state.login == '':
                notify(state, "Warning", "Please enter a valid login")
            elif state.login != '' and len(state.password) > 0:
                state.dialog_login = False
                state.dialog_new_account = False
                state.dialog_user = False

                users[state.login] = {}
                users[state.login]["password"] = encode(state.password)
                users[state.login]["last_visit"] = str(dt.datetime.now())

                json.dump(users, open('login/login.json', 'w'))
                reinitialize_state_after_login(state)

                state.user_selector = [
                    (state.login,
                     Icon(
                         'images/user.png',
                         state.login))] + state.user_selector
                user_selector = state.user_selector
                state.selected_user = state.login

                state.user_in_session += state.selected_user
        elif state.login in [user[0] for user in user_selector]:
            if test_password(users, state.login, state.password):
                state.dialog_login = False
                state.dialog_new_account = False
                state.dialog_user = False
                state.user_in_session += state.selected_user

                reinitialize_state_after_login(state)
            else:
                notify(state, "Warning", "Wrong password")

        else:
            notify(state, "Warning", "Unexpected error")


###############################################################################
# main_md
###############################################################################

# 메인 마크다운 페이지입니다. 여기에 메인 페이지에 포함된 다른 페이지가 있습니다.
# 시나리오_매니저_md, 비교_시나리오_md, 데이터베이스_md는 페이지 변수에 따라 보이게 됩니다.
# 이것이 'render' 매개변수의 목적입니다.
menu_lov = [
    ("Data Visualization",
     Icon(
         'images/chart_menu.svg',
         'Data Visualization')),
    ("Scenario Manager",
     Icon(
         'images/Scenario.svg',
         'Scenario Manager')),
    ("Compare Scenarios",
     Icon(
         'images/compare.svg',
         'Compare Scenarios')),
    ("Compare Cycles",
     Icon(
         'images/Cycle.svg',
         'Compare Cycles')),
    ('Databases',
     Icon(
         'images/Datanode.svg',
         'Databases'))]

main_md = login_md + """

<|menu|label=Menu|lov={menu_lov}|on_action=menu_fct|id=menu_id|>

<|part|render={page == 'Data Visualization'}|
""" + da_data_visualisation_md + """
|>

<|part|render={page == 'Scenario Manager'}|
""" + sm_scenario_manager_md + """
|>

<|part|render={page == 'Compare Scenarios'}|
""" + cs_compare_scenario_md + """
|>

<|part|render={page == 'Compare Cycles'}|
""" + cc_compare_cycles_md + """
|>

<|part|render={page == 'Databases'}|
""" + da_databases_md + """
|>

"""


###############################################################################
# 시나리오 생성/제출/처리를 위한 중요한 기능
###############################################################################

def update_scenario_selector(state, scenarios: list):
    """
    이 기능은 시나리오 선택기를 업데이트합니다. 
    새 시나리오를 만들 때 사용됩니다. 
    시나리오가 생성되면 이 목록에 (id,name)을 추가합니다.

    Args:
        scenarios (list): a list of tuples (scenario,properties)
    """

    state.scenario_selector = [(s.id, s.name) if not s.is_primary else (
        s.id, Icon('images/main.svg', s.name)) for s in scenarios]
    state.scenario_counter = len(state.scenario_selector)
    state.scenario_selector_two = state.scenario_selector.copy()

    sm_tree_dict[state.sm_selected_year][state.sm_selected_month] = state.scenario_selector


def make_primary(state):
    tp.set_primary(tp.get(state.selected_scenario))
    scenarios = [s for s in tp.get_scenarios(
    ) if 'user' in s.properties and state.login == s.properties['user']]
    update_scenario_selector(state, scenarios)
    state.selected_scenario_is_primary = True


def delete_scenario_fct(state):
    if tp.get(state.selected_scenario).is_primary:
        notify(
            state,
            "warning",
            "You can't delete the primary scenario of the month")
    else:
        tp.delete(state.selected_scenario)
        scenarios = [s for s in tp.get_scenarios(
        ) if 'user' in s.properties and state.login == s.properties['user']]
        update_scenario_selector(state, scenarios)

        if state.scenario_counter != 0:
            state.selected_scenario = state.scenario_selector[0][0]


def create_new_scenario(state):
    """
    이 기능은 cenario_manager_md 페이지에서 '만들기' 버튼을 눌렀을 때 사용합니다. 
    자세한 내용은 시나리오_매니저_md 페이지를 참조하세요. 
    다른 시나리오를 구성하고 작성하여 제출합니다.

    Args:
        state (_type_): the state object of Taipy
    """

    # 시나리오 카운터 업데이트
    state.scenario_counter += 1

    print("Creating scenario...")
    name = "Scenario " + dt.datetime.now().strftime('%d-%b-%Y') + " Nb : " + \
        str(state.scenario_counter)
    scenario = tp.create_scenario(scenario_cfg, name=name)
    scenario.properties['user'] = state.login

    # 모든 시나리오와 해당 속성을 가져옵니다.
    print("Getting properties...")
    scenarios = [s for s in tp.get_scenarios(
    ) if 'user' in s.properties and state.login == s.properties['user']]

    # 선택한 시나리오를 변경합니다. 새 시나리오는 선택한 시나리오입니다.
    # 
    state.selected_scenario = scenario.id

    # 시나리오 선택기를 업데이트합니다.
    print("Updating scenario selector...")
    update_scenario_selector(state, scenarios)

    # 이 시나리오를 제출
    print("Submitting it...")
    submit_scenario(state)


def catch_error_in_submit(state):
    """
    이 함수는 시나리오를 제출할 때 발생할 수 있는 오류를 잡는 데 사용됩니다. 
    오류가 포착되면 알림이 표시되고 오류를 방지하기 위해 변수가 변경됩니다. 
    오류는 고정 변수가 잘못 설정되면 실행 불가능하거나 
    무한한 문제가 발생할 수 있는 Cplex 모델의 솔루션에서 발생합니다.

    Args:
        state (_type_): the state object of Taipy
    """

    # 초기 생산량이 최대 생산 능력보다 높은 경우
    if state.fixed_variables["Initial_Production_FPA"] > state.fixed_variables["Max_Capacity_FPA"]:
        state.fixed_variables["Initial_Production_FPA"] = state.fixed_variables["Max_Capacity_FPA"]
        notify(
            state,
            "warning",
            "Value of initial production FPA is greater than max production A")

    # 초기 생산량이 최대 생산 능력보다 높은 경우
    if state.fixed_variables["Initial_Production_FPB"] > state.fixed_variables["Max_Capacity_FPB"]:
        state.fixed_variables["Initial_Production_FPB"] = state.fixed_variables["Max_Capacity_FPB"]
        notify(
            state,
            "warning",
            "Value of initial production FPB is greater than max production B")

    # 초기 재고가 최대 생산 능력보다 높은 경우
    if state.fixed_variables["Initial_Stock_RPone"] > state.fixed_variables["Max_Stock_RPone"]:
        state.fixed_variables["Initial_Stock_RPone"] = state.fixed_variables["Max_Stock_RPone"]
        notify(
            state,
            "warning",
            "Value of initial stock RP1 is greater than max stock 1")

    # 초기 재고가 최대 생산 능력보다 높은 경우
    if state.fixed_variables["Initial_Stock_RPtwo"] > state.fixed_variables["Max_Stock_RPtwo"]:
        state.fixed_variables["Initial_Stock_RPtwo"] = state.fixed_variables["Max_Stock_RPtwo"]
        notify(
            state,
            "warning",
            "Value of initial stock RP2 is greater than max stock 2")

    # 초기 생산이 최대 생산 능력보다 높은 경우
    # 
    if state.fixed_variables["Initial_Production_FPA"] + \
            state.fixed_variables["Initial_Production_FPB"] > state.fixed_variables["Max_Capacity_of_FPA_and_FPB"]:
                
        state.fixed_variables["Initial_Production_FPA"] = int(state.fixed_variables["Max_Capacity_of_FPA_and_FPB"] / 2)
        state.fixed_variables["Initial_Production_FPB"] = int(state.fixed_variables["Max_Capacity_of_FPA_and_FPB"] / 2)
        
        notify(
            state,
            "warning",
            "Value of initial productions is greater than the max capacities")


def submit_scenario(state):
    """
    이 기능은 선택한 시나리오를 제출합니다. '제출' 버튼을 누르거나 
    새 시나리오를 만들 때 사용됩니다. 오류가 있는지 확인한 다음 문제의 매개변수를 변경하고 
    시나리오를 제출합니다. 마지막으로 업데이트하려는 모든 변수를 업데이트합니다.

    Args:
        state (_type_): the state object of Taipy

    Returns:
        _type_: _description_
    """

    detect_inactive_session(state)

    # 시나리오에 제공될 매개변수에 오류가 있는지 확인합니다.
    # 
    catch_error_in_submit(state)

    # 시나리오 가져오기
    scenario = tp.get(state.selected_scenario)

    # 올바른 매개변수로 시나리오 설정
    scenario.fixed_variables.write(state.fixed_variables._dict)

    # 시나리오 실행
    tp.submit(scenario)

    # 업데이트하려는 모든 변수를 업데이트합니다(ch_results, pie_results 및 측정항목)
    # 
    update_variables(state)


def update_variables(state):
    """이 함수는 submit_scenario 또는 selected_scenario가 변경될 때만 사용됩니다. 업데이트하려는 모든 유용한 변수를 업데이트합니다.

    Args:
        state (_type_): the state object of Taipy
    """
    # 선택한 시나리오 가져오기
    scenario = tp.get(state.selected_scenario)

    # 결과 읽기
    state.ch_results = scenario.pipelines['pipeline'].results.read()
    state.pie_results = pd.DataFrame(
        {
            "values": state.ch_results.sum(axis=0),
            "labels": list(state.ch_results.columns)
        })

    state.sum_costs = state.ch_results['Total Cost'].sum()

    bool_costs_of_stock = [c for c in state.ch_results.columns
                           if 'Cost' in c and 'Total' not in c and 'Stock' in c]
    state.sum_costs_of_stock = int(state.ch_results[bool_costs_of_stock].sum(axis=1)\
                                                                        .sum(axis=0))

    bool_costs_of_BO = [c for c in state.ch_results.columns
                        if 'Cost' in c and 'Total' not in c and 'BO' in c]
    state.sum_costs_of_BO = int(state.ch_results[bool_costs_of_BO].sum(axis=1)\
                                                                  .sum(axis=0))


def create_chart(ch_results: pd.DataFrame, var: str):
    """데이터베이스" 페이지에서 볼 수 있는 차트 테이블을 생성/업데이트하는 함수입니다. 이
    함수는 "on_change" 함수에서 선택한 그래프가 변경될 때 차트를 변경하는 데 사용됩니다.

    Args:
        ch_results (pd.DataFrame): the results database that comes from the state
        var (str): the string that has to be found in the columns that are going to be used to create the chart table

    Returns:
        pd.DataFrame: the chart with the proper columns
    """
    if var == 'Cost':
        columns = ['index'] + [col for col in ch_results.columns if var in col]
    else:
        columns = [
            'index'] + [col for col in ch_results.columns if var in col and 'Cost' not in col]

    chart = ch_results[columns]
    return chart


def on_change(state, var_name, var_value):
    """이 함수는 상태 변수의 변경이 완료될 때 호출됩니다. 
    변경 사항이 확인되면 변경된 변수에 따라 작업을 생성할 수 있습니다.

    Args:
        state (State): the state object of Taipy
        var_name (str): the changed variable name
        var_value (obj): the changed variable value
    """
    # 변경된 변수가 선택한 시나리오인 경우
    if var_name == "selected_scenario" and var_value is not None:
        scenario = tp.get(state.selected_scenario)

        state.selected_scenario_is_primary = scenario.is_primary

        if scenario.results.is_ready_for_reading:
            # 시나리오가 변경되면 슬라이더를 올바른 값으로 설정합니다.
            # 
            fixed_temp = tp.get(state.selected_scenario).fixed_variables.read()
            state_fixed_variables = state.fixed_variables._dict.copy()
            for key in state.fixed_variables.keys():
                state_fixed_variables[key] = fixed_temp[key]
            state.fixed_variables = state_fixed_variables
            # I update all the other useful variables
            update_variables(state)

    if var_name == "dialog_user" or var_name == "dialog_login" or var_name == "dialog_new_account" or var_name == "user_selected":
        with open('login/login.json', "r") as f:
            state.users = json.load(f)
        state.user_selector = [(user,Icon('images/user.png', user))
                                for user in state.users.keys()]
        
        state.user_selector += [('Create new user', Icon('images/new_account.png', 'Create new user'))]

    # 그래프가 선택되거나 시나리오가 변경되고 '데이터베이스' 페이지에 있는 경우
    # 또는 데이터베이스 페이지로 이동하면 차트 테이블을 업데이트해야 합니다.
    if (var_name == 'sm_graph_selected' or var_name == "selected_scenario" and state.page =='Databases')\
        or (var_name == 'page' and var_value == 'Databases'):

        str_to_select_chart = None

        if state.sm_graph_selected == 'Costs':
            str_to_select_chart = 'Cost'
            state.cost_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Purchases':
            str_to_select_chart = 'Purchase'
            state.purchase_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Productions':
            str_to_select_chart = 'Production'
            state.production_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Stocks':
            str_to_select_chart = 'Stock'
            state.stock_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Back Order':
            str_to_select_chart = 'BO'
            state.bo_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Product FPA':
            str_to_select_chart = 'FPA'
            state.fpa_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Product FPB':
            str_to_select_chart = 'FPB'
            state.fpb_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Product RP1':
            str_to_select_chart = 'RP1'
            state.rp1_data = create_chart(state.ch_results, str_to_select_chart)
            
        elif state.sm_graph_selected == 'Product RP2':
            str_to_select_chart = 'RP2'
            state.rp2_data = create_chart(state.ch_results, str_to_select_chart)

        state.chart = create_chart(state.ch_results, str_to_select_chart)
        state.partial_table.update_content(state, da_create_display_table_md(str_to_select_chart.lower() + '_data'))


        # '데이터베이스' 페이지에 있는 경우 임시 csv 파일을 만들어야 합니다.
        # 
        if state.page == 'Databases':
            state.d_chart_csv_path = PATH_TO_TABLE
            state.chart.to_csv(state.d_chart_csv_path, sep=',')


# 초기 페이지는 "시나리오 관리자" 페이지입니다.
page = "Data Visualization"


def menu_fct(state, var_name: str, fct, var_value):
    """Functions that is called when there is a change in the menu control

    Args:
        state (_type_): the state object of Taipy
        var_name (str): the changed variable name
        var_value (_type_): the changed variable value
    """

    # 올바른 페이지를 렌더링하기 위해 state.page 변수의 값을 변경하십시오.
    # 
    try:
        state.page = var_value['args'][0]
    except BaseException:
        print("Warning : No args were found")

    # 'Databases' 페이지에서만 선택할 수 있는 sm_graph_selected의 'All' 옵션에 대한 보안
    # 
    if state.page != 'Databases' and state.sm_graph_selected == 'All':
        state.sm_graph_selected = 'Costs'


##########################################################################
# 상태 및 초기 값 생성
##########################################################################
gui = Gui(page=Markdown(main_md), css_file='main')
partial_table = gui.add_partial(da_display_table_md)

# 테이블의 너비와 높이 값
width_table = "100%"
height_table = "100%"

# 차트의 너비와 높이 값
width_chart = "100%"
height_chart = "60vh"


def initialize_variables():
    # 차트의 초기값
    global scenario, pie_results, sum_costs, sum_costs_of_stock, sum_costs_of_BO, scenario_counter,\
        cost_data, stock_data, purchase_data, production_data, fpa_data, fpb_data, bo_data, rp1_data, rp2_data, chart, ch_results,\
        chart, scenario_selector, selected_scenario, selected_scenario_is_primary, scenario_selector_two, selected_scenario_two,\
        fixed_variables

    fixed_variables = fixed_variables_default

    scenario = None
    pie_results = pd.DataFrame(
        {
            "values": [1] * len(list(ch_results.columns)),
            "labels": list(ch_results.columns)
        }, index=list(ch_results.columns)
        )
    
    sum_costs = 0
    sum_costs_of_stock = 0
    sum_costs_of_BO = 0
    sum_costs_of_BO = 0
    scenario_counter = 0

    cost_data = create_chart(ch_results, 'Cost')
    purchase_data = create_chart(ch_results, 'Purchase')
    production_data = create_chart(ch_results, 'Production')
    stock_data = create_chart(ch_results, 'Stock')
    bo_data = create_chart(ch_results, 'BO')
    fpa_data = create_chart(ch_results, 'FPA')
    fpb_data = create_chart(ch_results, 'FPB')
    rp1_data = create_chart(ch_results, 'RP1')
    rp2_data = create_chart(ch_results, 'RP2')

    chart = ch_results[['index',
                        'Purchase RP1 Cost',
                        'Stock RP1 Cost',
                        'Stock RP2 Cost',
                        'Purchase RP2 Cost',
                        'Stock FPA Cost',
                        'Stock FPB Cost',
                        'BO FPA Cost',
                        'BO FPB Cost',
                        'Total Cost']]


    # 페이지에 표시될 선택기
    scenario_selector = []
    selected_scenario = None

    selected_scenario_is_primary = False

    scenario_selector_two = scenario_selector.copy()
    selected_scenario_two = None


initialize_variables()

pd.read_csv('data/time_series_demand copy.csv').to_csv('data/time_series_demand.csv')

if __name__ == "__main__":
    gui.run(title="Production planning",
    		host='0.0.0.0',
    		port=os.environ.get('PORT', '5050'),
    		dark_mode=False,
            use_reloader=False)
else:
    app = gui.run(title="Production planning",
                  dark_mode=False,
                  run_server=False)
