import math

def calculate_condenser():
    # --- STEP 1: 설계 데이터 정의 (Example: Steam Condenser) ---
    # 뜨거운 유체 (Steam)
    m_h = 2.0           # 질량 유량 (kg/s)
    T_hi = 100.0        # 입구 온도 (C) -> 포화 증기 가정
    T_ho = 40.0         # 출구 온도 (C) -> 과냉각 포함
    T_sat = 100.0       # 응축 온도 (C)
    L_vap = 2257000     # 증발 잠열 (J/kg)
    Cp_h_liq = 4180     # 응축액 비열 (J/kg.K)
    
    # 차가운 유체 (Cooling Water)
    m_c = 50.0          # 질량 유량 (kg/s)
    T_ci = 25.0         # 입구 온도 (C)
    rho_c = 997         # 밀도 (kg/m3)
    Cp_c = 4180         # 비열 (J/kg.K)
    mu_c = 0.00089      # 점도 (Pa.s)
    k_c = 0.6           # 열전도도 (W/m.K)
    
    # 기하학적 구조 (Initial Guess)
    do = 0.01905        # 튜브 외경 (19.05mm)
    di = 0.01575        # 튜브 내경 (15.75mm)
    L = 6.0             # 튜브 길이 (m)
    Nt = 500            # 튜브 개수
    nt = 2              # 튜브 패스 수
    k_m = 50            # 튜브 재질 열전도도 (Carbon Steel)
    Rf_s = 0.0002       # 쉘 측 오염 저항
    Rf_t = 0.0001       # 튜브 측 오염 저항

    # --- STEP 2: 열량(Q) 및 LMTD 계산 ---
    # 전체 열부하 (잠열 + 현열)
    Q = m_h * (L_vap + Cp_h_liq * (T_sat - T_ho)) 
    # 냉각수 출구 온도 계산
    T_co = T_ci + Q / (m_c * Cp_c)
    
    dt1 = T_hi - T_co
    dt2 = T_ho - T_ci
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    
    print(f"--- Step 2: Thermal Duty ---")
    print(f"Heat Duty (Q): {Q/1e6:.2f} MW")
    print(f"Coolant T_out: {T_co:.2f} C")
    print(f"LMTD: {lmtd:.2f} C\n")

    # --- STEP 4: 튜브 측 열전달 계수 (h_t) ---
    A_flow_total = (math.pi * di**2 / 4) * (Nt / nt)
    v_c = m_c / (rho_c * A_flow_total)
    Re_c = (rho_c * v_c * di) / mu_c
    Pr_c = (Cp_c * mu_c) / k_c
    # 난류 가정 (Dittus-Boelter)
    Nu_c = 0.023 * Re_c**0.8 * Pr_c**0.4
    h_t = (Nu_c * k_c) / di
    
    print(f"--- Step 4: Tube Side ---")
    print(f"Velocity: {v_c:.2f} m/s, Re: {Re_c:.0f}")
    print(f"h_t: {h_t:.2f} W/m2.K\n")

    # --- STEP 5 & 6: 쉘 측 h_s 및 반복 계산 (Iteration) ---
    # 초기 가정: 벽면 온도 Tw는 유체 온도의 평균
    Tw = (T_sat + T_ci) / 2
    h_s = 0 # 초기화
    
    print(f"--- Step 6: Iteration for h_s and U ---")
    for i in range(10): # 10회 반복 수렴
        T_film = T_sat - 0.75 * (T_sat - Tw)
        # 응축액 물성 (Simplified for example)
        rho_l = 960; k_l = 0.68; mu_l = 0.00028
        
        # Horizontal tube condensation (Nusselt)
        term = (rho_l**2 * 9.81 * L_vap * k_l**3) / (mu_l * do * (T_sat - Tw))
        h_s = 0.725 * (term**0.25)
        
        # Overall U calculation (Area based on do)
        R_wall = (do * math.log(do/di)) / (2 * k_m)
        total_R = (1/h_s) + Rf_s + R_wall + (do/di)*(Rf_t + 1/h_t)
        U_calc = 1 / total_R
        
        # 새로운 벽면 온도 Tw 계산
        # Q/A = h_s(T_sat - Tw) = U(LMTD)
        Tw_new = T_sat - (U_calc * lmtd / h_s)
        
        if abs(Tw - Tw_new) < 0.01:
            break
        Tw = Tw_new
        print(f"Iter {i+1}: U = {U_calc:.2f}, Tw = {Tw:.2f}")

    # --- STEP 7: 면적 검토 및 압력 강하 ---
    A_required = Q / (U_calc * lmtd)
    A_provided = math.pi * do * L * Nt
    Excess = (A_provided - A_required) / A_required * 100
    
    print(f"\n--- Final Results ---")
    print(f"Required Area: {A_required:.2f} m2")
    print(f"Provided Area: {A_provided:.2f} m2")
    print(f"Area Excess: {Excess:.2f} %")
    
    if Excess < 0:
        print("결과: 면적이 부족합니다. 튜브 수나 길이를 늘리십시오.")
    else:
        print("결과: 설계 조건 만족.")

if __name__ == "__main__":
    calculate_condenser()