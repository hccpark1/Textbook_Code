
from CoolProp.CoolProp import PropsSI

def calculate_accumulator_volume(
    refrigerant_mass_kg = 0.9,        # 전체 냉매 질량 (kg)
    storage_ratio=0.8,          # 어큐뮬레이터 저장 비율 (0.5~0.8 권장)
    oil_mass_kg = 0.150,          # 냉동유 오일량 (kg)
    desiccant_mass_g = 180  ,     # 건조제 중량(g) (100~200g 권장) * 0.96 -> cc
    specific_volume = 0.0013,       # 냉매 비체적 (m³/kg) @ 95°C 포화 상태      
):
    m1 = refrigerant_mass_kg * storage_ratio    # [kg] 냉매량의 80% 저장공간(migration 고려)
    m2 = 25 / 1000                              # [kg] 냉매 주입 공차
    m3 = desiccant_mass_g / 1000                # [kg] 건조제 중량(g) → kg 변환
    m4 = oil_mass_kg                            # [kg] 냉동유 오일량 (kg)
    m_total = m1 + m2 + m3 + m4                 # [kg] 총 질량
    print(f"Accumulator 내부 질량: {m_total} kg")

    # 액체 냉매 저장 용적 계산 (kg → cc 변환)
    accumulator_volume = m_total * specific_volume * 1000000  # m³ → cc

    return round(accumulator_volume, 2)


# 계산 실행

acc_volume = calculate_accumulator_volume()

print(f"어큐뮬레이터 최소 요구 용량: {acc_volume} cc")
Pref_in = 0.2     # [MPaG] ±0.02 MPaG
Vref_in = 100.0       # [kg/h] ±10kg/hr
dP_accumulator = 20.0   # [kPaG] (0.2kgf/㎡G) 
print(f"Max 압력손실 : {dP_accumulator} kPaG")
print(f"No Leak 압력 : {Pref_in * 7.5} MPaG")
print(f"No Burst 압력 : {Pref_in * 12.25} MPaG")
