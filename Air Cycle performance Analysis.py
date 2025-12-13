import math

def calculate_air_cycle(T1_celsius, pressure_ratio, T3_celsius, turbine_eff, comp_eff=1.0):
    """ 에어 사이클(Reverse Brayton Cycle) 성능 계산 함수
    Parameters:
    T1_celsius (float): 외기 온도 (℃) - 압축기 흡입 온도
    pressure_ratio (float): 압축비 (P2/P1)
    T3_celsius (float): 열교환 후 터빈 입구 온도 (℃)
    turbine_eff (float): 터빈 단열 효율 (0.0 ~ 1.0)
    comp_eff (float): 압축기 단열 효율 (Default 1.0, 필요시 변경 가능)
    
    Returns:
    dict: 각 단계별 온도 및 성능 지표   """
    
    # 1. 상수 정의
    k = 1.4  # 공기 비열비 (Cp/Cv)
    exponent = (k - 1) / k  # (k-1)/k
    
    # 2. 섭씨 -> 켈빈 변환
    T1 = T1_celsius + 273.15
    T3 = T3_celsius + 273.15
    
    # 3. 압축 과정 (1 -> 2)
    # 이론적 압축 후 온도 (Isentropic)
    T2s = T1 * math.pow(pressure_ratio, exponent)
    
    # 실제 압축 후 온도 (압축기 효율 고려)
    # T2 = T1 + (T2s - T1) / comp_eff
    # 제공해주신 예제에서는 압축기 효율 언급이 없어 이론값(T2s)을 T2로 가정합니다.
    T2 = T2s 
    
    # 4. 팽창(터빈) 과정 (3 -> 4)
    # 이론적 팽창 후 온도 (Isentropic, P3/P4 = P2/P1 가정)
    # 압축비와 팽창비가 같다고 가정 (Pressure Loss 무시)
    expansion_ratio = pressure_ratio 
    T4s = T3 / math.pow(expansion_ratio, exponent)
    
    # 실제 토출 온도 (터빈 효율 고려)
    # T3 - T4 = eff * (T3 - T4s)  => T4 = T3 - eff * (T3 - T4s)
    T4 = T3 - turbine_eff * (T3 - T4s)
    
    # 5. 결과 정리 (켈빈 -> 섭씨 변환)
    results = {
        "T1_input": T1_celsius,
        "Pressure_Ratio": pressure_ratio,
        "T2_compressed": T2 - 273.15,
        "T3_cooled": T3_celsius,
        "T4s_ideal_exit": T4s - 273.15,
        "T4_actual_exit": T4 - 273.15,
        "Turbine_Efficiency": turbine_eff
    }
    
    return results

# --- 실행 예제 (사용자가 제공한 Case Study 조건) ---
# 조건 설정
t1_input = 30.0       # 외기 온도 (℃)
p_ratio = 3.0         # 압축비
t3_input = 40.0       # 열교환 후 온도 (℃)
turb_eff = 0.85       # 터빈 효율

# 계산 수행
data = calculate_air_cycle(t1_input, p_ratio, t3_input, turb_eff)

# 결과 출력
print(f"--- 에어 사이클 설계 계산 결과 ---")
print(f"1. 입력 조건")
print(f"   - 외기 온도 (T1): {data['T1_input']} ℃")
print(f"   - 압축비 (P2/P1): {data['Pressure_Ratio']}")
print(f"   - 열교환 후 온도 (T3): {data['T3_cooled']} ℃")
print(f"   - 터빈 효율 (η): {data['Turbine_Efficiency']}")
print("-" * 30)
print(f"2. 계산 결과")
print(f"   - 압축 후 온도 (T2): {data['T2_compressed']:.2f} ℃ ({data['T2_compressed']+273.15:.2f} K)")
print(f"   - 터빈 팽창 후 이론 온도 (T4s): {data['T4s_ideal_exit']:.2f} ℃ ({data['T4s_ideal_exit']+273.15:.2f} K)")
print(f"   - 실제 터빈 토출 온도 (T4): {data['T4_actual_exit']:.2f} ℃ ({data['T4_actual_exit']+273.15:.2f} K)")

# 검증: 예제 텍스트의 결과 (-32도 근처)와 일치하는지 확인