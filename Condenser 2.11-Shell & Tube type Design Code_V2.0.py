import math
import CoolProp.CoolProp as CP

def design_shell_and_tube_condenser(m_ncg_kg_s=0.0):
    """
    쉘-튜브 응축기 설계 (CoolProp, SBG, Bell-Delaware 통합)
    :param m_ncg_kg_s: 비응축 가스(Air) 질량 유량 (kg/s). 0이면 순수 응축.
    """
    print(f"\n{'='*50}")
    print(f"응축기 설계 평가 (비응축 가스 유량: {m_ncg_kg_s} kg/s)")
    print(f"{'='*50}")

    # --- STEP 1: 설계 조건 및 기하학적 형상 정의 ---
    P_shell = 101325.0         # 쉘 측 압력 (Pa) - 대기압
    P_tube = 300000.0          # 튜브 측 압력 (Pa) - 3 bar
    m_steam = 2.0              # 증기 질량 유량 (kg/s)
    m_cw = 50.0                # 냉각수 질량 유량 (kg/s)
    T_cw_in = 25 + 273.15      # 냉각수 입구 온도 (K)

    # 기하 구조 (Geometry)
    Ds = 0.6                   # 쉘 내경 (m)
    do = 0.01905               # 튜브 외경 (19.05 mm)
    di = 0.01575               # 튜브 내경 (15.75 mm)
    Pt = 0.0254                # 튜브 피치 (m, Triangular)
    L = 6.0                    # 튜브 길이 (m)
    Nt = 500                   # 튜브 총 개수
    nt = 2                     # 튜브 패스 수
    Bc = 0.25                  # 배플 컷 (25%)
    B = 0.35                   # 배플 간격 (m)
    k_m = 50.0                 # 튜브 재질 열전도도 (W/m.K)
    Rf_s = 0.0002              # 쉘 측 오염 저항
    Rf_t = 0.0001              # 튜브 측 오염 저항

    # --- STEP 2: CoolProp을 이용한 물성치 산출 및 열부하 계산 ---
    # 2.1 증기(Water) 물성 (포화 상태 기준)
    T_sat = CP.PropsSI('T', 'P', P_shell, 'Q', 1, 'Water')
    H_vap = CP.PropsSI('H', 'P', P_shell, 'Q', 1, 'Water')
    H_liq = CP.PropsSI('H', 'P', P_shell, 'Q', 0, 'Water')
    L_vap = H_vap - H_liq      # 증발 잠열 (J/kg)
    
    # 2.2 냉각수(Cooling Water) 출구 온도 계산
    Cp_cw_in = CP.PropsSI('C', 'T', T_cw_in, 'P', P_tube, 'Water')
    Q_latent = m_steam * L_vap
    
    # 비응축 가스(Air)가 있을 경우 현열 추가
    Q_sensible_gas = 0.0
    if m_ncg_kg_s > 0:
        Cp_air = CP.PropsSI('C', 'T', T_sat, 'P', P_shell, 'Air')
        # 수정됨: 포화 증기의 비열은 T, P 대신 P와 건도(Q=1)로 구해야 함
        Cp_steam = CP.PropsSI('C', 'P', P_shell, 'Q', 1, 'Water') 
        # 과냉각을 5K로 가정하여 가스 혼합물의 현열 변화 계산
        T_gas_out = T_sat - 5.0 
        Q_sensible_gas = (m_steam * Cp_steam + m_ncg_kg_s * Cp_air) * (T_sat - T_gas_out)
    
    Q_total = Q_latent + Q_sensible_gas
    T_cw_out = T_cw_in + Q_total / (m_cw * Cp_cw_in)
    
    # LMTD 계산
    dt1 = T_sat - T_cw_out
    dt2 = (T_sat - 5.0 if m_ncg_kg_s > 0 else T_sat) - T_cw_in
    LMTD = (dt1 - dt2) / math.log(dt1 / dt2)

    # --- STEP 3: 튜브 측(냉각수) 열전달 계수 산출 ---
    T_cw_avg = (T_cw_in + T_cw_out) / 2
    rho_cw = CP.PropsSI('D', 'T', T_cw_avg, 'P', P_tube, 'Water')
    mu_cw = CP.PropsSI('V', 'T', T_cw_avg, 'P', P_tube, 'Water')
    k_cw = CP.PropsSI('L', 'T', T_cw_avg, 'P', P_tube, 'Water')
    Cp_cw_avg = CP.PropsSI('C', 'T', T_cw_avg, 'P', P_tube, 'Water')

    A_tube_flow = (math.pi * di**2 / 4) * (Nt / nt)
    v_cw = m_cw / (rho_cw * A_tube_flow)
    Re_cw = (rho_cw * v_cw * di) / mu_cw
    Pr_cw = (Cp_cw_avg * mu_cw) / k_cw
    Nu_cw = 0.023 * Re_cw**0.8 * Pr_cw**0.4  # Dittus-Boelter
    h_t = (Nu_cw * k_cw) / di

    # --- STEP 4: 쉘 측 열전달 계수 계산 (SBG법 및 반복 계산) ---
    Z = Q_sensible_gas / Q_total if Q_total > 0 else 0.0
    
    T_wall = (T_sat + T_cw_avg) / 2
    for iteration in range(15):
        T_film = T_sat - 0.75 * (T_sat - T_wall)
        
        # 필름 온도는 과냉각(Subcooled) 상태이므로 T와 P 사용 가능
        rho_l = CP.PropsSI('D', 'T', T_film, 'P', P_shell, 'Water')
        mu_l = CP.PropsSI('V', 'T', T_film, 'P', P_shell, 'Water')
        k_l = CP.PropsSI('L', 'T', T_film, 'P', P_shell, 'Water')
        
        # 수평 튜브 응축 열전달 계수 (Nusselt)
        term = (rho_l**2 * 9.81 * L_vap * k_l**3) / (mu_l * do * max(1e-5, (T_sat - T_wall)))
        h_cond = 0.725 * (term**0.25)
        
        h_eff = h_cond
        h_g = 0.0
        # 비응축 가스가 있는 경우 (Silver-Bell-Ghaly)
        if m_ncg_kg_s > 0:
            A_shell_flow = Ds * B * (1 - do/Pt)
            v_gas = (m_steam + m_ncg_kg_s) / (CP.PropsSI('D', 'T', T_sat, 'P', P_shell, 'Air') * A_shell_flow)
            mu_g = CP.PropsSI('V', 'T', T_sat, 'P', P_shell, 'Air')
            k_g = CP.PropsSI('L', 'T', T_sat, 'P', P_shell, 'Air')
            Cp_g = CP.PropsSI('C', 'T', T_sat, 'P', P_shell, 'Air')
            
            Re_g = (CP.PropsSI('D', 'T', T_sat, 'P', P_shell, 'Air') * v_gas * do) / mu_g
            h_g = 0.36 * (Re_g**0.55) * ((Cp_g * mu_g)/k_g)**(1/3) * (k_g / do)
            h_eff = 1 / ((1 / h_cond) + (Z / h_g))

        # 총괄 열전달 계수 (U)
        R_wall = (do * math.log(do/di)) / (2 * k_m)
        total_R = (1/h_eff) + Rf_s + R_wall + (do/di)*(Rf_t + 1/h_t)
        U_calc = 1 / total_R
        
        # T_wall 업데이트
        T_wall_new = T_sat - (U_calc * LMTD / h_eff)
        if abs(T_wall - T_wall_new) < 0.05:
            break
        T_wall = T_wall_new

    A_req = Q_total / (U_calc * LMTD)
    A_prov = math.pi * do * L * Nt

    # --- STEP 5: 쉘 측 압력 강하 (Bell-Delaware Method) ---
    # 수정됨: 포화 증기의 밀도와 점도는 T 대신 건도(Q=1)로 구해야 함
    rho_s = CP.PropsSI('D', 'P', P_shell, 'Q', 1, 'Water') 
    mu_s = CP.PropsSI('V', 'P', P_shell, 'Q', 1, 'Water')
    
    # 5.1 교차류 최소 단면적 (Sm)
    Sm = B * (Ds - do + (Ds - do)/Pt * (Pt - do))
    Gs = m_steam / Sm
    Re_s = (Gs * do) / mu_s
    
    # 5.2 이상적 튜브 뱅크 마찰 계수 및 압력 강하 (Dpi)
    fi = 0.5 * (1.33 / (Pt/do))**(10/math.sqrt(max(Re_s, 1))) * Re_s**-0.22 if Re_s > 100 else 1.5/Re_s
    Ntc = (Ds * (1 - 2*Bc)) / (Pt * math.sin(math.radians(60)))
    Dpi = 2 * fi * Gs**2 * Ntc / rho_s
    
    # 5.3 누설 및 우회 보정 계수 (간략화된 형태)
    Rl = 0.7  
    Rb = 0.8  
    Nb = L / B - 1  
    
    Dp_cross = Dpi * (Nb - 1) * Rl * Rb
    Dp_total_shell = Dp_cross * 1.3 
    
    # --- STEP 6: 결과 출력 ---
    print(f"[열적 성능]")
    print(f" - 열부하(Q): {Q_total/1e6:.2f} MW")
    print(f" - LMTD: {LMTD:.2f} K")
    if m_ncg_kg_s > 0:
        print(f" - SBG Z-Factor: {Z:.5f}")
        print(f" - 가스상 열전달 계수(h_g): {h_g:.1f} W/m2.K")
    print(f" - 액막 응축 열전달 계수(h_cond): {h_cond:.1f} W/m2.K")
    print(f" - 유효 쉘측 열전달 계수(h_eff): {h_eff:.1f} W/m2.K")
    print(f" - 총괄 열전달 계수(U): {U_calc:.1f} W/m2.K")
    print(f" - 필요 면적: {A_req:.1f} m2 / 제공 면적: {A_prov:.1f} m2")
    
    print(f"\n[수력학적 성능 (Bell-Delaware)]")
    print(f" - 쉘 측 레이놀즈 수(Re_s): {Re_s:.0f}")
    print(f" - 이상적 교차류 압력 강하(Dpi): {Dpi:.2f} Pa")
    print(f" - 총 쉘 측 압력 강하(Dp_total): {Dp_total_shell/1000:.2f} kPa")

# 1. 비응축 가스가 없는 순수 응축 조건 (NCG = 0 kg/s)
design_shell_and_tube_condenser(m_ncg_kg_s=0.0)

# 2. 비응축 가스가 포함된 조건 (Air 0.05 kg/s 혼입)
design_shell_and_tube_condenser(m_ncg_kg_s=0.05)