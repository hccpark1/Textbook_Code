import math
from CoolProp.CoolProp import PropsSI

def mf_condenser_design():
    print("=== Automotive MF (Microchannel) Condenser Design ===\n")

    # ---------------------------------------------------------
    # STEP 1: 설계 데이터 정의 (Design Data)
    # ---------------------------------------------------------
    fluid_ref = 'R134a' # 냉매
    fluid_air = 'Air'   # 냉각 매체 (공기)

    # 냉매 측 조건 (차량용 에어컨 일반 조건)
    P_ref_pa = 1.5e6        # 응축 압력 (1.5 MPa, 약 15 bar)
    m_ref = 0.025           # 냉매 질량 유량 (kg/s)
    
    # 공기 측 조건
    T_air_in_k = 35.0 + 273.15 # 외기 온도 (35 C)
    P_air_pa = 101325.0        # 대기압
    V_air_face = 3.0           # 전면 풍속 (m/s)

    # ---------------------------------------------------------
    # STEP 2: 형상 제원 정의 (Geometry Definition)
    # ---------------------------------------------------------
    # 코어(Core) 전체 크기
    W_core = 0.600    # 코어 폭 (m)
    H_core = 0.400    # 코어 높이 (m)
    D_core = 0.016    # 코어 두께 (MPE 튜브의 폭, 16mm)

    # MPE 튜브 및 핀 제원
    H_tube = 0.002    # 튜브 높이 (2mm)
    H_fin = 0.008     # 핀 높이 (8mm)
    P_fin = 0.003     # 핀 피치 (3mm)
    t_fin = 0.0001    # 핀 두께 (0.1mm, 알루미늄)
    k_fin = 200.0     # 알루미늄 열전도도 (W/m.K)
    N_ports = 10      # 튜브 당 마이크로채널 포트 수
    D_hyd = 0.0012    # 포트의 수력 직경 (m)

    # ---------------------------------------------------------
    # STEP 3: 열전달 면적 계산 (Area Calculations)
    # ---------------------------------------------------------
    # 튜브 개수 산출 (코어 높이를 튜브+핀 높이로 나눔)
    N_tubes = int(H_core / (H_tube + H_fin))
    
    # 공기 측(Air-side) 면적 계산 
    A_tube_air = 2 * D_core * W_core * N_tubes # 공기에 노출된 튜브 평면 면적
    N_fins_per_tube = W_core / P_fin           # 튜브 1열당 핀 개수
    A_fin = 2 * D_core * H_fin * N_fins_per_tube * N_tubes # 핀 표면적
    A_air_total = A_tube_air + A_fin           # 총 공기측 전열 면적
    
    # 냉매 측(Refrigerant-side) 내부 면적
    A_ref_total = math.pi * D_hyd * W_core * N_ports * N_tubes

    print(f"[Geometry Info]")
    print(f" - Tubes: {N_tubes} ea")
    print(f" - Air-side Area (Aa): {A_air_total:.2f} m^2")
    print(f" - Ref-side Area (Ar): {A_ref_total:.2f} m^2")
    print(f" - Area Ratio (Aa/Ar): {A_air_total/A_ref_total:.1f}\n")

    # ---------------------------------------------------------
    # STEP 4: 열부하 및 출구 온도 계산
    # ---------------------------------------------------------
    # 냉매 포화 온도 및 잠열
    T_sat_k = PropsSI('T', 'P', P_ref_pa, 'Q', 1, fluid_ref)
    h_vap = PropsSI('H', 'P', P_ref_pa, 'Q', 1, fluid_ref)
    h_liq = PropsSI('H', 'P', P_ref_pa, 'Q', 0, fluid_ref)
    L_vap = h_vap - h_liq
    Q_duty = m_ref * L_vap # 총 방열량 (W)

    # 공기 질량 유량 및 출구 온도
    rho_air = PropsSI('D', 'T', T_air_in_k, 'P', P_air_pa, fluid_air)
    Cp_air = PropsSI('C', 'T', T_air_in_k, 'P', P_air_pa, fluid_air)
    m_air = rho_air * V_air_face * (W_core * H_core)
    T_air_out_k = T_air_in_k + Q_duty / (m_air * Cp_air)

    # LMTD (대수평균온도차) - 교차흐름(Cross-flow) 가정
    dT1 = T_sat_k - T_air_in_k
    dT2 = T_sat_k - T_air_out_k
    LMTD = (dT1 - dT2) / math.log(dT1 / dT2)

    print(f"[Thermal Duty]")
    print(f" - Condensing Temp: {T_sat_k - 273.15:.1f} C")
    print(f" - Heat Duty (Q): {Q_duty / 1000:.2f} kW")
    print(f" - Air Out Temp: {T_air_out_k - 273.15:.1f} C")
    print(f" - LMTD: {LMTD:.2f} C\n")

    # ---------------------------------------------------------
    # STEP 5: 열전달 계수 (Heat Transfer Coefficients)
    # ---------------------------------------------------------
    # 1. 공기 측 열전달 계수 (ha)
    # 자동차 핀-튜브의 Colburn j-factor 약식 상관식 적용
    # 실제로는 Chang-Wang 등의 복잡한 루버 핀(Louver Fin) 상관식 사용
    ha = 45.0 * (V_air_face)**0.6 # 단순화된 경험식 (W/m^2.K)

    # 핀 효율 (Fin Efficiency) 계산
    # 코루게이트 핀을 직선 핀으로 근사
    m_fin = math.sqrt(2 * ha / (k_fin * t_fin))
    fin_eff = math.tanh(m_fin * H_fin / 2) / (m_fin * H_fin / 2)
    
    # 전체 표면 효율 (Overall Surface Efficiency, eta_o)
    eta_o = 1 - (A_fin / A_air_total) * (1 - fin_eff)

    # 2. 냉매 측 열전달 계수 (hr)
    # 마이크로채널 내부 이상 유동 응축 (Two-phase condensation)
    # Shah 또는 Dobson-Chato 상관식을 적분해야 하나, 여기서는 평균 구간의 근사값 사용
    # 평균 품질(Quality) 구간에서 마이크로채널 R134a 응축 열전달 계수는 통상 2500~4000
    hr = 3500.0 # W/m^2.K

    print(f"[Heat Transfer Coefficients]")
    print(f" - Air-side (ha): {ha:.1f} W/m^2.K")
    print(f" - Fin Efficiency: {fin_eff*100:.1f} %")
    print(f" - Overall Surface Eff (eta_o): {eta_o*100:.1f} %")
    print(f" - Ref-side (hr): {hr:.1f} W/m^2.K\n")

    # ---------------------------------------------------------
    # STEP 6: 총괄 열전달 계수(U) 및 면적 평가
    # ---------------------------------------------------------
    # 공기 측 면적(Aa) 기준 총괄 열전달 계수 Ua
    # 튜브 벽면의 전도 저항은 얇은 알루미늄이므로 무시 (R_wall = 0)
    R_air = 1 / (eta_o * ha)
    R_ref = (A_air_total / A_ref_total) / hr
    Ua_calc = 1 / (R_air + R_ref)

    # 요구되는 공기 측 면적
    A_air_required = Q_duty / (Ua_calc * LMTD)
    Margin = (A_air_total - A_air_required) / A_air_required * 100

    print(f"[Final Performance Check]")
    print(f" - Overall U (Air-side): {Ua_calc:.1f} W/m^2.K")
    print(f" - Required Area (Aa): {A_air_required:.2f} m^2")
    print(f" - Provided Area (Aa): {A_air_total:.2f} m^2")
    print(f" - Margin: {Margin:.1f} %")

    if Margin > 0:
        print(" => 결론: 방열 면적이 충분합니다. (설계 합격)")
    else:
        print(" => 결론: 방열 능력이 부족합니다. 코어 면적(W, H)이나 두께(D)를 증가시키십시오.")

if __name__ == "__main__":
    mf_condenser_design()