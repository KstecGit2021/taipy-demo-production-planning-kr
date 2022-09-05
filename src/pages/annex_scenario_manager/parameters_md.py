from .chart_md import ch_chart_md, ch_layout_dict, ch_results
from config.config import fixed_variables_default
from taipy.gui import Icon


def create_sliders(fixed_variables):
    """"
    이것은 매개변수에 대한 슬라이더를 자체적으로 생성하는 매우 복잡한 함수입니다.
    손으로 할 수도 있었습니다. 그러나 이 방법은 장기적으로 더 유연합니다.
    """
    
    # 반환될 문자열
    slider_md = ""
    
    # 매개변수에는 세 가지 유형이 있습니다.
    param_types = ['Capacity Constraints','Objective Weights','Initial Parameters']
    # 다른 제품의 슬라이더는 (토글을 사용하여) 다른 섹션으로 그룹화됩니다.
    products = ['FPA','FPB','RPone','RPtwo','weight']
    
    for p_type in param_types:
        # p_type이 선택되면 해당 부분이 표시됩니다.
        slider_md += "\n<|part|render={pa_param_selected == '" + p_type + "'}|"
        if p_type != 'Objective Weights':
            # the part will be shown if 'Objective Weights' is not selected
            slider_md +="""
<center>
<|{pa_product_param}|toggle|lov={pa_choice_product_param}|value_by_id|>
</center>
<br/>
"""
        if p_type == 'Objective Weights':
            var_p = [key  for key in fixed_variables.keys() if ('produce' not in key and 'Weight' in key)]
            
            # 각 변수(var_p)에 대해 슬라이더가 생성되고 있습니다.
            # 최소값과 최대값도 자동으로 생성됩니다.
            for var in var_p :
                min_ = str(int(fixed_variables[var]*0.35))
                max_ = str(int(fixed_variables[var]*1.65)) if fixed_variables[var] != 0 else '50'
                
                name_of_var = var.replace('cost','Unit Cost -')
                name_of_var = name_of_var[0].upper() + name_of_var[1:].replace('_',' ').replace('one','1').replace('two','2')
                
                slider_md += "\n\n" + name_of_var + " : *<|{fixed_variables."+var+"}|>*"
                slider_md += "\n<|{fixed_variables."+var+"}|slider|orientation=h|min="+min_+"|max="+max_+"|step=5|>"
        else :
            # 제품에 따라 부품이 표시됩니다.
            for p in products :
                slider_md += "\n<|part|render={pa_product_param == 'product_"+p+"'}|"
                if p_type == 'Capacity Constraints':
                    var_p = [key  for key in fixed_variables.keys() if (p in key and 'produce' not in key and 'Max' in key)]
                else :
                    var_p = [key  for key in fixed_variables.keys() if (p in key and 'produce' not in key and 'Capacity' not in key and 'Max' not in key)]
                
                # 각 변수(var_p)에 대해 슬라이더가 생성되고 있습니다.
                # 최소값과 최대값도 자동으로 생성됩니다.
                for var in var_p :
                    min_ = str(int(fixed_variables[var]*0.35))
                    max_ = str(int(fixed_variables[var]*1.65)) if fixed_variables[var] != 0 else '50'
                    
                    name_of_var = var.replace('cost','Unit Cost -')
                    name_of_var = name_of_var[0].upper() + name_of_var[1:].replace('_',' ').replace('one','1').replace('two','2')
                    
                    slider_md += "\n\n" + name_of_var + " : *<|{fixed_variables."+var+"}|>*"
                    slider_md += "\n<|{fixed_variables."+var+"}|slider|orientation=h|min="+min_+"|max="+max_+"|step=5|>"
                    
    
                
                slider_md += "\n|>"
        slider_md+="\n|>"
    return slider_md

pa_sliders_md = create_sliders(fixed_variables_default)

pa_parameters_md = """
<|layout|columns=139 1 45|columns[mobile]=1|gap=1.5rem|
""" + ch_chart_md + """ 

<blank_space|
|blank_space>

<|
<center>
<|{pa_param_selected}|selector|lov={pa_param_selector}|>
</center>

""" + pa_sliders_md + """

<|Delete|button|on_action={delete_scenario_fct}|active={len(scenario_selector)>0}|id=delete_button|>
<|Make Primary|button|on_action={make_primary}|active={len(scenario_selector)>0 and not selected_scenario_is_primary}|id=make_primary|>
<|Re-optimize|button|on_action=submit_scenario|active={len(scenario_selector)>0}|id=re_optimize|>
<|New scenario|button|on_action=create_new_scenario|id=new_scenario|>
|>
|>
"""

pa_param_selector = ['Capacity Constraints','Objective Weights','Initial Parameters']
pa_param_selected = pa_param_selector[0]


# 슬라이더 선택 토글
pa_choice_product_param = [("product_RPone", Icon("images/P1.png", "product_RPone")),
                    ("product_RPtwo", Icon("images/P2.png", "product_RPtwo")),
                    ("product_FPA", Icon("images/PA.png", "product_FPA")),
                    ("product_FPB", Icon("images/PB.png", "product_FPB"))]
pa_product_param = 'Else'

