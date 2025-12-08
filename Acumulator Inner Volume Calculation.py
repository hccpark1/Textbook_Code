### Acumulator Inner Volume Calculation 

def calculate_accumulator_volume(m_total, gamma, rho_liq, V_oil, V_des):
    # 1. 냉매 마이그레이션으로 인한 부피 계산 (단위: m^3)
    V_ref_m3 = (gamma * m_total) / rho_liq

    # 2. m^3를 cc (cm^3)로 변환 (1 m^3 = 1,000,000 cc)
    V_ref_cc = V_ref_m3 * 1e6

    # 3. 총 어큐뮬레이터 용량 계산
    V_acc = V_ref_cc + V_oil + V_des

    return V_acc

# 예시 Input 및 계산
m_total = 0.6           # 시스템 전체 냉매량 (kg)
gamma = 0.7             # 어큐뮬레이터 저장 비율 (0.5 ~ 0.8)
rho_liq = 1200          # 냉매 밀도 (kg/m^3)
V_oil = 100             # 압축기 오일량 (cc)  100cc = 96g
V_des = 30              # 설계 여유 용량 (cc)

V_acc = calculate_accumulator_volume(m_total, gamma, rho_liq, V_oil, V_des)
print(f"*" * 40)
print(f"시스템 냉매량 = {m_total*1000:.0f} g")
print(f"압축기 오일량 = {V_oil:.0f} cc")
print(f"Accumalator 내용적 = {V_acc:.1f} cc")