import math


a = 6378245.0  # 克拉索夫斯基椭球参数长半轴a
ee = 0.00669342162296594323  # 克拉索夫斯基椭球参数第一偏心率平方
pi = 3.14159265358979324  # 圆周率
PI = 3.14159265358979324  # 圆周率
EARTH_RADIUS = 6378173    # m


def transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * pi) + 40.0 * math.sin(y / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * pi) + 320 * math.sin(y * pi / 30.0)) * 2.0 / 3.0
    return ret
 

def transform_lon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * pi) + 40.0 * math.sin(x / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * pi) + 300.0 * math.sin(x / 30.0 * pi)) * 2.0 / 3.0
    return ret


def gcj02wgs84(x,y):
    lon = float(x)
    lat = float(y)

    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = transform_lon(x, y)
    # 纬度
    dLat = transform_lat(x, y)
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI)
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon, wgsLat


def rad(d):
    return d * pi / 180


def wgs84_distance(x1, y1, x2, y2):
    x1 = rad(x1)
    y1 = rad(y1)
    x2 = rad(x2)
    y2 = rad(y2)
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    d = math.sqrt(math.pow(math.sin(dy / 2), 2) + math.cos(y1) * math.cos(y2) * math.pow(math.sin(dx / 2), 2))
    d = EARTH_RADIUS * 2 * math.asin(d)
    return d


def test():
    print(gcj02wgs84(104.064580, 30.708090))


def test_distance():
    print(wgs84_distance(103.9, 30.55, 104.2, 30.55))
    print(wgs84_distance(103.9, 30.85, 104.2, 30.85))
    print(wgs84_distance(103.9, 30.55, 103.9, 30.85))
    print(wgs84_distance(104.2, 30.55, 104.2, 30.85))


if __name__ == "__main__":
    test_distance()