import math
from CoolProp.CoolProp import PropsSI

def condenser_design_coolprop():
    print("=== Shell & Tube Condenser Design with CoolProp ===\n")

    # ---------------------------------------------------------
    # STEP 1: 설계 데이터 정의 (Design Data Definition)
    # ---------------------------------------------------------
    fluid_hot = 'Water'   # 쉘 측 유체 (응축될 증기)
    fluid_cold = 'Water'  # 튜브 측 유체 (냉각수)

    P_hot_pa = 101325.0   # 증기 압력 (1 atm = 101325 Pa)
    m_h = 2.0             # 증기 질량 유량 (kg/s)
    
    P_cold_pa = 200000.0  # 냉각수 압력 (2 bar)
    m_c = 50.0            # 냉각수 질량 유량 (kg/s)
    T_ci_k = 25.0 + 273.15 # 냉각수 입구 온도 (K)

    # ---------------------------------------------------------
    # STEP 2: 필요한 열부하(Q) 및 LMTD 계산
    # ---------------------------------------------------------
    # 1. 증기의 포화 온도 및 잠열 계산 (CoolProp)
    T_sat_k = PropsSI('T', 'P', P_hot_pa, 'Q', 1, fluid_hot)
    h_vap = PropsSI('H', 'P', P_hot_pa, 'Q', 1, fluid_hot)
    h_liq = PropsSI('H', 'P', P_hot_pa, 'Q', 0, fluid_hot)
    L_vap = h_vap - h_liq # 증발 잠열 (J/kg)
    
    # 열부하 (여기서는 포화증기가 100% 응축되는 조건만 가정)
    Q = m_h * L_vap

    # 2. 냉각수 출구 온도 계산 (현열 흡수)
    Cp_c_in = PropsSI('C', 'T', T_ci_k, 'P', P_cold_pa, fluid_cold)
    T_co_k = T_ci_k + Q / (m_c * Cp_c_in)
    
    # LMTD 계산
    dT1 = T_sat_k - T_co_k
    dT2 = T_sat_k - T_ci_k
    LMTD = (dT1 - dT2) / math.log(dT1 / dT2)

    print(f"[STEP 2] Heat Duty & Temperatures")
    print(f" - Saturation Temp: {T_sat_k - 273.15:.2f} C")
    print(f" - Latent Heat: {L_vap / 1000:.2f} kJ/kg")
    print(f" - Heat Duty (Q): {Q / 1e6:.3f} MW")
    print(f" - Coolant Out Temp: {T_co_k - 273.15:.2f} C")
    print(f" - LMTD: {LMTD:.2f} C\n")

    # ---------------------------------------------------------
    # STEP 3: 임시 형상 정의 (Tentative Geometry)
    # ---------------------------------------------------------
    do = 0.01905          # 튜브 외경 (m) - 3/4 inch
    di = 0.01575          # 튜브 내경 (m)
    L = 6.0               # 튜브 길이 (m)
    Nt = 500              # 튜브 총 개수
    nt_passes = 2         # 튜브 통과 횟수 (Passes)
    k_m = 50.0            # 튜브 재질 열전도도 (W/m.K, Carbon steel)
    Rf_s = 0.0002         # 쉘 측 오염 저항
    Rf_t = 0.0001         # 튜브 측 오염 저항

    # ---------------------------------------------------------
    # STEP 4: 튜브 측 열전달 계수 (ht) 계산
    # ---------------------------------------------------------
    T_c_bulk = (T_ci_k + T_co_k) / 2 # 냉각수 평균 온도
    
    # 평균 온도에서의 냉각수 물성치 (CoolProp)
    rho_c = PropsSI('D', 'T', T_c_bulk, 'P', P_cold_pa, fluid_cold)
    mu_c = PropsSI('V', 'T', T_c_bulk, 'P', P_cold_pa, fluid_cold)
    k_c = PropsSI('L', 'T', T_c_bulk, 'P', P_cold_pa, fluid_cold)
    Cp_c = PropsSI('C', 'T', T_c_bulk, 'P', P_cold_pa, fluid_cold)
    Pr_c = (Cp_c * mu_c) / k_c

    # 유속 및 레이놀즈 수 계산
    A_flow = (math.pi * di**2 / 4) * (Nt / nt_passes)
    v_c = m_c / (rho_c * A_flow)
    Re_c = (rho_c * v_c * di) / mu_c

    print(f"[STEP 4] Tube-Side (Coolant) Parameters")
    print(f" - Velocity: {v_c:.2f} m/s")
    print(f" - Reynolds Number: {Re_c:.0f}")

    # ---------------------------------------------------------
    # STEP 5 & STEP 6: 쉘 측 열전달 계수(hs) 및 전체 열전달 계수(U) 수렴 반복
    # ---------------------------------------------------------
    Tw_k = (T_sat_k + T_c_bulk) / 2 # 초기 벽면 온도 가정
    U_calc = 1000.0 # 초기 U 가정

    print(f"\n[STEP 5 & 6] Iteration for T_film, T_wall, and h_shell")
    for i in range(15):
        # 1. 튜브 벽면 온도에서의 냉각수 점도 산출 (점도 보정용)
        mu_cw = PropsSI('V', 'T', Tw_k, 'P', P_cold_pa, fluid_cold)
        
        # 2. 튜브 측 Nusselt 및 ht 계산 (Colburn 식 - 난류)
        if Re_c > 10000:
            Nu_c = 0.023 * (Re_c**0.8) * (Pr_c**(1/3)) * ((mu_c / mu_cw)**0.14)
        else: # 층류 혹은 천이구역 (간단히 Sieder-Tate 적용)
            Nu_c = 1.86 * ((Re_c * Pr_c * di / L)**(1/3)) * ((mu_c / mu_cw)**0.14)
        ht = (Nu_c * k_c) / di

        # 3. 필름 온도(T_film) 계산
        T_film_k = T_sat_k - 0.75 * (T_sat_k - Tw_k)
        
        # 4. 필름 온도에서의 응축액 물성치 (CoolProp)
        rho_film = PropsSI('D', 'T', T_film_k, 'P', P_hot_pa, fluid_hot)
        mu_film = PropsSI('V', 'T', T_film_k, 'P', P_hot_pa, fluid_hot)
        k_film = PropsSI('L', 'T', T_film_k, 'P', P_hot_pa, fluid_hot)

        # 5. 수평 튜브 쉘 측 열전달 계수 (hs) 계산 
        term = (rho_film**2 * 9.81 * L_vap * k_film**3) / (mu_film * do * (T_sat_k - Tw_k))
        hs = 0.725 * (term**0.25)

        # 6. 전체 열전달 계수 (U) 계산 (외경 기준)
        R_wall = (do * math.log(do/di)) / (2 * k_m)
        R_total = (1/hs) + Rf_s + R_wall + (do/di)*(Rf_t + 1/ht)
        U_new = 1 / R_total

        # 7. 새로운 벽면 온도(Tw) 도출 (Q/A = U*LMTD = hs*(Tsat - Tw))
        Tw_new_k = T_sat_k - (U_new * LMTD / hs)

        error = abs(Tw_k - Tw_new_k)
        print(f"  Iter {i+1:02d}: Tw = {Tw_k-273.15:.2f} C, ht = {ht:.0f}, hs = {hs:.0f}, U = {U_new:.1f}")
        
        Tw_k = Tw_new_k
        U_calc = U_new
        if error < 0.05: # 오차가 0.05 K 미만이면 수렴
            break

    # ---------------------------------------------------------
    # STEP 7: 압력 강하 계산 (튜브 측만 예시로 포함)
    # ---------------------------------------------------------
    # 마찰 계수 (간이식: f = 0.046 * Re^-0.2 for turbulent)
    f = 0.046 * (Re_c**-0.2)
    L_total = L * nt_passes
    
    # 튜브 내부 압력 강하
    dP_tubes = f * (L_total / di) * (rho_c * v_c**2 / 2)
    # 리턴 커버 압력 강하 (다회 통과 기준 Ke = 1.6) 
    dP_return = 1.6 * (rho_c * v_c**2 / 2) * nt_passes
    dP_total = dP_tubes + dP_return

    print(f"\n[STEP 7] Tube-Side Pressure Drop")
    print(f" - Total dP: {dP_total / 1000:.2f} kPa")

    # ---------------------------------------------------------
    # STEP 8: 최적화 및 결과 확인
    # ---------------------------------------------------------
    A_required = Q / (U_calc * LMTD)
    A_provided = math.pi * do * L * Nt
    Margin = (A_provided - A_required) / A_required * 100

    print(f"\n[STEP 8] Final Design Assessment")
    print(f" - Required Area: {A_required:.2f} m^2")
    print(f" - Provided Area: {A_provided:.2f} m^2")
    print(f" - Safety Margin: {Margin:.1f} %")
    
    if Margin >= 0:
        print(" => 결론: 현재 설계가 요구 조건을 만족합니다.")
    else:
        print(" => 결론: 전열 면적이 부족합니다. 튜브 수(Nt)나 길이(L)를 늘려야 합니다.")

if __name__ == "__main__":
    condenser_design_coolprop()