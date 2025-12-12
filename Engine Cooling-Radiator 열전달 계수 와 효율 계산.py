import math
from CoolProp.CoolProp import PropsSI
from tabulate import tabulate

def calculate_air_density(temp_C, pressure_Pa=101325):
    """주어진 온도와 압력에서 공기의 밀도를 계산합니다."""
    temp_K = temp_C + 273.15
    density = PropsSI('D', 'P', pressure_Pa, 'T', temp_K, 'Air')
    return density

def calculate_effectiveness_and_NTU(Cr, N, flow_type):
    """ NTU와 열용량 비율을 이용하여 열교환기 효율(ε)을 계산. Crossflow (unmixed)를 적용 """
    if Cr > 1:
        Cr = 1 / Cr  # Cmin / Cmax
        N = N * Cr  # NTU based on C_min

    # Crossflow (both fluid unmixed)
    epsilon = 1 - math.exp((1/Cr) * N**(0.22) * (math.exp(-Cr * N**(0.78)) - 1))
    return epsilon

def calculate_LMTD(Th_in, Th_out, Tc_in, Tc_out, flow_type="counterflow"):
    """ 대수 평균 온도차 (LMTD)를 계산합니다. """
    if flow_type == "counterflow":
        dT1 = Th_in - Tc_out
        dT2 = Th_out - Tc_in
    elif flow_type == "parallel":
        dT1 = Th_in - Tc_in
        dT2 = Th_out - Tc_out
    else:
        # Crossflow의 경우 LMTD 보정 계수가 필요하므로 이 함수만으로 사용하기에 부적합
        raise ValueError("LMTD calculation is best for counterflow or parallel flow. Use NTU-Epsilon method for crossflow.")
    
    try:
        return (dT1 - dT2) / math.log(dT1 / dT2)
    except (ValueError, ZeroDivisionError):
        return 0  # 0으로 나누는 경우를 방지


## 1. 초기 데이터 및 상수 설정 (SI 단위 통일)
Q_rad = 98.4  # [kW] 실제 방열량
Area_ratio = 5.3  # 외부 표면적 (m2/m2 정면면적)
Width_m = 81.3 / 100  # 라디에이터 너비 (m)
Height_m = 91.4 / 100 # 라디에이터 높이 (m)
Airflow_cmh = 4757  # 공기 유량 (CMH, m3/h)
M_coolant = 3.024  # 냉각수 질량 유량 (kg/s)
Cp_coolant = 3.5  # [kJ/(kg·K)] 냉각수 비열
Cp_air = 1.005  # [kJ/(kg·K)] 공기 비열

T_air_in = 32.0  # 공기 입구 온도 (℃)
dT_in = 83  # 냉각수-공기 입구 온도차 (℃)

## 2. 계산 과정
# 코어 면적 계산
Area_front = Width_m * Height_m  # 정면 면적
Area_o = Area_front * Area_ratio # 총 외부 표면적

# 공기 밀도 계산 (CoolProp 사용)
rho_air = calculate_air_density(T_air_in)

# 공기 질량 유량 (kg/s)
M_air = (Airflow_cmh / 3600) * rho_air

# 열용량 유량 (C_dot) 계산
C_dot_coolant = M_coolant * Cp_coolant
C_dot_air = M_air * Cp_air

# 최소 및 최대 열용량 유량
C_min = min(C_dot_coolant, C_dot_air)
C_max = max(C_dot_coolant, C_dot_air)
Cr = C_min / C_max # 열용량 비율 (C_r)

# 열교환기 실제 열량
Q_actual = Q_rad # [kW]

# 이론상 최대 열량
T_coolant_in = T_air_in + dT_in # 냉각수 입구 온도를 가정
Q_max = C_min * (T_coolant_in - T_air_in) # [kW]

# 3. 효율 (ε) 계산
epsilon = Q_actual / Q_max

# 4. 총 열전달 계수 (U) 계산 (NTU-ε 관계 이용)
# 효율(ε)을 통해 NTU(유용도)를 구하고, 이를 통해 U 계산
# NTU = f(ε, Cr)
# Crossflow (unmixed)에 대한 근사식 사용
# ε = 1 - exp((1/Cr) * N_tu^(0.22) * (exp(-Cr * N_tu^(0.78)) - 1))
# 이 식을 역으로 풀어야 하지만, 복잡하므로 효율 식에 NTU를 대입하여 검증하는 방식으로 접근
# 혹은 더 간단하게 U = Q_actual / (Ao * LMTD_effective)로 계산
# Crossflow의 LMTD 보정 계수(F)는 복잡한 도표를 봐야 하므로,
# 여기서는 NTU-ε 관계식을 이용한 방법을 적용하는 것이 더 적절합니다.

# NTU-epsilon 관계식에서 NTU를 구하는 것은 복잡하므로
# U = Q_rad / (Ao * LMTD) 방식으로 계산하되, 온도 출력을 먼저 구해야 함
dT_coolant = Q_actual / M_coolant / Cp_coolant
T_coolant_out = T_coolant_in - dT_coolant

dT_air = Q_actual / M_air / Cp_air
T_air_out = T_air_in + dT_air

# Crossflow의 경우, LMTD에 보정 계수(F)를 곱해야 하지만
# 주어진 정보만으로는 F를 계산할 수 없으므로, LMTD만으로 근사값을 구합니다.
LMTD_approx = calculate_LMTD(T_coolant_in, T_coolant_out, T_air_in, T_air_out, "counterflow")
U = Q_rad / (Area_o * LMTD_approx) # kW/(m²·K)

## 5. 결과 출력
results = [
    ["총 방열량 (Q)", f"{Q_rad:.1f} kW"],
    ["라디에이터 정면 면적 (Af)", f"{Area_front:.2f} m²"],
    ["라디에이터 외부 표면적 (Ao)", f"{Area_o:.2f} m²"],
    ["공기 질량 유량 (m_air)", f"{M_air:.2f} kg/s"],
    ["공기 밀도 (rho_air)", f"{rho_air:.3f} kg/m3"],
    ["최고 방열량(Qmax)", f"{Q_max:.1f} kW"],
    ["냉각수 질량 유량 (m_coolant)", f"{M_coolant:.2f} kg/s"],
    ["공기 측 열용량 (C_dot_air)", f"{C_dot_air:.2f} kW/K"],
    ["냉각수 측 열용량 (C_dot_coolant)", f"{C_dot_coolant:.2f} kW/K"],
    ["최소 열용량 (C_min)", f"{C_min:.2f} kW/K"],
    ["최대 열용량 (C_max)", f"{C_max:.2f} kW/K"],
    ["열용량 비율 (Cr)", f"{Cr:.2f}"],
    ["냉각수 입츨구 온도차", f"{dT_coolant:.1f} °C"],
    ["냉각수 입구 온도", f"{T_coolant_in:.1f} °C"],    
    ["냉각수 출구 온도", f"{T_coolant_out:.1f} °C"],
    ["공기 입구 온도", f"{T_air_in:.1f} °C"],    
    ["공기 출구 온도", f"{T_air_out:.1f} °C"],
    ["근사 LMTD", f"{LMTD_approx:.1f} °C"],
    ["라디에이터 효율 (ε)", f"{epsilon:.2f}"],
    ["총 열전달 계수 (U)", f"{U:.2f} kW/(m²·K)"],
]

print("\n** 라디에이터 성능 분석 결과 **")
# print(tabulate(results, headers=["항목", "값"], tablefmt="grid"))
print(tabulate(results, headers=["항목", "값"]))