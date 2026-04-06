import math

def calculate_dh(shape, **kwargs):
    """
    마이크로채널 포트 형상별 수력직경 계산
    """
    if shape == "circle":
        d = kwargs.get('d')
        return d
    
    elif shape == "rectangle":
        w = kwargs.get('w')
        h = kwargs.get('h')
        return (2 * w * h) / (w + h)
    
    elif shape == "triangle":
        s = kwargs.get('s') # 한 변의 길이
        return (math.sqrt(3) / 6) * s * 2 # 4A/P 간소화
    
    else:
        return None

# 예시: 폭 1.0mm, 높이 0.5mm 직사각형 포트
dh_rect = calculate_dh("rectangle", w=1.0, h=0.5)
print(f"직사각형 포트 Dh: {dh_rect:.4f} mm")