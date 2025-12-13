### 흡수식 시스템에서 배기가스 폐열회수용 Shell & Tube 열교환기 설계 계산
# 이 코드는 배기가스의 열을 LiBr 용액에 전달하는 Shell & Tube 열교환기의 기본 설계 계산을 수행합니다.

import math

def calculate_heat_exchanger():
    # 1. 입력 조건 (Input Parameters)
    # 설계 목표
    Q_kW = 5.0                  # 목표 열량 [kW]
    Q = Q_kW * 1000             # [W] 단위 변환

    # 배기가스 (Tube Side, Hot Fluid)
    m_dot_gas = 0.05            # 유량 [kg/s], 2.0L 가솔린, 부분 부하 기준
    Tg_in = 500.0               # 배기가스 입구 온도 [C]
    Cp_gas_kJ = 1.1             # 비열 [kJ/kg.K]
    Cp_gas = Cp_gas_kJ * 1000   # [J/kg.K] 단위 변환

    # LiBr 용액 (Shell Side, Cold Fluid)
    Ts_in = 80.0                # 입구 온도 [C]
    Ts_out = 95.0               # 목표 출구 온도 [C], 비등 시작

    # 설계 가정치
    U = 45.0                    # 총괄 열전달 계수 [W/m2.K], (오염 계수 고려된 보수적 수치)

    # 튜브 사양 (SUS Tube)
    D_tube_mm = 12.0            # 외경 [mm]
    D_tube = D_tube_mm / 1000   # [m] 단위 변환
    L_tube_mm = 300.0           # 길이 [mm]
    L_tube = L_tube_mm / 1000   # [m] 단위 변환

    # 2. 계산 단계 (Calculation Steps)
    # [Step 1] 배기가스 출구 온도 (Tg,out) 예측
    # 식: Q = m * Cp * (Tin - Tout)  =>  Tout = Tin - Q / (m * Cp)
    Tg_out = Tg_in - (Q / (m_dot_gas * Cp_gas))

    # [Step 2] 대수 평균 온도차 (LMTD) 계산 (Counter-flow)
    # dT1 = Hot_In - Cold_Out, dT2 = Hot_Out - Cold_In
    dT1 = Tg_in - Ts_out
    dT2 = Tg_out - Ts_in

    if dT1 == dT2:
        LMTD = dT1
    else:
        LMTD = (dT1 - dT2) / math.log(dT1 / dT2)

    # [Step 3] 필요 전열 면적 (A) 산출
    # 식: Q = U * A * LMTD  =>  A = Q / (U * LMTD)
    Area_required = Q / (U * LMTD)

    # [Step 4] 튜브 레이아웃 (Sizing)
    # 튜브 1개당 면적 (표면적)
    Area_per_tube = math.pi * D_tube * L_tube
    
    # 필요 튜브 개수 (올림 처리)
    N_tubes = Area_required / Area_per_tube
    N_tubes_final = math.ceil(N_tubes)

    # ==========================================
    # 3. 결과 출력 (Output)
    # ==========================================
    print(f"--- 설계 계산 결과 (Design Calculation Results) ---")
    print(f"[Input] 목표 열량 (Q): {Q_kW} kW")
    print(f"[Input] 배기가스 유량: {m_dot_gas} kg/s")
    print(f"-" * 40)
    print(f"[Step 1] 배기가스 출구 온도 (Tg,out): {Tg_out:.2f} ℃")
    print(f"         (온도 강하: {Tg_in - Tg_out:.2f} ℃)")
    print(f"[Step 2] 대수 평균 온도차 (LMTD)    : {LMTD:.2f} ℃")
    print(f"         (dT1: {dT1:.2f}, dT2: {dT2:.2f})")
    print(f"[Step 3] 필요 전열 면적 (Area)      : {Area_required:.4f} m²")
    print(f"[Step 4] 튜브 1개당 면적            : {Area_per_tube:.6f} m²")
    print(f"         필요 튜브 개수 (계산값)    : {N_tubes:.2f} 개")
    print(f"         ==> 최종 선정 튜브 개수    : {N_tubes_final} 개")
    print(f"-" * 40)
    
    # 쉘 직경 대략적 추정 (참고용, Pitch 1.25배 가정 시)
    # 대략적으로 N개 튜브가 원형으로 묶였을 때의 직경
    # D_bundle approx = D_tube * (N)^0.5 * 1.3 (여유율)
    est_shell_dia = D_tube_mm * math.sqrt(N_tubes_final) * 1.3
    print(f"[참고] 예상 Shell 직경 (약): {est_shell_dia:.1f} mm")

if __name__ == "__main__":
    calculate_heat_exchanger()