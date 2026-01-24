import math

# 1. 입력 파라미터 설정
pcd = 67.5          # 사판 피치 원 직경 (mm)
num_pistons = 10     # 피스톤 수 (5 * 2)
swp_deg = 19.2    # 사판 경사각 (degree)
piston_dia = 28.98  # 피스톤 외경 (mm)
p_s = 3.5            # 흡입 압력 (kg/cm^2)
p_d = 19.0           # 토출 압력 (kg/cm^2)
rpm = 600           # 회전수 (계산을 위한 임의 설정값)

# 2. 행정거리(Stroke) 계산
# 공식: S = Dp * tan(alpha)
alpha_rad = math.radians(swp_deg)
stroke = pcd * math.tan(alpha_rad)

# 3. 이론 배기량(Displacement) 계산
# 공식: Vd = n * (pi * d^2 / 4) * S
area_cm2 = math.pi * (piston_dia / 10)**2 / 4 # 단위를 cm로 변환
stroke_cm = stroke / 10
displacement_cc = num_pistons * area_cm2 * stroke_cm

# 4. 소요 토크(Torque) 계산
# 공식: T = (Vd * delta_P) / (2 * pi)
delta_p = p_d - p_s
torque_kgf_cm = (displacement_cc * delta_p) / (2 * math.pi)
torque_nm = torque_kgf_cm * 0.0980665 # Nm 단위 변환

# 5. 소요 동력(Power) 계산 (1000 RPM 기준)
# 공식: P = (2 * pi * N * T) / 60,000 (kW)
power_kw = (2 * math.pi * rpm * torque_nm) / 60000
# 입력조건 출력
print(f"** 입력조건 **")
print(f"1. 피스톤 외경: {piston_dia:.3f} mm")
print(f"2. 실린더 PCD 직경: {pcd:.3f} mm")
print(f"3. 사판 경사각: {swp_deg:.3f} degree")
print(f"4. 피스톤 수량: {num_pistons:.3f} ea")
print(f"5. 흡입 압력: {p_s:.3f} kg/cm^2")
print(f"6. 토출 압력: {p_d:.3f} kg/cm^2")
print("----------------------------------")
# 결과 출력
print(f"** 계산 결과 **")
print(f"1. 행정거리 (Stroke): {stroke:.3f} mm")
print(f"2. 이론 배기량 (Displacement): {displacement_cc:.3f} cc/rev")
print(f"3. 소요 토크 (Torque): {torque_kgf_cm:.3f} kgf·cm ({torque_nm:.3f} N·m)")
print(f"4. 소요 동력 (Power @600rpm): {power_kw:.3f} kW")