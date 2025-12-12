def calculate_radiator_design():
    # ==========================================
    # 1. 기초 설계 입력자료 정의
    # ==========================================
    print("--- [Step 1] 기초 설계 입력자료 정리 ---")
    
    # 라디에이터 치수 (인치)
    width_in = 28.0
    height_in = 20.0
    
    # 열적 요구사항
    Q_req_total = 6300.0  # BTU/min
    T_coolant_max_f = 240.0  # °F
    T_air_ambient_f = 100.0  # °F
    
    # 공기 유량
    airflow_scfm = 3100.0  # SCFM
    
    # 오염 계수 (Fouling Factor)
    fouling_percent = 2.0  # 2%
    
    # 전면 면적 계산 (Square Feet)
    # 144 = 12 * 12 (인치를 피트로 변환)
    face_area_ft2 = (width_in * height_in) / 144.0
    
    # 입구 온도차 (ITD: Inlet Temperature Difference)
    dt_in = T_coolant_max_f - T_air_ambient_f
    
    print(f"라디에이터 크기: {width_in}\" x {height_in}\"")
    print(f"전면 면적 (Face Area): {face_area_ft2:.2f} ft²")
    print(f"입구 온도차 (ITD): {dt_in:.1f} °F")
    print("-" * 40)


    # ==========================================
    # 2. 요구 방열량 규정화 (Normalization)
    #    BTU/min -> BTU/min/ft²/°F
    # ==========================================
    print("\n--- [Step 2] 요구 방열량 규정화 ---")
    
    # 기본 단위 면적당/온도차당 방열량
    q_specific_raw = Q_req_total / (face_area_ft2 * dt_in)
    
    # 오염(Fouling) 고려 (2% 여유)
    # 요구되는 규정화 방열량 (Q_nor_req)
    q_nor_req = q_specific_raw * (1 + fouling_percent / 100.0)
    
    print(f"기본 규정화 방열량: {q_specific_raw:.2f} BTU/min·ft²·°F")
    print(f"오염 고려({fouling_percent}%) 최종 요구 방열량 (Q_nor_req): {q_nor_req:.2f} BTU/min·ft²·°F")
    print("-" * 40)


    # ==========================================
    # 3. 공기 유속 계산 및 적합성 판단
    # ==========================================
    print("\n--- [Step 3] 공기 유속 계산 및 설계 판단 ---")
    
    # 공기 유속 (Face Velocity) 계산
    # Velocity (ft/min) = Volume Flow (ft³/min) / Area (ft²)
    velocity_fpm = airflow_scfm / face_area_ft2
    
    print(f"공기 유속 (Air Velocity): {velocity_fpm:.1f} ft/min")
    
    # ---------------------------------------------------------
    # 성능 곡선 및 압력 손실 데이터 비교 (시뮬레이션)
    # 실제로는 제조사의 그래프에서 유속(797)일 때의 값을 읽어야 함
    # ---------------------------------------------------------
    
    # 문제에서 주어진 19 FPI 사양의 성능 데이터 (가정된 Lookup 값)
    radiator_perf_capacity_19fpi = 12.0  # BTU/min·ft²·°F at 797 fpm
    pressure_drop_19fpi = 0.6            # inAq at 797 fpm
    
    print(f"\n[설계 검토 결과]")
    print(f"계산된 요구 성능 (Required): {q_nor_req:.1f}")
    print(f"19 FPI 사양 성능 (Capacity): {radiator_perf_capacity_19fpi:.1f}")
    
    if radiator_perf_capacity_19fpi >= q_nor_req:
        print(">> 판정: 적합 (Capacity >= Required)")
        print(f">> 공기 측 압력 강하: {pressure_drop_19fpi} inAq")
    else:
        print(">> 판정: 부적합 (성능 부족)")

# 함수 실행
if __name__ == "__main__":
    calculate_radiator_design()