## Condenser Heat Rejection Calculation Code
# 이 프로그램은 주어진 코어 형상 및 작동 조건에 대해 튜브 및 핀 응축기의 
# 정상 상태 방열량을 결정합니다.
import matplotlib.pyplot as plt
import numpy as np
import math
from decimal import Decimal, getcontext
import decimal
getcontext().prec = 2

## STEP 1. HEX 치수 정보 입력 및 확인(필요에 따라 수정 입력)
PI = 3.14
# Rho = 0.0752        # Dry Air Density (lbm/ft3)

# 외형치수
Lcond = 26.4        # Condenser Core Length (inch)
Hcond = 17.75       # Condenser Core Height (inch)
Tcond = 1.73        # Condenser Core Depth (inch)

# TUBE 치수
OD_tube = 0.375         # Tube 외경 (3/8 inch)
OD = OD_tube + 0.016    # Tube 외경 + Tube 팽창 허용치(OD 3/8" = 0.016 inch)
Do = OD                 # Tube 실제 외경 (OD_tube + 핀 두계 * 2)
t_tube = 0.020          # Tube 벽 두께(inch)  was 0.035 inch
ID = OD_tube - 2 * t_tube
S1 = 1.0                # Tube Spacing-Vertical (inch)      # 변경검토(L1)
S2 = 0.866              # Tube Spacing-Horizontal (inch)    # 변경검토(L2)
Ntube = 35              # Total No. of Tubes (ea)   # Was N1
K_alu = 112.0          # Aluminum (Btu/(hr-ft-F)), Copper = 209

# FIN 치수
t_fin = 0.008           # Fin Thickness (inch) 
FPI = 12.0              # Fin Density(FPI)
eff_fin = 0.99          # Fin 효율

## STEP 2. 응축기 작동조건 입력 및 확인 (필요에 따라 수정 입력)
T1 = 110                # Condenser Inlet Air Temperature or Ambient Temperature (F) 
T2 = 122                # Condenser Outlet Air Temperature (F)
Tr = 145                # Cindenser Refrigerant Condensing Temperature (F)
Vair = 465              # Condenser Inlet Air Velocity (ft/min) 
D = 0.344               # Constant
N7 = 0.60               # Constant

## Step 3. Core 기본 면적 계산
# 기본 표면적 (Ap) 계산. Ap = Tube 외부 표면적(Do=OD+2*t_f) - Fin의해 가려진 Tube 외부 표면적
Ap = (PI * Do / 144) * ((1 - FPI * t_fin) * (Lcond * Ntube))    # Core 1차 표면적 (ft^2)

# 2차 표면적 (Af) 계산
Af = (FPI/6) * (S1*S2 - PI/4*Do**2) * (Lcond/12 * Ntube)        # Core 2차 표면적

# 총 외부 열전달 면적 (Ao) 계산
Ao = Ap + Af

print("DO = %.3f" % Do)
print("1차 표면적(Ap) = %.2f" % Ap)
print("2차 표면적(Af) = %.2f" % Af)
print("총 외부 열전달 면적(Ao) = %.2f" % Ao)
print("-----------------------")

## Step 4. 응축기 전체 내측 표면적(Ai) 계산
Ai = PI * ID * (Lcond/144 * Ntube)                  #(sq ft)
print("ID = %.3f" % ID)
print("Tube 내측 표면적(Ai) = %.2f" % Ai)
print("-----------------------")

## Step 5. 공기측 열전달 계수(ho) 계산
# [Table-1] 공기 측 필름 계수 ho를 계산하는 데 사용되는 경험적 상수에서 c, n 값을 수동으로 구한다.
c = 0.344
n = 0.600
ho = c*(Vair)**n                                    #(Btu/(hr-ft2-F)
print("c = %.3f" % c)
print("n = %.3f" % n)
print("공기측 열전달 계수(ho) = %.2f" % ho)
print("-----------------------")

## Step 6. 응축기 코어의 핀 효율성
# Gardner's Graph V-19 참조
m = math.sqrt(2 * ho / (K_alu * t_fin / 12))
ro = math.sqrt((S1*S2)/PI)
ri = Do
print("m = %.3f" % m)
print("ro = %.3f" % ro)
print("ri = %.3f" % ri)
print("-----------------------")

V19_x = m * (ro - ri)/12
V19_y = ro / ri
print("V19_x = %.3f" % V19_x)
print("V19_y = %.3f" % V19_y)
# eff_fin = 0.99를 그래프에서 얻음
print("Fin Effectiveness = %.2f" % eff_fin)
print("-----------------------")

## Step 7. 냉매측 열전달 계수
print("# Step 7. hr 계산 결과")
# 초기 가정 온도차 dt12 = 10 (F)
for dT12 in range(10, 100, 1): 
    # Table 2 참조
    J = 6.7326387865856E-10*Tr**4 - 0.0000003175237522791*Tr**3 + 0.0000546211008365181*Tr**2 - 0.00394117659639464 *Tr + 0.18747867621002
    psi = PI - (0.47 * J * (Lcond/12 * dT12**(3/4)) / (ID)**2.75)**0.142    # radian
    psid = psi * (180 / PI)                # deg
    
    # Beta 계산
    # Beta = -0.00000623688464526542*psid2 + 0.00020724360581448400*psid + 0.89894916661642000000
    Beta = -0.0000062*psid**2 + 0.0002*psid + 0.898949 
    # Omega = -1.3*Tr + 533.72
    Omega = -0.0016*Tr**2 -0.9166*Tr + 512.3
    
    # hr 계산
    hr = (psi/PI)*(Beta*Omega)/(((ID/12)*dT12)**(1/4))    # Btu/(hr-ft2-F)  
    EQ_L = (hr * dT12) / (ho * (Ao / Ai)) + dT12
    EQ_R = Tr - T1
    Diff_EQ = EQ_L - EQ_R
    if abs(Diff_EQ) <= 1:
        print("EQ_L 과 EQ_R이 거의 유사합니다.")
        print("J = %.4f" % J)
        print("Ψ(degree) = %.1f" % psid)
        print("β = %.4f" % Beta)
        print("Ω = %.1f" % Omega)
        print("hr = %.1f" % hr)
        print("EQ_L = %.1f" % EQ_L)
        print("EQ_R = %.1f" % EQ_R)
        print("EQ_L - EQ_R = %.1f" % Diff_EQ)
        print("dT12 = %.1f" % dT12)
        T2cal = T1 + dT12
        print("T2cal = %.1f" % T2cal)
        print('-----------------------')
        break
   
from numpy import log as ln
## Step 8. Uo 계산
Uo = 1/((1/ho)+(Ao/Ai/hr)+(1-eff_fin)/(ho*(Ap / Af + eff_fin)))
print("-- STEP 8 결과 --")
print("Uo = %.2f" % Uo)

## Step 9. LMTD 계산
LMTD = (T2-T1) / ln((Tr-T1)/(Tr-T2))
# LMTD2 = (T2-T1) / math.log((Tr-T1)/(Tr-T2))
print("-- STEP 9 결과 --")
print("LMTD = %.1f" % LMTD)
# print("LMTD2 = %.1f" % LMTD2)


## Step 10 응축기 열방출량 계산 . Qc and Qc/ft2 계산

# 실수 곱셈은 소숫점 이하의 많은 자리수가 곱셈이 되는 오류가 있어 개선함. 
Ao = str(round(Ao,1))
Ao = float(Ao)
Uo = str(round(Uo,1))
Uo = float(Uo)
LMTD = str(round(LMTD,1))
LMTD = float(LMTD)
 
Qc = Ao * Uo * LMTD
Qc_Area = Qc / ((Hcond * Lcond) / 144)
print("-- STEP 10 결과 --")
print("Qc = %d" % Qc)
print("Qc_Area = %d" % Qc_Area)
print("---------------------")

## Step 9B. Core Effectiveness(Eff_core) 계산
Pair = 2116.8           # 1 atm = 14.7 psi = 2116.8 lbm/ft2
Rair = 53.3523              # 공기 기체상수 (lbm/ft3-R) Rair=101325 Pa
Rho_air = Pair / (Rair * (T1 + 459.67))
Cm = 14.4 * Rho_air * Vair * (Hcond * Lcond / 144)
Cm = str(round(Cm,1))
Cm = float(Cm)
Eff_core = 1 - math.exp(-(Uo * Ao) / Cm)

print("-- STEP 9B 결과 --")
print("Air Density(Rho) = %.3f" % Rho_air)
print("Cm = %.2f" % Cm)
print("Core Effectiveness(Eff_core) = %.3f" % Eff_core)

## Step 10B. Qc and Qc/ft2 계산
Eff_core = str(round(Eff_core,1))
Eff_core = float(Eff_core)
Qcond = Eff_core * Cm * (Tr - T1)       # Btu/hr
Qcond = str(round(Qcond,1))
Qcond = float(Qcond)

## Step 11. 출구 공기온도(T2) 계산
T2 = T1 + (Qcond / Cm)

print("-- STEP 10B & 11 결과 --")
print("Qcond = %d" % Qcond)
print("Air Outlet Temp (T2) = %d" % T2)
print("----- End of Codes ---------")

