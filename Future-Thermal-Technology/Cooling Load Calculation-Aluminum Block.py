# -*- coding: utf-8 -*-
"""
알루미늄 블록 냉각 계산
조건: 405 g 알루미늄 블록을 100°C -> 20°C로 300 s 동안 냉각
- 입력: 질량(m), 초기온도, 최종온도, 시간
- 출력: 총 열량 Q [J], 평균 냉각 파워 Q_dot [W]
- CoolProp로 물성 조회 시도, 실패 시 사용자 제공값 사용
"""

from math import isfinite

# --- 입력값 ---
mass_g = 405.0                 # 질량 [g]
T_initial_C = 100.0            # 초기 온도 [°C]
T_final_C = 20.0               # 최종 온도 [°C]
time_s = 300.0                 # 냉각 시간 [s]

# 사용자 제공 물성 (기본값)
rho_g_per_cm3 = 2.7            # 밀도 [g/cm3] (참고)
cp_user_J_per_gK = 0.9         # 비열 [J/(g·K)] (0.9 J/g.K = 900 J/kg.K)

# --- 단위 변환 ---
mass_kg = mass_g / 1000.0      # kg
deltaT_K = T_initial_C - T_final_C

# --- CoolProp로 비열 조회 시도 (일반적으로 고체 물성은 제공되지 않을 수 있음) ---
cp_J_per_gK = None
try:
    from CoolProp.CoolProp import PropsSI
    # CoolProp은 주로 유체에 대한 라이브러리이므로 고체(Aluminum) 조회가 안 될 가능성이 큽니다.
    # 시도해보고 실패하면 예외 처리로 넘어갑니다.
    # 일부 빌드에서는 'INCOMP::ALUMINUM' 같은 식별자가 없으므로 아래 호출은 대부분 실패합니다.
    T_ref_K = (T_initial_C + T_final_C) / 2.0 + 273.15
    # 시도: 'Al' 또는 'ALUMINUM' 같은 키워드로 조회 (환경에 따라 동작하지 않음)
    cp_al = PropsSI('Cpmass', 'T', T_ref_K, 'P', 101325, 'Aluminum')
    # PropsSI 결과는 J/kg.K 이므로 J/g.K 로 변환
    cp_J_per_gK = cp_al / 1000.0
except Exception:
    cp_J_per_gK = None

# 최종 사용할 비열 결정
if cp_J_per_gK is None or not isfinite(cp_J_per_gK):
    cp_J_per_gK = cp_user_J_per_gK
    used_source = "user_provided"
else:
    used_source = "coolprop"

# --- 계산 ---
# Q = m * cp * deltaT  (단위: J)
Q_J = mass_g * cp_J_per_gK * deltaT_K

# 평균 냉각 파워 (W)
Q_dot_W = Q_J / time_s

# 출력 (가독성)
print("=== 입력값 ===")
print(f"질량: {mass_g:.1f} g ({mass_kg:.3f} kg)")
print(f"온도 변화: {T_initial_C:.1f} °C -> {T_final_C:.1f} °C  (ΔT = {deltaT_K:.1f} K)")
print(f"냉각 시간: {time_s:.1f} s")
print()

print("=== 사용된 물성 ===")
if used_source == "coolprop":
    print(f"CoolProp에서 조회한 비열: {cp_J_per_gK:.4f} J/(g·K)")
else:
    print(f"사용자 제공 비열: {cp_J_per_gK:.4f} J/(g·K)")
print(f"밀도(참고): {rho_g_per_cm3:.2f} g/cm^3")
print()

print("=== 계산 결과 ===")
print(f"총 냉각에 필요한 열량 Q: {Q_J:,.1f} J  ({Q_J/1000.0:,.3f} kJ)")
print(f"평균 냉각 파워 Q_dot: {Q_dot_W:,.3f} W")
