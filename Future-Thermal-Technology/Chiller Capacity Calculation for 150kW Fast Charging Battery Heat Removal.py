# -*- coding: utf-8 -*-
"""
150 kW 급속 충전 중인 전기차 배터리 발열 및 칠러 용량 계산
- 입력값: 충전전력, 내부저항 발열 손실률, 냉각수 유량(kg/s), 냉각수 비열(사용자값 또는 CoolProp)
- 출력값: 배터리 발열량 (W), 필요 칠러 냉각용량 (W, kW), 냉각수 온도 강하 (degC)
"""

from math import isfinite

# --- 입력 조건 (필요시 수정) ---
P_charge_kW = 150.0            # 충전 전력 [kW]
loss_fraction = 0.03           # 배터리 내부 저항에 의한 발열 손실률 (예: 3%)
mass_flow_kg_s = 0.25          # 냉각수 질량유량 [kg/s] (15 lpm ≈ 0.25 kg/s)
use_coolprop = True            # CoolProp 사용 여부 (설치되어 있으면 True)

# CoolProp 관련 기본값
T_ref_C = 20.0                 # 참조 온도 [°C] (비열 계산용)
P_ref_Pa = 101325.0            # 대기압 [Pa]
glycol_mass_fraction = 0.5     # 에틸렌글리콜 질량분율 (50:50)

# 사용자 제공 비열(대체값, J/kg.K)
cp_user_kJ_per_kgK = 3.4       # kJ/kg.K
cp_user = cp_user_kJ_per_kgK * 1000.0  # J/kg.K

# --- CoolProp로 비열 조회 시도 ---
cp_mix = None
if use_coolprop:
    try:
        from CoolProp.CoolProp import PropsSI
        T_ref_K = T_ref_C + 273.15
        # 물과 에틸렌글리콜의 비열을 각각 조회한 뒤 질량분율 가중평균으로 혼합비열 계산
        cp_water = PropsSI('Cpmass', 'T', T_ref_K, 'P', P_ref_Pa, 'Water')          # J/kg.K
        # CoolProp의 비압축성(혼합) 에틸렌글리콜 이름은 INCOMP::MEG (Mono Ethylene Glycol)
        cp_eg = PropsSI('Cpmass', 'T', T_ref_K, 'P', P_ref_Pa, 'INCOMP::MEG')      # J/kg.K
        cp_mix = glycol_mass_fraction * cp_eg + (1.0 - glycol_mass_fraction) * cp_water
    except Exception as e:
        # CoolProp이 없거나 조회 실패 시 사용자 제공값 사용
        cp_mix = None

# 최종 사용할 비열 결정
if cp_mix is None or not isfinite(cp_mix):
    cp = cp_user
    used_source = "user_provided"
else:
    cp = cp_mix
    used_source = "coolprop_mix"

# --- 계산 ---
P_charge_W = P_charge_kW * 1000.0
heat_loss_W = P_charge_W * loss_fraction                     # 배터리 내부 발열량 [W]
chiller_required_W = heat_loss_W * 1.20                      # 시스템 손실 20% 고려 [W]
deltaT_C = heat_loss_W / (mass_flow_kg_s * cp)               # 냉각수 온도 강하 [°C]

# --- 출력 ---
print("=== 입력 조건 ===")
print(f"충전 전력: {P_charge_kW:.1f} kW")
print(f"발열 손실률: {loss_fraction*100:.2f} %")
print(f"냉각수 유량: {mass_flow_kg_s:.3f} kg/s")
print(f"참조 온도: {T_ref_C:.1f} °C")
print()

print("=== 사용된 냉각수 비열 ===")
if used_source == "coolprop_mix":
    print(f"CoolProp 조회 (에틸렌글리콜 {glycol_mass_fraction*100:.0f}% 질량분율): cp = {cp:.1f} J/kg.K")
else:
    print(f"사용자 제공값: cp = {cp/1000.0:.3f} kJ/kg.K ({cp:.1f} J/kg.K)")
print()

print("=== 계산 결과 ===")
print(f"① 배터리 발열량: {heat_loss_W:.1f} W  ({heat_loss_W/1000.0:.3f} kW)")
print(f"② 필요 칠러 냉각용량 (시스템 손실 20% 포함): {chiller_required_W:.1f} W  ({chiller_required_W/1000.0:.3f} kW)")
print(f"③ 냉각수 온도 강하 ΔT: {deltaT_C:.3f} °C")

# 결론 문구 (검증용)
print()
print("=== 결론 ===")
print(f"계산에 따르면 약 {chiller_required_W/1000.0:.2f} kW 급 이상의 칠러가 필요합니다.")
print(f"냉각수는 칠러를 통과하며 약 {deltaT_C:.2f} °C 냉각되어 배터리로 공급됩니다.")
