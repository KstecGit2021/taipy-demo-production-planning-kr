from taipy.gui import Icon
import pandas as pd

ch_layout_dict = {"margin":{"t":20}}

# 차트 설정 토글
ch_choice_chart = [("pie", Icon("images/pie.png", "pie")),
                    ("chart", Icon("images/chart.png", "chart"))]
ch_show_pie = ch_choice_chart[1][0]

ch_results = pd.DataFrame({"Monthly Production FPA":[],
                          "Monthly Stock FPA": [],
                          "Monthly BO FPA": [],
                          "Max Capacity FPA": [],
                          
                          "Monthly Production FPB": [],
                          "Monthly Stock FPB": [],
                          "Monthly BO FPB": [],
                          "Max Capacity FPB": [],
                          
                          "Monthly Stock RP1":[],
                          "Monthly Stock RP2":[],
                          
                          "Monthly Purchase RP1":[],
                          "Monthly Purchase RP2":[],
                          
                          "Demand FPA": [],
                          "Demand FPB": [],
                          
                          'Stock FPA Cost': [],
                          'Stock FPB Cost': [],
                          
                          'Stock RP1 Cost': [],
                          'Stock RP2 Cost': [],
                          
                          'Purchase RP1 Cost': [],
                          'Purchase RP2 Cost': [],
                          
                          "BO FPA Cost":[],
                          "BO FPB Cost":[],
                          
                          "Total Cost": [],
                          "index": []})



def get_col(ch_results:pd.DataFrame,var:str):
    if var == 'Cost':
        columns = [col for col in ch_results.columns if var in col]
    elif var=='Production':
        columns = [col for col in ch_results.columns if (var in col or 'Capacity' in col) and 'Cost' not in col]
    else :
        columns = [col for col in ch_results.columns if var in col and 'Cost' not in col]
        
    return columns


def get_y_format(columns):
    md =""
    for col_i in range(len(columns)):
        md+=f"y[{col_i+1}]={columns[col_i]}|"
        if "Capacity" in columns[col_i] :
            md+=f"line[{col_i+1}]=dash|"
        
    return md[:-1]


def create_charts_md(ch_results):
    """"
    이것은 모든 차트를 생성하는 매우 복잡한 함수입니다.
    또한 사용자 작업에 따라 시간이 지남에 따라 변경되는 단일 문자열을 갖도록 수동으로 수행하거나 부분적으로 사용할 수 있습니다.
    """
    
    # 차트용 md를 만드는 매개변수
    config_scenario_option = ["sm_show_config_scenario", "not(sm_show_config_scenario)"]
    
    # 파이는 이러한 표현에 가능합니다.
    pie_possible = ['Costs','Purchases','Productions','Stocks','Back Order']
    charts_option_for_col = ['Cost','Purchase','Production','Stock','BO','FPA','FPB','RP1','RP2']
    charts_option = ['Costs','Purchases','Productions','Stocks','Back Order','Product FPA','Product FPB','Product RP1','Product RP2']
    
    md = ""
    for config_scenario in config_scenario_option :
        md += "\n<|part|render={"+config_scenario+"}|"
        md += "\n<|"
            
        for charts_i in range(len(charts_option)):
            columns = get_col(ch_results,charts_option_for_col[charts_i])
            y_format = get_y_format(columns)
            columns = [c for c in columns if 'Total' not in c] # in the pie, we don't want to show the total
            
            if charts_option[charts_i] in pie_possible :
                md +="\n<|{pie_results.loc[" + str(columns) + "]}|chart|type=pie|x=values|label=labels|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|render={ch_show_pie=='pie' and sm_graph_selected=='"+charts_option[charts_i]+"'}|>"
                md += "\n<|{ch_results}|chart|x=index|" + y_format + "|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|render={ch_show_pie=='chart' and sm_graph_selected=='"+charts_option[charts_i]+"'}|>"
            else:
                md += "\n<|{ch_results}|chart|x=index|" + y_format + "|width={width_chart}|height={height_chart}|layout={ch_layout_dict}|render={sm_graph_selected=='"+charts_option[charts_i]+"'}|>"

        md += """\n|>
|>"""

    return md


ch_chart_md_1 = """
<br/>
<|layout|columns=1 1|columns[mobile]=1|
<|
<center>
<|{str(int(sum_costs_of_BO/1000))+' K'}|indicator|value={sum_costs_of_BO}|min=50_000|max=1_000|width=93%|>
Back Order Cost
</center>
|>

<|
<center>
<|{str(int(sum_costs_of_stock/1000))+' K'}|indicator|value={sum_costs_of_stock}|min=100_000|max=25_000|width=93%|>
Stock Cost
</center>
|>
|>
"""

ch_chart_md = """
<|
<|part|render={len(scenario_selector)>0}|
<|""" + ch_chart_md_1 + """|>
""" + create_charts_md(ch_results) + """
|>

<no_scenario|part|render={len(scenario_selector)==0}|
## No scenario created for the current month
|no_scenario>
|>
"""




