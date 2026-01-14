import math

def calculate_orifice_diameter():
    """
    CCOT 시스템용 오리피스 튜브 내경 계산 시뮬레이션
    기반 이론: Bernoulli Equation 및 Short Tube Orifice 보정 계수 적용
    """
    
    print("=== CCOT 오리피스 튜브 사이징 계산 시작 ===")
    
    # ---------------------------------------------------------
    # 1. 입력 변수 설정 (Design Inputs)
    # ---------------------------------------------------------
    # 보고서 5절의 가정 시나리오 데이터 적용
    Q_load_kw = 5.5          # 목표 냉방 부하 (kW)
    Cd = 0.70                # 유량 계수 (Discharge Coefficient)
    
    # 냉매 물성치 (R134a) - 보고서 예제 값 적용
    # 실제 엔지니어링에서는 CoolProp 등의 라이브러리로 동적 호출 권장
    
    # 입구 조건 (50°C 과냉각 액체)
    # P_cond는 Pa 단위로 변환 (1 bar = 100,000 Pa)
    P_cond_pa = 1318000      # 약 13.18 bar
    rho_liquid = 1080        # 액체 밀도 (kg/m^3)
    h_in = 271.6             # 입구 엔탈피 (kJ/kg)
    
    # 출구 조건 (2°C 포화 기체/습증기)
    P_evap_pa = 315000       # 약 3.15 bar
    h_out = 399.7            # 출구 엔탈피 (kJ/kg)

    print(f"\n[입력 조건]")
    print(f"  - 냉방 부하: {Q_load_kw} kW")
    print(f"  - 응축 압력(P_high): {P_cond_pa/1000} kPa")
    print(f"  - 증발 압력(P_low): {P_evap_pa/1000} kPa")
    print(f"  - 유량 계수(Cd): {Cd}")

    # ---------------------------------------------------------
    # 2. 필요 질량 유량 계산 (Mass Flow Rate Calculation)
    # ---------------------------------------------------------
    # 공식: m_dot = Q_load / (h_out - h_in)
    
    delta_h = h_out - h_in   # 냉동 효과 (kJ/kg)
    m_req = Q_load_kw / delta_h  # 질량 유량 (kg/s)
    
    print(f"\n[1단계] 필요 질량 유량 계산")
    print(f"  - 단위 질량당 냉동 효과 (Delta h): {delta_h:.1f} kJ/kg")
    print(f"  - 필요 질량 유량 (m_dot): {m_req:.4f} kg/s")

    # ---------------------------------------------------------
    # 3. 단면적 및 내경 계산 (Geometry Calculation)
    # ---------------------------------------------------------
    # 공식: m_dot = Cd * A * sqrt(2 * rho * delta_P)
    # 변형: A = m_dot / (Cd * sqrt(2 * rho * delta_P))
    
    delta_P = P_cond_pa - P_evap_pa  # 압력 차이 (Pa)
    
    # 분모항 계산 (Bernoulli 항)
    bernoulli_term = math.sqrt(2 * rho_liquid * delta_P)
    
    # 단면적 (m^2)
    area_m2 = m_req / (Cd * bernoulli_term)
    area_mm2 = area_m2 * 1e6  # mm^2 변환
    
    print(f"\n[2단계] 오리피스 단면적 계산")
    print(f"  - 압력 차이 (Delta P): {delta_P} Pa")
    print(f"  - 필요 단면적: {area_mm2:.4f} mm^2")

    # 내경 (Diameter) 계산
    # 공식: A = (pi * D^2) / 4  ->  D = sqrt(4 * A / pi)
    diameter_mm = math.sqrt((4 * area_m2) / math.pi) * 1000
    diameter_inch = diameter_mm / 25.4

    # ---------------------------------------------------------
    # 4. 결과 출력 및 표준 규격 매칭 (Result & Selection)
    # ---------------------------------------------------------
    print(f"\n[3단계] 최종 계산 결과")
    print(f"  - 계산된 내경 (mm): {diameter_mm:.3f} mm")
    print(f"  - 계산된 내경 (inch): {diameter_inch:.3f} inch")
    
    print("-" * 30)
    print(">>> 표준 오리피스 튜브 매칭:")
    
    # 표준 규격 딕셔너리 (Color Code)
    standard_sizes = {
        "Brown": 0.047,
        "Green": 0.052,
        "Orange": 0.057,
        "Red": 0.062,
        "Blue": 0.067
    }
    
    # 가장 가까운 규격 찾기
    closest_color = min(standard_sizes, key=lambda k: abs(standard_sizes[k] - diameter_inch))
    closest_size = standard_sizes[closest_color]
    
    print(f"  계산값({diameter_inch:.3f}\")에 가장 근접한 규격은 '{closest_color}' ({closest_size}\") 입니다.")
    
    if diameter_inch > closest_size:
        print("  * 주의: 계산값이 표준값보다 큽니다. 유량 확보를 위해 한 단계 큰 사이즈 고려 필요.")
    else:
        print("  * 참고: 계산값이 표준값 이내입니다. 시스템 안정성을 고려하여 선정하세요.")

if __name__ == "__main__":
    calculate_orifice_diameter()