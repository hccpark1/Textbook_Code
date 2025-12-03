# TEC Module Selection Case-3

# Data Input
Tc = 25.0           # [C]
Rhs = 6.0           # [C/W] Housing Heat Resistance
Qc = 0.5            # [W]
Tamb = 35.0         # [C] Ambient Temperature
Th_0 = 50.0         # [C] 초기 고온온도 가정 (그래프 데이터 값 채택택)
Module = "18Cyl-1.2A"

## 1. Th 추정
Vin_max = 2.4       # [V] 특성곡선에서 취득
Iin_max = 1.2       # [A] 특성곡선에서 취득
Pin_max = Vin_max * Iin_max
Trise_hs_0 = Th_0 - Tamb   # Housing 온도상승 초기 가정

Pin = Pin_max
Qh = Qc + Pin 
print(f'Pin = {Pin:.1f} Watts') 
print(f'Qh = {Qh:.1f} Watts') 

# Housing 온도 상승 계산
Trise_hs = Rhs * Qh
Th_1 = Tamb + Trise_hs
print(f'Housing 온도상승 = {Trise_hs:.1f} C') 
print(f'Th = {Th_1:.1f} C') 

## 2. Housing 최고온도와 Th 비교
Temp_diff = Th_1 - Th_0
print(f'Housing 최고온도와 Th 차이 = {Temp_diff:.1f} C') 
if abs(Temp_diff) < 6.0 :
    print("온도차이 허용 수준")
else:
    print("온도차이 과다다") 

## 3. 모듈 온도차 dT 계산
dT = Th_1-Tc
print(f'모듈온도차 = {dT:.1f} C') 
dT = round(dT/10,1)*10
print(f'모듈온도차 = {dT:.1f} C') 

## 4. Qc vs I Graph에서 DT에서의 Qmax 상당 전류와 Qmax 값 읽어 입력
Iin_max = 1.2   # INPUT [A]
Qmax = 0.9      # INPUT [W]   

## 5. DT곡선과 Qc 교차점에서의 전류(I) 확인 및 입력
Iin = 0.55      # [A]
# Vin vs I Graph에서 Iin - DT 교차점의 X축 V 값 확인 입력
Vin = 1.2       # [V]

## 5. Th 추정
Pin = Vin * Iin
Qh = Qc + Pin 
print(f'Pin = {Pin:.2f} Watts') 
print(f'Qh = {Qh:.2f} Watts') 
Trise_hs = Rhs * Qh
print(f'Housing 온도상승 = {Trise_hs:.1f} C') 
Th_1 = Tamb + Trise_hs
print(f'Th = {Th_1:.1f} C') 
Temp_diff = Th_1 - Tc
print(f'Housing 최고온도와 Th 차이 = {Temp_diff:.1f} C') 
if abs(Temp_diff) < 6.0 :
    print("온도차이 허용 수준")
else:
    print("온도차이 과다다") 