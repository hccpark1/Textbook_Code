import numpy as np

# --- 입력 데이터 ---
# 저온 유체 (물)
m_dot_c = 0.75        # kg/s
cp_c = 4.18           # kJ/kg·K (물의 비열)
T_c_in = 38           # °C

# 고온 유체 (오일)
m_dot_h = 1.5         # kg/s
cp_h = 1.884          # kJ/kg·K
T_h_in = 116          # °C

# 열교환기 사양
A = 13                # m²
# 전체 열전달 계수 (W/m²·K를 kW/m²·K로 변환: 340 W/m²·K = 0.340 kW/m²·K)
U = 0.340             # kW/m²·K

# --- 1. 열용량률 (C) 계산 ---
C_c = m_dot_c * cp_c  # kW/K
C_h = m_dot_h * cp_h  # kW/K

# 최소 및 최대 열용량률 (C_min, C_max) 및 용량률 비율 (C_r)
C_min = min(C_h, C_c)
C_max = max(C_h, C_c)
C_r = C_min / C_max

print(f"--- 열용량률 계산 ---")
print(f"물(저온) 열용량률 (C_c): {C_c:.4f} kW/K")
print(f"오일(고온) 열용량률 (C_h): {C_h:.4f} kW/K")
print(f"최소 열용량률 (C_min): {C_min:.4f} kW/K")
print(f"용량률 비율 (C_r = C_min/C_max): {C_r:.4f}")
print("--------------------------\n")


# --- 2. 전달 단위 수 (NTU) 계산 ---
# NTU = U * A / C_min
NTU = (U * A) / C_min

print(f"--- 전달 단위 수 (NTU) 계산 ---")
print(f"전달 단위 수 (NTU): {NTU:.4f}")
print("--------------------------\n")


# --- 3. 열교환기 효율 (epsilon) 계산 (역류) ---
# 역류(Counter flow) 열교환기의 NTU-epsilon 관계식
if C_r == 1:
    # C_r = 1인 경우 (특수 경우)
    epsilon = NTU / (1 + NTU)
else:
    # 일반적인 경우
    epsilon = (1 - np.exp(-NTU * (1 - C_r))) / (1 - C_r * np.exp(-NTU * (1 - C_r)))

print(f"--- 열교환기 효율 (epsilon) 계산 ---")
print(f"열교환기 효율 (ε): {epsilon:.4f}")
print("--------------------------\n")

# --- 4. 최대 가능 열전달률 (Q_max) 계산 ---
# Q_max = C_min * (T_h_in - T_c_in)
Q_max = C_min * (T_h_in - T_c_in)

print(f"--- 최대 열전달률 (Q_max) 계산 ---")
print(f"최대 가능 온도 차 (ΔT_max): {T_h_in - T_c_in:.1f} K")
print(f"최대 가능 열전달률 (Q_max): {Q_max:.2f} kW")
print("--------------------------\n")


# --- 5. 총 열전달률 (Q) 계산 ---
# Q = epsilon * Q_max
Q = epsilon * Q_max

print(f"--- 최종 결과 ---")
print(f"총 열전달률 (Q): {Q:.2f} kW")
print("====================================")
