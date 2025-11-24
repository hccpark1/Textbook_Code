import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI
import numpy as np

# 1. 입력값 정의 및 단위 변환
Tdb_C = 40.0  # 건구 온도 (Dry Bulb Temperature, Tdb) [°C]
Twb_C = 20.0  # 습구 온도 (Wet Bulb Temperature, Twb) [°C]
P_atm = 101325.0 # 대기압 (Atmospheric Pressure) [Pa] (표준 대기압: 101,325 Pa)

# CoolProp 입력 단위: 온도 [K], 압력 [Pa]
Tdb_K = Tdb_C + 273.15
Twb_K = Twb_C + 273.15
P_Pa = P_atm

# 2. CoolProp HAPropsSI 함수를 이용한 계산
# HAPropsSI(Output, Input1_Name, Input1_Value, Input2_Name, Input2_Value, Input3_Name, Input3_Value)

# 입력 조건: 'Tdb' (건구 온도), 'Twb' (습구 온도), 'P' (압력)

# 2-1. 습도비 (Humidity Ratio, W)
W = CP.HAPropsSI('W', 'Tdb', Tdb_K, 'Twb', Twb_K, 'P', P_Pa) # [kg_w/kg_da]

# 2-2. 엔탈피 (Enthalpy, H) - 건조 공기 1kg당 엔탈피
H = CP.HAPropsSI('H', 'Tdb', Tdb_K, 'Twb', Twb_K, 'P', P_Pa) # [J/kg_da]

# 2-3. 노점 온도 (Dew Point Temperature, Tdp)
Tdp_K = CP.HAPropsSI('D', 'Tdb', Tdb_K, 'Twb', Twb_K, 'P', P_Pa)
Tdp_C = Tdp_K - 273.15 # [°C]

# 2-4. 상대 습도 (Relative Humidity, RH or Phi)
RH = CP.HAPropsSI('R', 'Tdb', Tdb_K, 'Twb', Twb_K, 'P', P_Pa) # [소수점: 0 ~ 1]

# 2-5. 비체적 (Specific Volume, V) - 건조 공기 1kg당 체적
V = CP.HAPropsSI('V', 'Tdb', Tdb_K, 'Twb', Twb_K, 'P', P_Pa) # [m³/kg_da]

# 3. 결과 출력
print(f"## 📊 CoolProp 습공기 계산 결과 (Tdb={Tdb_C}°C, Twb={Twb_C}°C, P={P_Pa/1000:.1f}kPa)")
print("---")
print(f"1. 습도비 (W): {W:>.5f} [kg_수증기/kg_건조공기]")
# CoolProp은 엔탈피 기준점을 다르게 설정할 수 있으므로, 결과값은 참고용으로 사용
print(f"2. 엔탈피 (H): {H/1000:>.2f} [kJ/kg_건조공기] (엔탈피는 0°C 건조 공기 기준)") 
print(f"3. 노점 온도 (Tdp): {Tdp_C:>.2f} [°C]")
print(f"4. 상대 습도 (RH): {RH*100:>.2f} [%]")
print(f"5. 비체적 (V): {V:>.5f} [m³/kg_건조공기]")