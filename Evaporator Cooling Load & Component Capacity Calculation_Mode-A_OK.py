### Evaporator Cooling Load Calculation at Bench Mode-A
# 필요한 라이브러리 불러오기
import math
from numpy import log as ln
import psychrolib
import sys
from iapws import IAPWS97

# Set the unit system to SI Units
psychrolib.SetUnitSystem(psychrolib.SI)

# 상수 정의
Gas_constant = 8.31432 # J/(mol*K)
R_gas = 0.287                   # kJ/(kg-*K)
Molar_mass_air = 0.0289644      # kg/mol
cp = 0.241                      # kcal/(kg-c)

# 건구온도, 상대습도를 알 때 습구온도 구하기기
def GetTWetBulbFromRelHum(TDryBulb, RelHum, Pressure) :
    TWetBulb = psychrolib.GetTWetBulbFromRelHum(TDryBulb, RelHum, Pressure) 
    # print(f'건구온도={TDryBulb:.1f}C, 상대습도={RelHum:.1f} 일 때 습구온도 = {TWetBulb:.1f}C')
    return TWetBulb

# 공기 밀도 계산하기
def GetDryAirDensity(TDryBulb, Pressure):   # psychrolib 사용
    density_air = psychrolib.GetDryAirDensity(TDryBulb, Pressure)
    return density_air

# 응축수 량 계산
def condense_water_calculation(tdb, twb, P) :
    # 습구온도 tw의 포화압력을 구한다. ASHRAE "Fundamentals" 6장 식(4)
    C8 = -5800.2206
    C9 = 1.3914993
    C10 = -0.04860239
    C11 = 0.41764768e-4
    C12 = -0.14452093e-7
    C13 = 6.5459673

    Twet =  twb + 273.15
    print(f"습구 절대온도 Twet = {Twet:.2f} K")
    # LN_Pws = C8/Twet + C9 + C10*Twet + C11*Twet**2 + C12*Twet**3 + C13*math.log(Twet)
    LN_Pws = C8/Twet + C9 + C10*Twet + C11*Twet**2 + C12*Twet**3 + C13*ln(Twet)    
    LN_Pws = round(LN_Pws, 5)
    Pws = math.exp(LN_Pws)                   # [Pa]
    Pws = round(Pws, 2)
    print(f"LN(Pws) = {LN_Pws:.5f}")
    print(f"Pws = {Pws}")
    # 습구온도에 대한 Ws(Humidity Ratio at Saturation) 계산-ASHRAE "Fundamentals" 6장 식(21)
    Ws = 0.62198 * (Pws / (P - Pws))
    Ws = round(Ws, 5)
    print(f"Humidity Ratio at Saturation(Ws) = {Ws:.5f}")

    # W(Humidity Ratio) 계산
    Whr = ((2501-2.381*twb)*Ws - (tdb-twb)) / (2501+1.805*tdb - 4.186*twb)
    Whr = round(Whr, 5)
    print(f"Humidity Ratio(Whr) = {Whr:.5f} [kg/kg-dry air]")
    print("-------------------------------------")

    return Whr

### Main program
## 냉방부하 조건(Known Values) 입력하세요.
V_car = 65.0                    # Input 차량 속도 [km/h] 
t_amb = 38.0                    # Input 외기 공기온도[C]
t_air_evap_out = 17.0           # Input 증발기 출구 공기 건구온도[C]
rh_evap_in = 0.99                # Input 증발기 입구 공기 상대습도(%RH/100)
rh_evap_out = 0.5              # Input 증발기 출구 공기 상대습도(%RH/100)
AirVol = 550.0                  # Input 증발기 입구 풍량[CMH]
Pair_in = 101325                # Input 입구부 공기 압력 = 대기압[Pa]
Pair_out = 101325               # Input 출구부 공기 압력 = 대기압[Pa]

# Evaporator Cooling Load Calculation Condition (입력 결과에 따른 계산)
t_air_evap_in = t_amb + 3.0     # 증발기 입구 공기온도[C]. 건구온도. Heat Pickup 2.0[C]
t_air_cond_in = t_amb + 2.0     # 증발기 입구 공기온도[C]. 건구온도. Heat Pickup 2.0[C]

# 증발기 입/출구부 공기 습구온도(WB) 계산
twet_in = GetTWetBulbFromRelHum(t_air_evap_in, rh_evap_in, Pair_in)  
twet_out = GetTWetBulbFromRelHum(t_air_evap_out, rh_evap_out, Pair_out)

# Summary for Evaporator Cooling Load Calculation Condition 
print("------ Condition for Evaporator Cooling Load --------")
print(f"증발기 입구 조건 : {t_air_evap_in:.1f}DB[C], {twet_in:.1f}WB[C], {rh_evap_in*100:.1f}%RH, {Pair_in/1e3:.3f}kPa")
print(f"증발기 출구 조건 : {t_air_evap_out:.1f}DB[C], {twet_out:.1f}WB[C], {rh_evap_out*100:.1f}%RH, {Pair_out/1e3:.3f}kPa")
print("----------------------------------------------------")

# 1. 건공기 감열량 계산
# 1.1 밀도 계산 및 출력
density_air = GetDryAirDensity(t_air_evap_in, Pair_in)
density_air = round(density_air, 4)
print(f"공기 밀도 = {density_air} kg/m^3")    
# 1.2 공기의 질량 유동률 (kg/h)
massflow_air = AirVol * density_air
massflow_air = round(massflow_air, 2)
print(f"공기 질량유동률 = {massflow_air} kg/h")

# 1.3 건 공기(Dry Air)의 감열량 (kcal/h)
dt_air_evap = t_air_evap_in - t_air_evap_out
Qdryair = massflow_air * cp * dt_air_evap
Qdryair = round(Qdryair, 1)
print(f"건공기 감열량 = {Qdryair} kcal/h")
print("-------------------------------------")


# 2. Evaporator Core 입출구의 응축수 량 계산.
# 2.1 입출구 응축수 량 계산.
Whr_in = condense_water_calculation(t_air_evap_in, twet_in, Pair_in)
Whr_out = condense_water_calculation(t_air_evap_out, twet_out, Pair_out)
Whr_in = round(Whr_in, 5)
Whr_out = round(Whr_out, 5)
print(f"입구측 Humidity Ratio = {Whr_in:.5f} kg/kg-dry air")
print(f"출구측 Humidity Ratio = {Whr_out:.5f} kg/kg-dry air")

# 입출구 응축수 량 차이 계산
Whr = Whr_in - Whr_out       # [kg/kg-dryair]
Whr = round(Whr, 5)
print(f"입출구 응축수 량의 차이 = {Whr:.5f} kg/kg-dry air")

# 조건 풍량에 대한 응축수 량 계산
massflow_water = massflow_air * Whr     # [kg/h]
massflow_water = round(massflow_water, 5)
print(f"질량유량에 대한 응축수 량 = {massflow_water:.5f} kg/h")

# Latent Heat of Condensed water (Emperical equation)
Q_latent = massflow_water * (-2.3647 * t_air_evap_out+2500.8) * 0.2388    # [kcal/h]
Q_latent = round(Q_latent, 5)
print(f"건공기 감영량 = {Qdryair:.1f} kcal/h")
print(f"응축수 잠열량 = {Q_latent:.1f} kcal/h")
Qevap = Qdryair+Q_latent
Qevap = round(Qevap, 1)
print("-------------------------------------")
print(f"증발기 냉각 부하 = {Qevap:.1f} kcal/h, {Qevap/860:.1f} kW")

## Refrigerant Flowrate Calculation
# 4 Operating points System operating conditions (Refrigerant Size)
SC_cond = 10.0                  # Input 응축기 출구 과냉각도[C]
SH_cond = 10.0                  # Input 압축기 입구 과열도[C]
P1 = 4.0                       # Input 압축기 입구 압력[barA]. 4.08[kg/cm2A]
T1 = 18.0                       # Input 압축기 입구 온도[C].
P2 = 19.0                       # Input 압축기 출구 압력[barA]. 19.37[kg/cm2A]
T2 = 80.0                       # Input 압축기 출구 온도[C].
P3 = 19.0                       # Input 응축기 출구 압력[barA]. 19.37[kg/cm2A]
T3 = 53.0                       # Input 응축기 출구 온도[C].    
P4 = 5.0                        # Input 증발기 입구 압력[barA]. 4.08[kg/cm2A]. 대안=2.75 [barA]
T4 = 9.0                       # Input 증발기 입구 온도[C]. 대안=13.0 [C]
x_evap = 0.34                   # Input 증발기 입구 건도
RPM_comp = 1900                 # Input 압축기 회전수[rpm]
Eff_volume = 0.75               # Input 압축기 체적 효율
fluid = 'R134a'                 # Input 냉매 종류
# 증발기 내부 유동 냉매 질량유동률 계산
# 1. Evaporator Inlet/Outlet Enthalpy Calculation
# Comp.suction enthalpy(h1)와 Condenser outlet enthalpy(h3=h4) 계산
from CoolProp.CoolProp import PropsSI
from CoolProp.CoolProp import PhaseSI
import CoolProp

def get_phase(T, P, fluid):
    Phase = PhaseSI("T", T,"P",P,fluid)
    return Phase  

def get_enthalpy(T, P, fluid):
    h = PropsSI('H', 'T', T, 'P', P, fluid)
    return h / 1000  # J/kg to kJ/kg    

def get_enthalpy_liq_gas(T, P, Q, fluid):
    h = PropsSI('H', 'T', T, 'Q', Q, 'R134a')
    return h / 1000  # J/kg to kJ/kg   

def get_specific_volume(T, P, fluid):
    v = 1 / PropsSI('D', 'T', T, 'P', P, fluid)
    return v

def get_entropy(T, P, Q, fluid):
    s = PropsSI('S', 'T', T, 'P', P, 'R134a')
    return s / 1000  # J/kg to kJ/kg

def get_saturation_temperature(pressure_pa, fluid):
    T_satK = PropsSI('T', 'P', pressure_pa, 'Q', 1, fluid)
    return T_satK


# enthalpy [kJ/kg] of R134a
Phase1 = get_phase(T1 + 273.15, P1 * 1e5, fluid)
Phase2 = get_phase(T2 + 273.15, P2 * 1e5, fluid)   
Phase3 = get_phase(T3 + 273.15, P3 * 1e5, fluid)
Phase4 = get_phase(T4 + 273.15, P4 * 1e5, fluid)   
Phase4b = get_phase(T4 + 273.15, P4 * 1e5, fluid) 

h1 = get_enthalpy(T1 + 273.15, P1 * 1e5, fluid)
h2 = get_enthalpy(T2 + 273.15, P2 * 1e5, fluid)
h3 = get_enthalpy(T3 + 273.15, P3 * 1e5, fluid)
# h4 = get_enthalpy(T4 + 273.15, P4 * 1e5, fluid)
h4 = h3                         # 팽창 밸브 (등엔탈피 팽창)     
h4b = get_enthalpy_liq_gas(T4 + 273.15, P4 * 1e5, 0.34, fluid)
k_kj2kcal = 0.2388459           # kJ to kcal

s1 = get_entropy(T1 + 273.15, P1 * 1e5, 1, fluid)
s2 = get_entropy(T2 + 273.15, P2 * 1e5, 1, fluid)
v1 = get_specific_volume(T1 + 273.15, P1 * 1e5, fluid)
v2 = get_specific_volume(T2 + 273.15, P2 * 1e5, fluid)

print('Enthalpy at Points')
print('------------------------')
print(f"Point 1: Phase={Phase1}, h={h1:.1f} kJ/kg, s={s1:.2f} kJ/kg/K, v={v1:.4f} m^3/kg")
print(f"Point 2: Phase={Phase2}, h={h2:.1f} kJ/kg, s={s2:.2f} kJ/kg/K, v={v2:.4f} m^3/kg")
print(f"Point 3: Phase={Phase3}, h={h3:.1f} kJ/kg")
print(f"Point 4: Phase={Phase4}, h={h4:.1f} kJ/kg")

# 2. 엔탈피 차(h1-h4) 및 냉매유량 계산
delta_h_14 = h1 - h4
print(f"응축기 입출구 엔탈피 차(h1-h4) = {delta_h_14:.1f} kJ/kg")       
m_ref_evap = Qevap / (delta_h_14 * k_kj2kcal)  # [kg/h]
m_ref_evap = round(m_ref_evap, 2)
print(f"냉매유량 = {m_ref_evap:.2f} kg/h")

# 3. 압축기 요구성능 결정
# 압축기 출구 냉매 포화온도 계산
T2s = get_saturation_temperature(P2 * 1e5, "R134a") - 273.15
print(f"압축기 출구 포화온도(T2s) = {T2s:.1f} C")

# 압축기 흡입체적 계산(IV:intake_volume)
IV = m_ref_evap * v1 * (1e6/60) /RPM_comp  # [cc/rev]
print(f"압축기 흡입체적 (IV) = {IV:.2f} cc/rev")

# 압축기 토출량 계산(Displacement)
capa_comp = m_ref_evap * (h2 - h1)  # [kJ/h]
capa_comp_kcal = capa_comp * k_kj2kcal  # [kcal/h]
print(f"압축기 Capacity = {capa_comp:.2f} kJ/h, {capa_comp_kcal:.2f} kcal/h, {capa_comp_kcal/860.02:.2f} kW")
displacement = IV / Eff_volume   # [cc]
print(f"압축기 토출량 = {displacement:.1f} cc")
print("-------------------------------------")

# 4. 응축기 성능 계산
# 응축기 규격 정보 입력
Width_cond = 67.0           # Input 응축기 폭[cm]
Height_cond = 34.0          # Input 응축기 높이[cm]
Depth_cond = 1.6            # Input 응축기 두께[cm]
AV_cond_1 = 857.0           # Input 응축기 공기 유량[m3/h] at Va=1.0m/s
AV_cond_2 = 1820            # Input 응축기 공기 유량[m3/h] at Va=1.5m/s was 1280
AV_cond_3 = 2570            # Input 응축기 공기 유량[m3/h] at Va=3.0m/s  2570
AV_cond_4 = 4280            # Input 응축기 공기 유량[m3/h] at Va=5.3m/s

# 응축기 방열성능 계산
Qcond = Qevap + capa_comp_kcal  # [kcal/h]
print(f"응축기 방열량 = {Qcond:.1f} kcal/h")

# 응축기 냉매 질량유동률 계산
m_ref_cond = Qcond / ((h2 - h3) * k_kj2kcal)  # [kg/h]
print(f"응축기 냉매 질량유동률 = {m_ref_cond:.1f} kg/h")

sp_volume_cond = get_specific_volume(t_air_cond_in+273.15, Pair_in, "air")
print(f"응축기 공기 비체적 = {sp_volume_cond:.4f} m^3/kg")

# 응축기 공기 질량유동률 계산 at AV_cond_3 조건
Qcond_air = Qcond                           # [kcal/h]
m_air_cond = AV_cond_2 / sp_volume_cond   # [kg/h]   
print(f"응축기 공기 질량유량 = {m_air_cond:.1f} kg/h")

# 응축기 전후면 공기 온도차 계산 at AV_cond_3 조건
delta_air_cond = Qcond_air / (m_air_cond * cp)  # [C]
print(f"응축기 전후면 공기 온도차 = {delta_air_cond:.1f} C")

# 응축기 효율(Effectiveness) 계산 at AV_cond_3 조건
T_air_sat = get_saturation_temperature(P2*1e5,"R134a") - 273.15
print(f"응축기 공기 포화온도 = {T_air_sat:.1f} C")
Eff_cond = delta_air_cond / (T_air_sat - t_air_cond_in)  # [C]
print(f"응축기 Effectiveness = {Eff_cond:.3f}")

