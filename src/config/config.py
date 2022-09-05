import taipy as tp
from taipy import Scope, Config
from taipy.core import Frequency

import json
from algos.algos import *

# 이 코드는 시나리오_cfg 및 파이프라인_csg를 생성하는 코드입니다. 
# 이 두 변수는 기본 코드에서 새 시나리오를 만드는 데 사용됩니다.

# 이 코드는 실행 그래프를 구성할 것입니다.

###############################################################################
# 데이터노드
###############################################################################

# 첫 번째 데이터 노드를 생성합니다. 소스는 csv 파일입니다.
path_to_demand = 'data/time_series_demand.csv'
demand_cfg = Config.configure_data_node(id="demand",
                                storage_type="csv", 
                                scope=Scope.SCENARIO,
                                path=path_to_demand,
                                has_header=True)


fixed_variables_default_json = open('data/fixed_variables_default.json')
fixed_variables_default = json.load(fixed_variables_default_json)

# fixed_variables_default를 기본 데이터로 하는 두 번째 데이터 노드 생성 
# 이것은 fixed_variable에 대한 다른 값을 제출할 때 쓸 이 데이터 노드입니다.
fixed_variables_cfg = Config.configure_data_node(id="fixed_variables", default_data = fixed_variables_default, scope=Scope.PIPELINE)

# 모델을 추적하는 데이터 노드는 다음과 같습니다. model_created 데이터 노드, model_solved 데이터 노드
model_created_cfg = Config.configure_data_node(id="model_created", scope=Scope.PIPELINE)
model_solved_cfg = Config.configure_data_node(id="model_solved", scope=Scope.PIPELINE)

# 이것은 메인 코드에서 결과를 얻는 데 사용할 데이터 노드입니다.
results_cfg = Config.configure_data_node(id="results", scope=Scope.PIPELINE)

###############################################################################
# 작업
###############################################################################

# (demand_cfg,fixed_variables_cfg) -> |create_model| -> (model_created_cfg)
create_model_task = Config.configure_task(id="create_model",
                            input=[demand_cfg,fixed_variables_cfg],
                            function=create_model,
                            output=[model_created_cfg])

# (model_created_cfg) -> |solve_model| -> (model_solved_cfg)
solve_model_cfg = Config.configure_task(id="solve_model",
                                    input=[model_created_cfg],
                                    function=solve_model,
                                    output=[model_solved_cfg])

# (model_solved_cfg,fixed_variables_cfg,demand_cfg) -> |create_results| -> (results_cfg)
create_results_cfg = Config.configure_task(id="create_results",
                                       input=[model_solved_cfg,fixed_variables_cfg,demand_cfg],
                                       function=create_results,
                                       output=[results_cfg])


###############################################################################
# 파이프라인 및 시나리오 구성
###############################################################################

# 파이프라인 : 작업 실행. 일련의 작업을 수행하는 것을 말합니다. 
pipeline_cfg = Config.configure_pipeline(id="pipeline",task_configs=[create_model_task,solve_model_cfg,create_results_cfg])

# 시나리오 : 파이프라인 실행. 일련의 파이프라인(여기서는 하나만)의 실행을 나타냅니다.
# 이 변수를 통해 새로운 시나리오를 생성합니다.
scenario_cfg = Config.configure_scenario(id="scenario",pipeline_configs=[pipeline_cfg], frequency=Frequency.MONTHLY)

