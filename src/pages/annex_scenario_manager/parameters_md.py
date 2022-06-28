from .chart_md import ch_chart_md, ch_layout_dict, ch_results
from config.config import fixed_variables_default
from taipy.gui import Icon


def create_sliders(fixed_variables):
    """"
    This is a pretty complex function that creates the sliders for the parameters by itself.
    It could also have been done by hand. However, this way is more flexible in the long run. 
    """
    
    # the string that will be returned
    slider_md = ""
    
    # there are three types of parameters 
    param_types = ['Capacity Constraints','Objective Weights','Initial Parameters']
    # sliders of different products will be grouped in different sections (with a toggle)
    products = ['FPA','FPB','RPone','RPtwo','weight']
    
    for p_type in param_types:
        # the part will be shown when p_type is selected
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
            
            # sliders are being created for each variable (var_p)
            # min and max value are also created automatically
            for var in var_p :
                min_ = str(int(fixed_variables[var]*0.35))
                max_ = str(int(fixed_variables[var]*1.65)) if fixed_variables[var] != 0 else '50'
                
                name_of_var = var.replace('cost','Unit Cost -')
                name_of_var = name_of_var[0].upper() + name_of_var[1:].replace('_',' ').replace('one','1').replace('two','2')
                
                slider_md += "\n\n" + name_of_var + " : *<|{fixed_variables."+var+"}|>*"
                slider_md += "\n<|{fixed_variables."+var+"}|slider|orientation=h|min="+min_+"|max="+max_+"|step=5|>"
        else :
            # the part will be shown depending on the product
            for p in products :
                slider_md += "\n<|part|render={pa_product_param == 'product_"+p+"'}|"
                if p_type == 'Capacity Constraints':
                    var_p = [key  for key in fixed_variables.keys() if (p in key and 'produce' not in key and 'Max' in key)]
                else :
                    var_p = [key  for key in fixed_variables.keys() if (p in key and 'produce' not in key and 'Capacity' not in key and 'Max' not in key)]
                
                # sliders are being created for each variable (var_p)
                # min and max value are also created automatically
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


# Toggle for choosing the sliders
pa_choice_product_param = [("product_RPone", Icon("images/P1.png", "product_RPone")),
                    ("product_RPtwo", Icon("images/P2.png", "product_RPtwo")),
                    ("product_FPA", Icon("images/PA.png", "product_FPA")),
                    ("product_FPB", Icon("images/PB.png", "product_FPB"))]
pa_product_param = 'Else'

