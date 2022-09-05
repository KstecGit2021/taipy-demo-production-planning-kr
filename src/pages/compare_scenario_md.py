import taipy as tp
import pandas as pd


cs_compare_scenario_md = """
# 시나리오 비교

<|layout|columns=3 3 1|columns[mobile]=1|

<layout_scenario|
**Scenario 1**

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



<layout_scenario|
**Scenario 2**

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

<|{selected_scenario_two}|selector|lov={scenario_selector_two}|dropdown|value_by_id|width=18rem|>
|>
|>
|layout_scenario>


<br/>
<br/>
<br/>
<center>
<|Compare scenario|button|on_action=compare_scenarios|active={len(scenario_selector)>1}|>
</center>
|>

<|part|render={cs_show_comparaison and len(scenario_selector)>=2}|
<|layout|columns=1 1 1|columns[mobile]=1|
<|
**Representation**

<|{cs_compar_graph_selected}|selector|lov={cs_compar_graph_selector}|dropdown=|value_by_id|>
|>

<br/>
<br/>
<center>
**Total cost of scenario 1:** *<|{str(int(sum_costs/1000))+' K'}|>*
</center>

<br/>
<br/>
<center>
**Total cost of scenario 2:** *<|{str(int(cs_sum_costs_two/1000))+' K'}|>*
</center>
|>



<|part|render={cs_compar_graph_selected=='Metrics'}|
<br/>
<br/>
<|layout|columns=1 1|columns[mobile]=1|
<|{cs_comparaison_metrics_df[cs_comparaison_metrics_df['Metrics']=='BO Cost']}|chart|type=bar|x=Metrics|y[1]=Scenario 1: BO Cost|y[2]=Scenario 2: BO Cost|color[2]=#2b93db|width={width_chart}|height={cs_height_bar_chart}|layout={ch_layout_dict}|>

<|{cs_comparaison_metrics_df[cs_comparaison_metrics_df['Metrics']=='Stock Cost']}|chart|type=bar|x=Metrics|y[1]=Scenario 1: Stock Cost|y[2]=Scenario 2: Stock Cost|color[1]=#ff7f0e|color[2]=#ff9a41|width={width_chart}|height={cs_height_bar_chart}|layout={ch_layout_dict}|>
|>
|>

<|part|render={cs_compar_graph_selected=='Costs'}|
<|{cs_comparaison_df}|chart|x=index|y[1]=Scenario 1 Cost|y[2]=Scenario 2 Cost|color[2]=#1f77b4|line[2]=dash|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|>
|>
<|part|render={cs_compar_graph_selected=='Purchases'}|
<|{cs_comparaison_df}|chart|x=index|y[1]=Scenario 1 Purchase|y[2]=Scenario 2 Purchase|color[2]=#1f77b4|line[2]=dash|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|>
|>
<|part|render={cs_compar_graph_selected=='Productions'}|
<|{cs_comparaison_df}|chart|x=index|y[1]=Scenario 1 Production|y[2]=Scenario 2 Production|color[2]=#1f77b4|line[2]=dash|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|>
|>
<|part|render={cs_compar_graph_selected=='Stocks'}|
<|{cs_comparaison_df}|chart|x=index|y[1]=Scenario 1 Stock|y[2]=Scenario 2 Stock|color[2]=#1f77b4|line[2]=dash|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|>
|>
<|part|render={cs_compar_graph_selected=='Back Order'}|
<|{cs_comparaison_df}|chart|x=index|y[1]=Scenario 1 BO|y[2]=Scenario 2 BO|color[2]=#1f77b4|line[2]=dash|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|>
|>
|>

"""


def compare_scenarios(state):
    """이 기능은 사용자가 다른 메트릭에서 선택한 두 가지 시나리오를 비교하고 비교 그래프에 대한 데이터 프레임을 채웁니다.

    Args:
        state (State): 모든 GUI 변수
    """
    state.cs_show_comparaison = True
    
    # 사용자가 선택한 두 가지 시나리오 가져오기
    results_1 = tp.get(state.selected_scenario).pipelines['pipeline'].results.read()
    results_2 = tp.get(state.selected_scenario_two).pipelines['pipeline'].results.read()
    state.cs_sum_costs_two = results_2['Total Cost'].sum()

    # 두 시나리오의 부분 비용 계산
    bool_costs_of_stock = [c for c in results_2.columns
                           if 'Cost' in c and 'Total' not in c and 'Stock' in c]
    
    state.cs_sum_costs_of_stock_two = int(results_2[bool_costs_of_stock].sum(axis=1)\
                                                                        .sum(axis=0))

    bool_costs_of_BO = [c for c in results_2.columns
                        if 'Cost' in c and 'Total' not in c and 'BO' in c]
    state.cs_sum_costs_of_BO_two = int(results_2[bool_costs_of_BO].sum(axis=1)\
                                                                  .sum(axis=0))

    # 비교 그래프의 데이터 프레임을 채웁니다.
    new_result_1 = pd.DataFrame({"index": results_1.index})
    new_result_2 = pd.DataFrame({"index": results_2.index})

    columns_to_merge = ['Cost', 'Purchase', 'Production', 'Stock', 'BO']
    for col in columns_to_merge:
        if col == 'Cost':
            bool_col_1 = [c for c in results_1.columns
                          if col in c and 'Total' not in c]
            bool_col_2 = [c for c in results_2.columns
                          if col in c and 'Total' not in c]
        else:
            bool_col_1 = [c for c in results_1.columns
                          if col in c and 'Total' not in c and 'Cost' not in c]
            bool_col_2 = [c for c in results_2.columns
                          if col in c and 'Total' not in c and 'Cost' not in c]

        new_result_1[col] = results_1[bool_col_1].sum(axis=1)
        new_result_2[col] = results_2[bool_col_2].sum(axis=1)

    new_result_1.columns = ['Scenario 1 ' + column if column != 'index' else 'index'
                            for column in new_result_1.columns]
    new_result_2.columns = ['Scenario 2 ' + column if column !='index' else 'index'
                            for column in new_result_2.columns]

    state.cs_comparaison_metrics_df = pd.DataFrame(
        {
            "Metrics": [ "Stock Cost", "BO Cost"],
            "Scenario 1: Stock Cost": [state.sum_costs_of_stock, None],
            "Scenario 2: Stock Cost": [state.cs_sum_costs_of_stock_two, None],
            "Scenario 1: BO Cost": [None, state.sum_costs_of_BO],
            "Scenario 2: BO Cost": [None, state.cs_sum_costs_of_BO_two]
        })

    state.cs_comparaison_df = pd.merge(new_result_1, new_result_2, on="index", how="inner")
    print("Comparaison done")
    pass


cs_height_bar_chart = "80%"

cs_show_comparaison = False

cs_compar_graph_selector = [
    'Metrics',
    'Costs',
    'Purchases',
    'Productions',
    'Stocks',
    'Back Order']
cs_compar_graph_selected = cs_compar_graph_selector[0]

cs_comparaison_df = pd.DataFrame({'index': [0],
                                  'Scenario 1 Cost': [0],
                                  'Scenario 1 Purchase': [0],
                                  'Scenario 1 Production': [0],
                                  'Scenario 1 Stock': [0],
                                  'Scenario 1 BO': [0],
                                  'Scenario 2 Cost': [0],
                                  'Scenario 2 Purchase': [0],
                                  'Scenario 2 Production': [0],
                                  'Scenario 2 Stock': [0],
                                  'Scenario 2 BO': [0]})

cs_comparaison_metrics_df = pd.DataFrame({"Metrics": ["Stock Cost", "BO Cost"],
                                          "Scenario 1: Stock Cost": [0, 0],
                                          "Scenario 2: Stock Cost": [0, 0],
                                          "Scenario 1: BO Cost": [0, 0],
                                          "Scenario 2: BO Cost": [0, 0]})

cs_sum_costs_of_stock_two = 0
cs_sum_costs_of_BO_two = 0
cs_sum_costs_two = 0
