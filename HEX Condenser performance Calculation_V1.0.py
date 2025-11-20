import math
from CoolProp.CoolProp import PropsSI

def get_desnity_enthalpy(T, P):
    P_pa = P                # Pa
    Temp_K = 273.15 + T      # 온도 (K)
    # 밀도, 엔탈피, 엔트로피 계산
    RHO_liq = PropsSI('D', 'T', Temp_K, 'Q', 0, 'R134a')
    RHO_gas = PropsSI('D', 'T', Temp_K, 'Q', 1, 'R134a')

    return RHO_liq, RHO_gas

def fluid_properties(T, P, fluid):   # 물성치 계산
    P_pa = P                 # Pa
    Temp_K = 273.15 + T      # 온도 (K)    
    RHO = PropsSI('D', 'T', Temp_K, 'P', P_pa, fluid)       # 밀도 [kg/m3]
    CP = PropsSI('C', 'T', Temp_K, 'P', P_pa, fluid)        # 비열 [J/kg-K]
    MU = PropsSI('V', 'T', Temp_K, 'P', P_pa, fluid)        # 점성 계수 [Pa-s]
    K = PropsSI('L', 'T', Temp_K, 'P', P_pa, fluid)         # 열전도율 [W/m-K]
    PR = PropsSI('PRANDTL', 'T', Temp_K, 'P', P_pa, fluid)  # 프란틀 수

    return RHO, CP, K, MU, PR

# --- ⚙️ 열전달 계수 계산 메서드 ---
def air_side_area(L_cond,H_cond,P_tube,W_tube,H_tube,H_fin,P_fin):
    # 공기 측 (External) 열전달 면적 A_air = A_fin + Ao_tube 를 계산. (1-row tube 한정)
    N_tube = math.floor(H_cond / P_tube)    # 소수점 이하 버리고 내림을 수행
    
    # 핀 면적 (A_fin)
    N_fin_per_row = (math.floor(L_cond / P_fin))  # 루버핀 수량/row
    N_total_fin = N_fin_per_row * (N_tube + 1) 
    H_fin_act = math.sqrt(H_fin**2 + (P_fin/2)**2)  # 루버핀 빗변의 길이 
   
    f_corrugation = 1.0  # 루버 핀 보정 계수
    A_fin = 2 * (W_tube * H_fin_act) * N_total_fin * f_corrugation  # m^2
    print("** Air side 외부 표면적")          
    print(f"N_tube= {N_tube:.0f} ea, (N_fin_per_row)= {N_fin_per_row:.0f}ea, N_total_fin= {N_total_fin:.0f}ea")
    print(f"H_fin_act= {H_fin_act:.6f} m, A_fin= {A_fin:.3f} m2, A_fin 보정후= {A_fin:.3f} m2") 
    
    # 튜브 외부 표면적 (Ao_tube)
    Ao_tube = 2 * (L_cond * W_tube) * N_tube    # m^2
    A_air = A_fin + Ao_tube                     # m^2  
    print(f"Ao_tube= {Ao_tube:.3f} m2, Air측 총 표면적(A_air)= {A_air:.3f} m2")
    return A_fin, Ao_tube, A_air, N_tube


def refrigerant_side_area(H_tube,THK_tube,W_tube,N_port,N_tube,L_cond):
    """ 냉매 측 (Internal) 열전달 면적을 계산합니다. """
    H_port = H_tube - 2 * THK_tube
    W_port = (W_tube - (N_port + 1) * THK_tube) / N_port
    
    L_wet = 2 * (H_port + W_port) # 단일 포트의 내부 습윤 둘레(Wetted perimeter)
    A_port = H_port * W_port
    Dh_port = 4 * A_port / L_wet
    A_ref = L_wet * L_cond * N_tube

    print("** 냉매 side 내부 표면적")
    print(f"H_port= {H_port:.5f} m, W_port= {W_port:.5f} m, L_wet= {L_wet:.6f} m")   
    print(f"A_port= {A_port:.7f} m2, Dh_port= {Dh_port:.5} m, A_ref= {A_ref:.4f} m2")
    print(F"Dh_port={Dh_port:.6f} m")
    return H_port, W_port, L_wet, A_port, Dh_port, A_ref    


def calculate_air_side_h(N_tube,H_tube,H_cond,V_air,RHO_air,P_louver,MU_air,PR_air,CP_air) :
    # 공기 측 (External) 열전달 계수 (h_air)를 계산.
    sigma = 1.0 - (N_tube * H_tube) / H_cond    # 수축률
    u_max = V_air / sigma if sigma > 0 else 0.0     # [m/s]
    Re_Lp = (RHO_air * u_max * P_louver) / MU_air
    print("-" * 40)
    print("** Air side 열전달 계수")
    print(f"Fin 수축률(sigma) = {sigma:.4f} ")
    print(f"공기 최대 풍속(u_max) = {u_max:.4f} m/s")
    print(f"Renold수-루버핀(Re_Lp) = {Re_Lp:.4f} ")
    # Re_Lp = (RHO_air * V_air * P_louver) / MU_air
    # Louver Fin에 대한 대표적 경험식: j = 0.208 * Re_Lp ^ -0.29 (단순 근사치)
    j_factor = 0.208 * (Re_Lp ** (-0.29))
    G_max = RHO_air * u_max
    Pr_correction = PR_air ** (-2.0/3.0)
    h_air = j_factor * G_max * CP_air * Pr_correction     # [W/m^2-K]
    print(f"Colburn j-factor(j-factor) = {j_factor:.4f} ")
    print(f"최대 질량 유속(G_max) = {G_max:.4f} ")
    print(f"Air side 대류 열전달 계수(h_air) = {h_air:.4f} ")
    return h_air

def calculate_air_side_h2(RHO_air,V_air,P_louver,MU_air,PR_air,Ang_louver,P_fin,L_finin,W_tube,L_louver,P_tube,t_fin,CP_air) :
    # 공기 측 (External) 열전달 계수 (h_air)를 계산.
    Re_Lp = (RHO_air * V_air * P_louver) / MU_air
    j1 = Re_Lp**(-0.56)
    j2 = (Ang_louver/90)**0.27
    j3 = (P_fin / P_louver)**(-0.14)
    j4 = (L_finin / P_louver)**(-0.29)
    j5 = (W_tube / P_louver)**(-0.23)
    j6 = (L_louver / P_louver)**0.68
    j7 = (P_tube / P_louver)**(-0.28)
    j8 = (t_fin / P_louver)**(-0.05)

    Pr_correction = PR_air ** (-2.0/3.0)
    j_factor2 = 1.21 * j1 * j2 * j3 * j4 * j5 * j6 * j7 * j8
    h_air2 = j_factor2 * RHO_air * V_air * CP_air * Pr_correction

    # Pressure drop (NOT finished)
    # f_air = 4.05 * Re_Lp**(-0.522) * (math.cos(Ang_louver))**(-1.94) * (P_louver/P_fin)**0.233
    # G_ac = (RHO_air * V_air) / sigma
    # dP_air = f_air * (A_as * G_ac**2)/(A_ac * 2 * RHO_air)
    
    return h_air2

def calculate_air_side_h3(RHO_air,V_air,P_louver,MU_air,PR_air,Ang_louver,P_fin,L_finin,W_tube,L_louver,P_tube,t_fin,CP_air) :
    # 공기 측 (External) 열전달 계수 (h_air)를 계산.
    Re_Lp = (RHO_air * V_air * P_louver) / MU_air
    j1 = Re_Lp**(-0.42) * H_louver**0.33
    j2 = (L_louver / H_fin)**0.33
    j3 = H_fin**0.26
    j4 = 1000**0.59
    St_Pr_23 = 0.249 * j1 * j2 * j3 * j4
    h_air3 = St_Pr_23 * RHO_air * V_air * CP_air 

    # h_air3 = 0.249* j_factor2 * RHO_air * V_air * CP_air * Pr_correction
    print(f"h_air3 = {h_air3:.5f} ")
    return h_air3


def calculate_refrigerant_side_h(Dh_port,A_port,N_tube,N_port,m_ref,MU_ref,PR_ref,K_ref,T_cond_in, P_cond_in ):
    # Returns: float: 냉매 측 열전달 계수 h_ref [W/m^2-K] 
 
    N_total_ports = N_tube * N_port                    # 전체 포트 수     
    G_ref = m_ref / (N_total_ports * A_port / 2)    # 냉매 질량 유속 (G_ref = m_ref / A_flow) [kg/m^2-s]
    Re_ref = (G_ref * Dh_port) / MU_ref              # 냉매 레이놀즈 수 (Re_ref) - 액상 가정 [무차원]  

    # 단순화된 Dittus-Boelter 응축 열전달 상관관계 (Nusselt number 기반의 형태 근사)
    # 예시: Nu = C * Re_ref^a * Pr_ref^b (매우 단순화된 가정)    
    Nu_ref = 0.023 * (Re_ref**0.8) * (PR_ref**0.4)
    h_ref = Nu_ref * (K_ref / Dh_port)             # [W/m^2-K]
    print("-" * 40)
    print("** 냉매 side 열전달 계수")
    print(f"수력직경={Dh_port:.6f} m, 총 포트 수(N_total_ports)={N_total_ports:.0f} ea")
    print(f'G_ref = {G_ref:.5f} kg/s.m2, Re_ref = {Re_ref:.5f} ')
    print(f'h_ref = {h_ref:.5f} ')
    # 실제 응축기는 h_ref이 공기 측보다 훨씬 크므로, 최소값 제한 (5000 W/m^2-K)
   
    quality_x = 0.45
    RHO_liq, RHO_gas = get_desnity_enthalpy(T_cond_in, P_cond_in)
    Co = ((1-quality_x)/quality_x)**0.8 * (RHO_gas / RHO_liq)**0.5 
    f_improve = 1 + (3.8 / Co**0.76)
    h_ref = h_ref * f_improve
    print(f'f_improve = {f_improve:.5f}, 최종 내부 열전달 계수(h_inner) = {h_ref:.5f} ')

    return max(h_ref, 5000.0) 

def calculate_refrigerant_side_h2(Dh_port,A_port,N_tube,N_port,m_ref,MU_ref,PR_ref,K_ref,T_cond_in, P_cond_in ):
    # 2상 영역 냉매 열전달 계수 (Cavallini-Zecchin 상관관계 사용) 
 
    N_total_ports = N_tube * N_port                    # 전체 포트 수     
    G_ref = m_ref / (N_total_ports * A_port / 2)    # 냉매 질량 유속 (G_ref = m_ref / A_flow) [kg/m^2-s]
    Temp_K = 273.15 + T_cond_in      # 온도 (K)
    MU_liq = PropsSI('V', 'T', Temp_K, 'Q', 0, "R134a")        # 점성 계수 [Pa-s]
    MU_vap = PropsSI('V', 'T', Temp_K, 'Q', 1, "R134a")        # 점성 계수 [Pa-s]
    RHO_liq = PropsSI('D', 'T', Temp_K, 'Q', 0, "R134a")        # 점성 계수 [Pa-s]
    RHO_vap = PropsSI('D', 'T', Temp_K, 'Q', 1, "R134a")        # 점성 계수 [Pa-s]
    x = 0.8
    Re_liq = (G_ref * (1 - 0) * Dh_port) / MU_liq              # 냉매 레이놀즈 수 (Re_ref) - 액상 가정 [무차원]  
    Re_vap = (G_ref * 1 * Dh_port) / MU_vap
    Re_eq = Re_liq + Re_vap * (RHO_vap / RHO_liq) * (RHO_liq / RHO_vap)

    h_ref2 = 0.05 * Re_eq**0.8 * PR_ref**0.33 * (K_ref / Dh_port)             # [W/m^2-K]
    print("-" * 40)
    print("** 냉매 side 열전달 계수(2)")
    print(f"수력직경={Dh_port:.6f} m, 총 포트 수(N_total_ports)={N_total_ports:.0f} ea")
    print(f'G_ref = {G_ref:.5f} kg/s.m2, Re_eq = {Re_eq:.5f} ')
    print(f'h_ref2 = {h_ref2:.5f} ')
    # 실제 응축기는 h_ref이 공기 측보다 훨씬 크므로, 최소값 제한 (5000 W/m^2-K)
   
    return max(h_ref2, 5000.0) 

def calculate_overall_u(H_fin, h_air, h_ref, K_fin_tube, t_fin, A_fin, A_air, A_ref):
    # 3. 코어의 전체 열전달 계수 (U_o)를 계산합니다. (공기 측 면적 A_air 기준)
    # 3-1. 핀 효율 (Fin Efficiency, η_f) 계산 ---
    # 핀 길이 (L_fin) [m] - 핀 높이의 절반
    L_fin = (H_fin / 2.0)
    
    m_factor = math.sqrt((2.0 * h_air) / (K_fin_tube * t_fin))  # m factor [1/m]
    # 핀 효율 (η_f)
    m_Lf = m_factor * L_fin
    eta_f = math.tanh(m_Lf) / m_Lf if m_Lf > 1e-6 else 1.0
    print(f'eta_f = {eta_f:.5f}')

    # 3-2. 전체 핀 효율 (Overall Fin Efficiency, η_o) 계산
    eta_o = 1.0 - (A_fin / A_air) * (1.0 - eta_f) if A_air > 0 else 0.0
    print(f'eta_o = {eta_o:.5f}')
    # 3-3. 전체 열전달 계수 (U_o) 계산. 튜브 벽 전도 열저항 0으로 가정
    # R_wall = (THK_tube / K_fin_tube) * (A_air / A_wall) -> 매우 작음
    R_wall_resistance = 0.0 
    
    # U_o (A_air 기준) 계산: 1/U_o = 1/(η_o * h_air) + R_wall + A_air/(h_ref * A_ref)
    if eta_o * h_air == 0 or A_ref == 0:
        return 0.0, eta_o

    U_o = 1.0 / ( (1.0 / (eta_o * h_air)) + R_wall_resistance + (A_air / (h_ref * A_ref)) )
    print(f'U_o = {U_o:.5f} W/m^2-K')
    return U_o, eta_o

# --- 📊 성능 계산 메서드 (NTU, Q) ---

def calculate_effectiveness_ntu(L_cond,H_cond,RHO_air, V_air,CP_air, U_o,A_air,T_cond, T_air_in):
    # 4. 응축기의 Effectiveness (유효도, ε)와 NTU를 계산하고 열 제거량 (Q)을 계산.   
    # 4-1. 공기 측 열용량 유량 (C_air) 계산 ---
    A_front = L_cond * H_cond           # 전면 면적 [m^2]
    m_air = RHO_air * V_air * A_front   # 공기 질량 유량 [kg/s]
    C_air = m_air * CP_air              # 공기 열용량 유량 [W/K]
    print("-" * 40)
    print(f'응축기 전면면적(A_front)= {A_front:.5f} m^2')
    print(f'공기 질량 유량(m_air) = {m_air:.5f} kg/s')
    print(f'공기 열용량 유량(C_air) = {C_air:.5f} W/K')
    
    # 4-2. NTU (Number of Transfer Units) 계산
    NTU = (U_o * A_air) / C_air if C_air > 0 else 0.0

    # 4-3. Effectiveness (ε) 계산 ---
    # 응축기는 C_min = C_air, C_max = C_ref (phase change) -> C_r = 0 인 경우로 간주
    epsilon = 1.0 - math.exp(-NTU)   

    # 4-4. 최대 열 제거량 (Q_max) 및 실제 열 제거량 (Q)
    Q_max = C_air * (T_cond - T_air_in)
    Q = epsilon * Q_max
    print(f'NTU(NTU) = {NTU:.5f} , Effectiveness(ε) = {epsilon:.5f} ')   
    print(f'Qmax (Q_max) = {Q_max:.5f} , 방열량 (Q) = {Q:.5f} ')   
    return epsilon, NTU, Q, C_air

# --- 📈 온도 분석 메서드 ---
def calculate_lmtd_and_temp_rise(T_air_in, Q, C_air, T_cond):
    # 5. 대수 평균 온도차 (LMTD, ΔT_lm) 및 공기 온도 상승을 계산.   
    # 5-1. 공기 출구 온도 (T_air_out) 계산
    if C_air == 0:
        return 0.0, T_air_in

    T_air_out = T_air_in + (Q / C_air)  # Q = C_air * (T_air_out - T_air_in)
    print(f"Tair,out= {T_air_out:.5f} C")
    # 5-2. LMTD 계산. 응축기 (T_cond = 일정 가정)
    dT1 = T_cond - T_air_in  # 입구 온도차
    dT2 = T_cond - T_air_out      # 출구 온도차

    if dT1 == dT2:
        LMTD = dT1
    elif dT1 > 0 and dT2 > 0:
        LMTD = (dT1 - dT2) / math.log(dT1 / dT2)
    else:
        LMTD = 0.0
        
    print(f"LMTD= {LMTD:.5f} C")    
    return LMTD, T_air_out

    

##############################################################################
### 입력 데이터 (HEX 치수 및 냉매 조건)
# Condenser 외형 치수 (m)
L_cond = 680.0 / 1e3     # 코어 길이(가로 길이). 코어 폭=튜브 폭(W_tube)
H_cond = 350.0 / 1e3     # 코어 높이

# 튜브 상세 (m)
W_tube = 16.0 / 1e3            # 튜브 폭
H_tube = 1.8 / 1e3             # 튜브 높이
P_tube = 9.7 / 1e3             # 튜브 피치
THK_tube = 0.2 / 1e3             # 튜브 벽 두께 [mm]
N_port = 16.0                  # 포트 수

# 핀 상세 (m)
P_fin = 2.50 / 1e3            # 핀 피치
H_fin = 8.10 / 1e3            # 핀 높이
t_fin = 0.10 / 1e3            # 핀 소재 두께
L_finin = 16.0                  # 핀 길이
P_louver = 1.30 / 1e3         # 루버 피치
Ang_louver = 25.0              # 루버 앵글(deg)
L_louver = 7.0/1e3            # 루버 길이(m)
H_louver = 0.25 / 1e3         # 루버 높이(m)

# 작동 조건
V_air = 3.5             # 전면 풍속 [m/s]
T_air_in = 35.0         # 입구 공기 온도 [C] (T_air_in)
T_cond = 60.0           # 응축 온도 [C]
T_cond_in = 90.0           # 응축기 입구 온도 [C]
P_cond_in = 17.0 * 98066.5     # kg/cm2(gage) -> Pa(abs)
# m_ref = 0.1             # 냉매 질량 유량 [kg/s]
m_ref = 0.1           # 냉매 질량 유량 [kg/s]  was 0.035
h_fg =140000.0          # 응축 잠열 [J/kg]

## 공기 물성치 상수 (air Properties at T_avg ~ 35 C) 추후 CoolProp 이용으로 변경 예정
# RHO_air = 1.145     # 공기 밀도 [kg/m^3]
# CP_air = 1007.0     # 공기 비열 [J/kg-K]
# MU_air = 1.83e-5    # 공기 점성 계수 [Pa-s]
# K_air = 0.0267      # 공기 열전도율 [W/m-K]
# PR_air = 0.69       # 프란틀 수 (Pr = Cp*mu/k)
RHO_air, CP_air, K_air, MU_air, PR_air = fluid_properties(T_air_in, P=101325, fluid="Air")
print("-" * 40)
print("0. 공기 물성표 -------")
print(f"RHO_air={RHO_air:.3f}kg/m^3, CP_air={CP_air:.1f}J/kg-K, MU_air={MU_air:.5e}Pa-s")
print(f"K_air={K_air:.5f}W/m-K, Pr_air={PR_air:.3f}" )
print("-" * 40)

## 소재 및 냉매 물성치 상수 ---
K_fin_tube = 200.0  # 핀/튜브 열전도율 (알루미늄) [W/m-K]
K_ref = 0.08        # 냉매 열전도율 (응축액 상태, 단순화) [W/m-K]
MU_ref = 2.0e-4     # 냉매 점성 계수 (응축액 상태, 단순화) [Pa-s]
PR_ref = 2.0        # 냉매 프란틀 수 (단순화)


###🎯 계산 실행
# 1. Air side 표면적 계산
A_fin, Ao_tube, A_air, N_tube = air_side_area(L_cond,H_cond,P_tube,W_tube,H_tube,H_fin,P_fin)
    
# 2. Refrigerant side 표면적 계산
H_port, W_port, L_wet, A_port, Dh_port, A_ref = refrigerant_side_area(H_tube,THK_tube,W_tube,N_port,N_tube,L_cond)

# 3. 열전달 계수 계산 (h_air, h_ref)
h_air = calculate_air_side_h(N_tube,H_tube,H_cond,V_air,RHO_air,P_louver,MU_air,PR_air,CP_air)
h_air2 = calculate_air_side_h2(RHO_air,V_air,P_louver,MU_air,PR_air,Ang_louver,P_fin,L_finin,W_tube,L_louver,P_tube,t_fin,CP_air)
h_air3 = calculate_air_side_h3(RHO_air,V_air,P_louver,MU_air,PR_air,Ang_louver,P_fin,L_finin,W_tube,L_louver,P_tube,t_fin,CP_air)
# 2. 냉매 측 (Internal) 열전달 계수 (h_ref)를 계산
h_ref = calculate_refrigerant_side_h(Dh_port,A_port,N_tube,N_port,m_ref,MU_ref,PR_ref,K_ref,T_cond_in, P_cond_in )
h_ref2 = calculate_refrigerant_side_h2(Dh_port,A_port,N_tube,N_port,m_ref,MU_ref,PR_ref,K_ref,T_cond_in, P_cond_in )
# 2. 전체 열전달 계수 계산 (U_o)
U_o, eta_o = calculate_overall_u(H_fin, h_air, h_ref, K_fin_tube, t_fin, A_fin, A_air, A_ref)

# 3. NTU, Effectiveness (ε), 열 제거량 (Q) 계산
epsilon, NTU, Q, C_air = calculate_effectiveness_ntu(L_cond,H_cond,RHO_air, V_air,CP_air, U_o,A_air,T_cond, T_air_in)

# 4. LMTD 및 공기 출구 온도 계산
LMTD, T_air_out = calculate_lmtd_and_temp_rise(T_air_in, Q, C_air, T_cond)


print("*" * 50)
print(f"--- 응축기 열성능 분석 결과 ---")
print(f"1. 치수 및 면적")
print(f'   - 총 Tube 수(N_tube) = {N_tube:.0f} ea')
print(f"   - 공기 측 면적 (A_air): {A_air:.3f} m^2")
print(f"   - 냉매 측 면적 (A_ref): {A_ref:.3f} m^2")
print(f"   - 공기 열용량 유량 (C_air): {C_air:.1f} W/K")
print(f"")
print(f"2. 열전달 계수")
print(f"   - 공기 측 열전달 계수 (h_air): {h_air:.1f} W/m^2-K")
print(f"   - 공기 측 열전달 계수 2 (h_air_2): {h_air2:.1f} W/m^2-K")
print(f"   - 냉매 측 열전달 계수 (h_ref): {h_ref:.1f} W/m^2-K")
print(f"   - 전체 핀 효율 (η_o): {eta_o:.3f}")
print(f"   - 코어 전체 열전달 계수 (U_o): {U_o:.1f} W/m^2-K")
print(f"")
print(f"3. 성능 파라미터")
print(f"   - NTU (무차원): {NTU:.3f}")
print(f"   - 응축기 유효도 (Effectiveness, ε): {epsilon:.3f}")
print(f"   - **열 제거량 (Heat Rejection, Q): {Q/1000.0:.1f} kW**")
print(f"")
print(f"4. 온도 분석")
print(f"   - 입구 공기 온도 (T_air_in): {T_air_in:.1f} C")
print(f"   - 출구 공기 온도 (T_air_out): {T_air_out:.1f} C")
print(f"   - 응축 온도 (T_cond): {T_cond:.1f} C")
print(f"   - 대수 평균 온도차 (ΔT_lm): {LMTD:.1f} K")
print(f"--------------------------------------------------")
print(f"*주의: h_air 및 h_ref 계산에는 복잡한 유체 역학적 현상을 단순화한 경험적")
print(f" 상관관계가 사용되었으므로, 실제 값과 차이가 있을 수 있습니다.")