import math

def calculate_orifice_diameter(Q, delta_P, rho, Cd=0.62):
    """     오리피스 튜브 직경 계산 함수
    Q: 냉매 유량 (m^3/s)
    delta_P: 압력 차 (Pa)
    rho: 냉매 밀도 (kg/m^3)
    C: 유량 계수 (기본값 0.62)
    반환값: 오리피스 직경 (m)     """

    # # 압력 차에 따른 루트 계산
    # root_term = math.sqrt((2 * delta_P) / rho)

    # # 분모 계산
    # denominator = Cd * math.pi * root_term

    # # 직경 계산
    # d = math.sqrt((4 * Q) / denominator)

    Area = Q/(Cd*math.sqrt(2*(delta_P / rho)))
    d = 2*math.sqrt(Area/math.pi)

    return d

def get_color_from_diameter(diameter):
    # Predefined diameter-color mapping
    orifice_tubes = {
        0.052: "Green",
        0.057: "Orange",
        0.062: "Red",
        0.067: "Blue",
        0.072: "Black"
    }
    # Find the closest matching diameter
    closest = min(orifice_tubes.keys(), key=lambda x: abs(x - diameter))
    return f"Closest orifice tube for {diameter:.3f} inches is {orifice_tubes[closest]} (diameter: {closest:.3f} inches)."


# 예시 조건-2
mref = 230 #kg/h
mref = mref/3600    # kg/s
rho = 1200          # 냉매 밀도 (kg/m^3)
Q = mref/rho        # m3/s
# delta_P = 1551*1000  # 압력 차 (Pa)
delta_P = 1730*1000  # 압력 차 (Pa)

# 함수 호출
diameter_m = calculate_orifice_diameter(Q, delta_P, rho)
diameter_mm = diameter_m * 1000
diameter_inch = (diameter_m * 1000) / 25.4

# 출력 (mm 단위로 변환)
print(f"냉매 질량유량: {mref:.5f} kg/s")
print(f"냉매 유량: {Q:.6f} m3/s")
print(f"냉매 압력차이: {delta_P/1000:.3f} kPa")
print(f"계산된 오리피스 튜브 직경: {diameter_mm:.3f} mm")
print(f"계산된 오리피스 튜브 직경: {diameter_inch:.3f} inch")

color = get_color_from_diameter(diameter_inch)
print(color)

# End of Code