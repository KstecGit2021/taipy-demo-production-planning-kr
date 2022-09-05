import pandas as pd
import numpy as np
from pulp import *


# 이 코드는 이러한 기능이 필요한 작업을 생성하는 config.py에서 사용됩니다.
# 이 함수는 전형적인 파이썬 함수입니다(Taipy는 없습니다)

###############################################################################
# 기능
###############################################################################


def create_model(demand: pd.DataFrame, fixed_variables: dict):
    """이 함수는 모델을 생성합니다. 문제의 모든 변수와 제약을 생성합니다.
    또한 목적 함수를 생성합니다.

    Args:
        demand (pd.DataFrame): 수요 데이터 프레임
        fixed_variables (dict): 고정된 변수 사전

    Returns:
        dict: (생성된 모델이 있는) 모델 정보
    """
    print("모델 생성 중...")

    monthly_demand_FPA = demand["Demand_A"]
    monthly_demand_FPB = demand["Demand_B"]

    nb_periods = len(monthly_demand_FPA)

    # 모델 생성
    prob = LpProblem("Production_Planning", LpMinimize)
    
    # 변수 생성
    # 제품 A의 경우
    monthly_production_FPA = [
        LpVariable(f"Monthly_Production_FPA_{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_FPA = [
        LpVariable(f"Monthly_Stock_FPA_{m}", 0) for m in range(nb_periods)
    ]

    monthly_back_order_FPA = [
        LpVariable(f"Monthly_Back_Order_FPA_{m}", 0) for m in range(nb_periods)
    ]

    # 제품 B의 경우
    monthly_production_FPB = [
        LpVariable(f"Monthly_Production_FPB_{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_FPB = [
        LpVariable(f"Monthly_Stock_FPB_{m}", 0) for m in range(nb_periods)
    ]
    monthly_back_order_FPB = [
        LpVariable(f"Monthly_Back_Order_FPB_{m}", 0) for m in range(nb_periods)
    ]

    # 제품 1의 경우
    monthly_purchase_RPone = [
        LpVariable(f"Monthly_Purchase_RPone_{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPone = [
        LpVariable(f"Monthly_Stock_RPone_{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_not_used_RPone = [
        LpVariable(f"Monthly_Stock_not_used_RPone{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPone_for_FPA = [
        LpVariable(f"Monthly_Stock_RPone_for_FPA{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPone_for_FPB = [
        LpVariable(f"Monthly_Stock_RPone_for_FPB{m}", 0) for m in range(nb_periods)
    ]

    # 제품 2의 경우 
    monthly_purchase_RPtwo = [
        LpVariable(f"Monthly_Purchase_RPtwo{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPtwo = [
        LpVariable(f"Monthly_Stock_RP{m}two", 0) for m in range(nb_periods)
    ]
    monthly_stock_not_used_RPtwo = [
        LpVariable(f"Monthly_Stock_not_used_RPtwo{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPtwo_for_FPA = [
        LpVariable(f"Monthly_Stock_RPtwo_for_FPA{m}", 0) for m in range(nb_periods)
    ]
    monthly_stock_RPtwo_for_FPB = [
        LpVariable(f"Monthly_Stock_RPtwo_for_FPB{m}", 0) for m in range(nb_periods)
    ]

    # 제약 조건 생성

    # 제품 A에 대한 Kirchoff의 법칙
    for m in range(1, nb_periods):
        prob += (
            monthly_production_FPA[m]
            - monthly_back_order_FPA[m - 1]
            + monthly_stock_FPA[m - 1]
            == monthly_demand_FPA[m] + monthly_stock_FPA[m] - monthly_back_order_FPA[m]
        )
    # 제품 B에 대한 Kirchoff의 법칙
    for m in range(1, nb_periods):
        prob += (
            monthly_production_FPB[m]
            - monthly_back_order_FPB[m - 1]
            + monthly_stock_FPB[m - 1]
            == monthly_demand_FPB[m] + monthly_stock_FPB[m] - monthly_back_order_FPB[m]
        )

    # 제품 1에 대한 Kirchoff의 법칙
    for m in range(1, nb_periods):
        prob += (
            monthly_purchase_RPone[m - 1] + monthly_stock_not_used_RPone[m - 1]
            == monthly_stock_RPone[m]
        )
    # 없음 문제에 대한 MS 수정
    prob += monthly_purchase_RPone[nb_periods - 1] == 0

    for m in range(1, nb_periods):
        prob += (
            monthly_purchase_RPtwo[m - 1] + monthly_stock_not_used_RPtwo[m - 1]
            == monthly_stock_RPtwo[m]
        )
    # 없음 문제에 대한 MS 수정
    prob += monthly_purchase_RPtwo[nb_periods - 1] == 0

    for m in range(nb_periods):
        prob += monthly_production_FPA[m] <= fixed_variables["Max_Capacity_FPA"]

    prob += monthly_production_FPA[0] == fixed_variables["Initial_Production_FPA"]

    prob += monthly_back_order_FPA[0] == fixed_variables["Initial_Back_Order_FPA"]

    prob += monthly_stock_FPA[0] == fixed_variables["Initial_Stock_FPA"]

    # 제품 A에 대한 BOM에 대한 제약

    for m in range(1, nb_periods):
        prob += (
            monthly_production_FPA[m]
            == fixed_variables["number_RPone_to_produce_FPA"]
            * monthly_stock_RPone_for_FPA[m - 1]
            + fixed_variables["number_RPtwo_to_produce_FPA"]
            * monthly_stock_RPtwo_for_FPA[m - 1]
        )

    for m in range(nb_periods):
        prob += (
            fixed_variables["number_RPone_to_produce_FPA"]
            * monthly_stock_RPone_for_FPA[m]
            == fixed_variables["number_RPtwo_to_produce_FPA"]
            * monthly_stock_RPtwo_for_FPA[m]
        )

    # 변수에 대한 제약조건: 제품 A의 최대값과 초기값
    for m in range(nb_periods):
        prob += monthly_production_FPB[m] <= fixed_variables["Max_Capacity_FPB"]
    prob += monthly_production_FPB[0] == fixed_variables["Initial_Production_FPB"]

    prob += monthly_back_order_FPB[0] == fixed_variables["Initial_Back_Order_FPB"]
    prob += monthly_stock_FPB[0] == fixed_variables["Initial_Stock_FPB"]

    # 제품 B에 대한 BOM에 대한 제약

    for m in range(1, nb_periods):
        prob += (
            monthly_production_FPB[m]
            == fixed_variables["number_RPone_to_produce_FPB"]
            * monthly_stock_RPone_for_FPB[m - 1]
            + fixed_variables["number_RPtwo_to_produce_FPB"]
            * monthly_stock_RPtwo_for_FPB[m - 1]
        )

    for m in range(nb_periods):
        prob += (
            fixed_variables["number_RPone_to_produce_FPB"]
            * monthly_stock_RPone_for_FPB[m]
            == fixed_variables["number_RPtwo_to_produce_FPB"]
            * monthly_stock_RPtwo_for_FPB[m]
        )

    for m in range(nb_periods):
        prob += monthly_stock_RPone[m] <= fixed_variables["Max_Stock_RPone"]

    prob += monthly_stock_RPone[0] == fixed_variables["Initial_Stock_RPone"]

    prob += monthly_purchase_RPone[0] == fixed_variables["Initial_Purchase_RPone"]

    for m in range(nb_periods):
        prob += monthly_stock_RPone[m] == (
            monthly_stock_not_used_RPone[m]
            + monthly_stock_RPone_for_FPA[m]
            + monthly_stock_RPone_for_FPB[m]
        )
    # 변수에 대한 제약 조건: 제품 1의 최대값 및 초기값

    for m in range(nb_periods):
        prob += monthly_stock_RPtwo[m] <= fixed_variables["Max_Stock_RPtwo"]

    prob += monthly_stock_RPtwo[0] == fixed_variables["Initial_Stock_RPtwo"]

    prob += monthly_purchase_RPtwo[0] == fixed_variables["Initial_Purchase_RPtwo"]
    # 제품 1의 재고를 정의하는 제약 조건
    
    for m in range(nb_periods):
        prob += monthly_stock_RPtwo[m] == (
            monthly_stock_not_used_RPtwo[m]
            + monthly_stock_RPtwo_for_FPA[m]
            + monthly_stock_RPtwo_for_FPB[m]
        )
    # 변수에 대한 제약 조건: 제품 A 및 B의 최대 값(누적)

    for m in range(nb_periods):
        prob += (
            monthly_production_FPA[m] + monthly_demand_FPB[m]
            <= fixed_variables["Max_Capacity_of_FPA_and_FPB"]
        )

    # 목적 함수 설정
    prob += lpSum(
        fixed_variables["Weight_of_Back_Order"]
        / 100
        * (
            fixed_variables["cost_FPA_Back_Order"] * monthly_back_order_FPA[m]
            + fixed_variables["cost_FPB_Back_Order"] * monthly_back_order_FPB[m]
        )
        + fixed_variables["Weight_of_Stock"]
        / 100
        * (
            fixed_variables["cost_FPA_Stock"] * monthly_stock_FPA[m]
            + fixed_variables["cost_FPB_Stock"] * monthly_stock_FPB[m]
            + fixed_variables["cost_RPone_Stock"] * monthly_stock_RPone[m]
            + fixed_variables["cost_RPtwo_Stock"] * monthly_stock_RPtwo[m]
        )
        for m in range(nb_periods)
    )

    # 필요한 모든 정보를 사전에 담기
    model_info = {
        "model_created": prob,
        "model_solved": None,
        "Monthly_Production_FPA": monthly_production_FPA,
        "Monthly_Stock_FPA": monthly_stock_FPA,
        "Monthly_Back_Order_FPA": monthly_back_order_FPA,
        "Monthly_Production_FPB": monthly_production_FPB,
        "Monthly_Stock_FPB": monthly_stock_FPB,
        "Monthly_Back_Order_FPB": monthly_back_order_FPB,
        "Monthly_Stock_RPone": monthly_stock_RPone,
        "Monthly_Stock_RPtwo": monthly_stock_RPtwo,
        "Monthly_Purchase_RPone": monthly_purchase_RPone,
        "Monthly_Purchase_RPtwo": monthly_purchase_RPtwo,
    }

    print("Model created")
    return model_info


def solve_model(model_info: dict):
    """이 함수는 모델을 풀고 사전에 있는 모든 솔루션을 반환합니다.

    Args:
        model_info (dict): create_model 함수에 의해 전달된 model_info

    Returns:
        dict: 해결된 모델 및 솔루션
    """
    print("모델 풀기...")
    prob = model_info["model_created"]

    nb_periods = len(model_info["Monthly_Production_FPA"])

    # 모델 풀기
    m_solved = prob.solve()

    # 올바른 변수에서 솔루션 얻기
    # 제품 A의 경우
    prod_sol_FPA = [
        value(model_info["Monthly_Production_FPA"][p]) for p in range(nb_periods)
    ]
    stock_sol_FPA = [
        value(model_info["Monthly_Stock_FPA"][p]) for p in range(nb_periods)
    ]
    bos_sol_FPA = [
        value(model_info["Monthly_Back_Order_FPA"][p]) for p in range(nb_periods)
    ]

    # 제품 B의 경우
    prod_sol_FPB = [
        value(model_info["Monthly_Production_FPB"][p]) for p in range(nb_periods)
    ]
    stock_sol_FPB = [
        value(model_info["Monthly_Stock_FPB"][p]) for p in range(nb_periods)
    ]
    bos_sol_FPB = [
        value(model_info["Monthly_Back_Order_FPB"][p]) for p in range(nb_periods)
    ]

    # 제품 1의 경우
    stock_RPone_sol = [
        value(model_info["Monthly_Stock_RPone"][p]) for p in range(nb_periods)
    ]
    stock_RPtwo_sol = [
        value(model_info["Monthly_Stock_RPtwo"][p]) for p in range(nb_periods)
    ]

    # 제품 2의 경우
    purchase_RPone_sol = [
        value(model_info["Monthly_Purchase_RPone"][p]) for p in range(nb_periods)
    ]
    purchase_RPtwo_sol = [
        value(model_info["Monthly_Purchase_RPtwo"][p]) for p in range(nb_periods)
    ]

    # 사전에 넣기
    model_info = {
        "model_created": prob,
        "model_solved": m_solved,
        "Monthly_Production_FPA": prod_sol_FPA,
        "Monthly_Stock_FPA": stock_sol_FPA,
        "Monthly_Back_Order_FPA": bos_sol_FPA,
        "Monthly_Production_FPB": prod_sol_FPB,
        "Monthly_Stock_FPB": stock_sol_FPB,
        "Monthly_Back_Order_FPB": bos_sol_FPB,
        "Monthly_Stock_RPone": stock_RPone_sol,
        "Monthly_Purchase_RPone": purchase_RPone_sol,
        "Monthly_Stock_RPtwo": stock_RPtwo_sol,
        "Monthly_Purchase_RPtwo": purchase_RPtwo_sol,
    }
    print("Model solved")
    return model_info


def create_results(model_info: dict, fixed_variables: dict, demand: pd.DataFrame):
    """이 함수는 모델의 결과를 생성합니다. 결과 데이터 프레임은 모든 유용한 정보의 연결입니다.

    Args:
        model_info (dict): solve_model 함수에 의해 생성된 사전
        fixed_variables (dict): 문제의 고정 변수
        demand (pd.DataFrame): A와 B에 대한 수요

    Returns:
        pd.DataFrame: 솔루션에 대한 모든 유용한 정보를 수집하는 데이터 프레임
    """
    print("결과 생성 중...")

    # A와 B에 대한 수요 얻기
    demand_series_FPA = demand["Demand_A"]
    demand_series_FPB = demand["Demand_B"]

    nb_periods = len(demand_series_FPA)

    # 다른 비용을 계산
    cost_FPBO_FPA = fixed_variables["cost_FPA_Back_Order"] * np.array(
        model_info["Monthly_Back_Order_FPA"]
    )
    cost_stock_FPA = fixed_variables["cost_FPA_Stock"] * np.array(
        model_info["Monthly_Stock_FPA"]
    )
    cost_FPBO_FPB = fixed_variables["cost_FPB_Back_Order"] * np.array(
        model_info["Monthly_Back_Order_FPB"]
    )
    cost_stock_FPB = fixed_variables["cost_FPB_Stock"] * np.array(
        model_info["Monthly_Stock_FPB"]
    )
    cost_stock_RPone = fixed_variables["cost_RPone_Stock"] * np.array(
        model_info["Monthly_Stock_RPone"]
    )
    cost_stock_RPtwo = fixed_variables["cost_RPtwo_Stock"] * np.array(
        model_info["Monthly_Stock_RPtwo"]
    )
    cost_product_RPone = fixed_variables["cost_RPone_Purchase"] * np.array(
        model_info["Monthly_Purchase_RPone"]
    )
    cost_product_RPtwo = fixed_variables["cost_RPtwo_Purchase"] * np.array(
        model_info["Monthly_Purchase_RPtwo"]
    )

    # 총 비용(비용의 합계)
    total_cost = (
        cost_FPBO_FPA
        + cost_stock_FPA
        + cost_FPBO_FPB
        + cost_stock_FPB
        + cost_stock_RPone
        + cost_product_RPone
        + cost_product_RPtwo
        + cost_stock_RPtwo
    )

    # 데이터 프레임을 생성하는 데 사용할 사전 생성
    dict_for_dataframe = {
        "Monthly Production FPA": model_info["Monthly_Production_FPA"],
        "Monthly Stock FPA": model_info["Monthly_Stock_FPA"],
        "Monthly BO FPA": model_info["Monthly_Back_Order_FPA"],
        "Max Capacity FPA": [fixed_variables["Max_Capacity_FPA"]] * nb_periods,
        "Monthly Production FPB": model_info["Monthly_Production_FPB"],
        "Monthly Stock FPB": model_info["Monthly_Stock_FPB"],
        "Monthly BO FPB": model_info["Monthly_Back_Order_FPB"],
        "Max Capacity FPB": [fixed_variables["Max_Capacity_FPB"]] * nb_periods,
        "Monthly Stock RP1": model_info["Monthly_Stock_RPone"],
        "Monthly Stock RP2": model_info["Monthly_Stock_RPtwo"],
        "Monthly Purchase RP1": model_info["Monthly_Purchase_RPone"],
        "Monthly Purchase RP2": model_info["Monthly_Purchase_RPtwo"],
        "Demand FPA": demand_series_FPA,
        "Demand FPB": demand_series_FPB,
        "Stock FPA Cost": cost_stock_FPA,
        "Stock FPB Cost": cost_stock_FPB,
        "Stock RP1 Cost": cost_stock_RPone,
        "Stock RP2 Cost": cost_stock_RPtwo,
        "Purchase RP1 Cost": cost_product_RPone,
        "Purchase RP2 Cost": cost_product_RPtwo,
        "BO FPA Cost": cost_FPBO_FPA,
        "BO FPB Cost": cost_FPBO_FPB,
        "Total Cost": total_cost,
        "index": range(nb_periods),
    }

    results = pd.DataFrame(dict_for_dataframe).round()
    print("Results created")

    # 모델이 생성되는 방식 때문에 마지막 두 관찰을 지웁니다. 
    # 값에는 의미가 없습니다.
    return results[:-2]
