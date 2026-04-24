from CoolProp.CoolProp import PropsSI

### 물의 냉각에 필요한 Thermal Load 게산식 (X. 미래 기술 트랜드 교재 Page 39)
# 물 0.5 Liter를 5℃ -> 영하 5℃로 10분간 냉각할 때 필요한 냉각열 계산

# === 조건 설정 ===
V_L = 0.5            # 부피 [L]
T_init_C = 5.0       # 초기 온도 [℃]
T_freeze_C = 0.0     # 어는점 [℃]
T_final_C = -5.0     # 최종 온도 [℃]
time_s = 1800        # 냉각 시간 [s]
P = 101325           # 대기압 [Pa] (1 atm)

# 사용자 제공 물성치 (단위: J/kg 및 J/kg.℃ 로 변환)
# (1 g = 0.001 kg 이므로 1000을 곱해줍니다)
Cp_ice = 2.05 * 1000       # 얼음 비열 [J/(kg.℃)] 
L_freeze = 333.55 * 1000   # 물 응고열 (잠열) [J/kg] 

# 절대온도(K) 변환
T_init_K = T_init_C + 273.15
T_freeze_liquid_K = 273.153 # CoolProp 액체 한계 온도 (0.003℃)

# === 1. 질량 계산 (CoolProp 활용) ===
# 5℃ 물의 정확한 밀도를 구해 부피를 질량으로 변환
D_water = PropsSI('D', 'T', T_init_K, 'P', P, 'Water') 
m_kg = (V_L * 0.001) * D_water 

# === 2. 열량 계산 ===
# 1) 액체 냉각 (5℃ -> 0℃) : CoolProp 엔탈피 차이 이용
H_liquid_initial = PropsSI('H', 'T', T_init_K, 'P', P, 'Water')
H_liquid_freeze = PropsSI('H', 'T', T_freeze_liquid_K, 'P', P, 'Water')
Q1_liquid_cooling = m_kg * (H_liquid_initial - H_liquid_freeze)

# 2) 상변화 (0℃ 물 -> 0℃ 얼음) : 주어진 잠열 이용
Q2_phase_change = m_kg * L_freeze

# 3) 고체 냉각 (0℃ 얼음 -> -5℃ 얼음) : 주어진 얼음 비열 이용
# 온도 차이(delta T)는 0 - (-5) = 5℃
Q3_solid_cooling = m_kg * Cp_ice * (T_freeze_C - T_final_C)

# 4) 총 필요 열량 (Q_total) [J]
Q_total = Q1_liquid_cooling + Q2_phase_change + Q3_solid_cooling

# 5) 필요 흡열량 (Qc) [W]
Qc_W = Q_total / time_s

# === 결과 출력 ===
print("-" * 45)
print(f"[계산 조건]")
print(f"초기 물 부피: {V_L} L")
print(f"계산된 질량 : {m_kg * 1000:.1f} g (5℃ 밀도 {D_water:.1f} kg/m³ 기준)")
print("-" * 45)
print(f"[결과]")
print(f"1) 액체 냉각 (5℃->0℃)    : {Q1_liquid_cooling:,.1f} J")
print(f"2) 상변화 (응고)         : {Q2_phase_change:,.1f} J")
print(f"3) 고체 냉각 (0℃->-5℃)  : {Q3_solid_cooling:,.1f} J")
print(f"4) 총 필요 열량 (Qtotal) : {Q_total:,.1f} J")
print(f"5) 필요 흡열량 (Qc)      : {Qc_W:.1f} W")
print("-" * 45)