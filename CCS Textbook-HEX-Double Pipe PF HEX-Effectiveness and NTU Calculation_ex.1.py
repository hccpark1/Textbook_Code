### 이중관 병렬유동(Parallel Flow) 열교환기의 효율 및 NTU 계산 ###
import numpy as np

# --- 입력 데이터 ---
# 고온 유체 (오일)
m_dot_h = 270         # kg/hr
cp_h = 1.88           # kJ/kg·K
T_h_in = 205          # °C

# 저온 유체 (물)
m_dot_c = 225         # kg/hr
cp_c = 4.18           # kJ/kg·K (물의 비열)
T_c_in = 16           # °C
T_c_out = 44          # °C

# 전체 열전달 계수 (W/m²·K를 kW/m²·K로 변환: 340 W/m²·K = 0.340 kW/m²·K)
U = 0.340             # kW/m²·K

# --- 1. 기본 계산: 열용량률 및 전달된 열량 ---

# 열용량률 (C = m_dot * cp)
C_h = m_dot_h * cp_h  # kW/K (시간당 kg * kJ/kg·K = kJ/hr·K)
C_c = m_dot_c * cp_c  # kW/K

# 전달된 열량 (Q)
# 저온 유체의 온도 변화를 이용
Q = C_c * (T_c_out - T_c_in)

# 최소 및 최대 열용량률 (C_min, C_max) 및 용량률 비율 (C_r)
C_min = min(C_h, C_c)
C_max = max(C_h, C_c)
C_r = C_min / C_max

# 고온 유체 출구 온도 (T_h_out)
# 에너지 평형: Q = C_h * (T_h_in - T_h_out)
T_h_out = T_h_in - (Q / C_h)

print("-" * 40)
print(f"1. 열용량률 및 열량")
print(f"  오일(고온) 열용량률 (C_h): {C_h:.2f} kJ/hr·K")
print(f"  물(저온) 열용량률 (C_c): {C_c:.2f} kJ/hr·K")
print(f"  전달된 열량 (Q): {Q:.2f} kJ/hr")
print(f"  고온 유체 출구 온도 (T_h_out): {T_h_out:.2f} °C")
print(f"  용량률 비율 (C_r = C_min/C_max): {C_r:.4f}")
print("  -------------------------\n")


# a) 필요한 열전달 면적 (A) 계산 ---
# LMTD (대수 평균 온도 차) 법 사용
# 병렬 유동(Parallel flow)
Delta_T1 = T_h_in - T_c_in     # 입구 온도 차
Delta_T2 = T_h_out - T_c_out   # 출구 온도 차

# 대수 평균 온도 차 (LMTD)
if Delta_T1 != Delta_T2:
    LMTD = (Delta_T1 - Delta_T2) / np.log(Delta_T1 / Delta_T2)
else:
    LMTD = Delta_T1 # Delta_T1 == Delta_T2인 경우 (이론적)

# 열전달 면적 (A): Q = U * A * LMTD
A = Q / (U * LMTD)

# Q는 kJ/hr, U는 kW/m²·K (kJ/s·m²·K)이므로, A를 구하려면 단위를 맞춰야 함
# A = (Q[kJ/hr]) / (U[kW/m²·K] * LMTD[K])
# A = (Q[kJ/hr]) / (U[kJ/s·m²·K] * LMTD[K])
# A = (Q / 3600 [kJ/s]) / (U[kW/m²·K] * LMTD[K])
# A = (Q / 3600) / (U * LMTD)
Q_kW = Q / 3600 # kJ/hr -> kJ/s (kW)
A_final = Q_kW / (U * LMTD)

print(f"a) 열전달 면적 (A)")
print(f"  입구 온도 차 (ΔT1): {Delta_T1:.2f} K")
print(f"  출구 온도 차 (ΔT2): {Delta_T2:.2f} K")
print(f"  대수 평균 온도 차 (LMTD): {LMTD:.2f} K")
print(f"  필요한 열전달 면적 (A): {A_final:.2f} m²")
print("  -------------------------\n")


# b) 전달 단위 수 (NTU) 계산 ---
# NTU = U * A / C_min
NTU = (U * A_final) / (C_min / 3600) # C_min을 kW/K로 변환 (kJ/hr·K -> kJ/s·K)
# 또는 NTU = (U * A_final) / (C_c / 3600)  # 여기서는 C_c가 C_min이므로
NTU_final = (U * A_final) / (C_c / 3600)

print(f"b) 전달 단위 수 (NTU)")
print(f"  전달 단위 수 (NTU): {NTU_final:.2f}")
print("  -------------------------\n")


# --- c) 열교환기 효율 (epsilon) 계산 ---
# 1. 실제 전달 열량 (Q)
# Q는 이미 계산됨: Q = 28 * C_c

# 2. 최대 가능 열전달률 (Q_max)
# Q_max = C_min * (T_h_in - T_c_in)
Q_max = C_min * (T_h_in - T_c_in)

# 3. 효율 (epsilon)
# epsilon = Q / Q_max
epsilon = Q / Q_max

# (선택 사항) NTU-epsilon 관계식으로 효율 검증 (병렬 유동)
# epsilon = (1 - exp(-NTU * (1 + C_r))) / (1 + C_r)
epsilon_check = (1 - np.exp(-NTU_final * (1 + C_r))) / (1 + C_r)

print(f"c) 열교환기 효율 (epsilon)")
print(f"  최대 가능 열전달률 (Q_max): {Q_max:.2f} kJ/hr")
print(f"  효율 (ε): {epsilon:.4f}")
print(f"  (NTU-ε 공식 검증: {epsilon_check:.4f})")
print("  -------------------------\n")

# 최종 결과 정리
print("2. 최종 결과 정리")
print(f"  a) 필요한 열전달 면적 (A): {A_final:.2f} m²")
print(f"  b) 전달 단위 수 (NTU): {NTU_final:.2f}")
print(f"  c) 열교환기 효율 (ε): {epsilon:.4f}")
print("  -------------------------\n")