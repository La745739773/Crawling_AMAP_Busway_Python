import math
import os





def gcj2_wgs84(lon,lat):
    a = 6378245.0 # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323 #克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324 # 圆周率

    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLon += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    #纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLat += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI);
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    #print(str(wgsLon) + ' ' + str(wgsLat))
    return wgsLon,wgsLat

def gcj2_wgs84_func(input_file,output_file):
    with open(input_file,'r',encoding='utf-8') as file:
        out_file = open(output_file,'a+',encoding='utf-8')
        while 1:
            aryline = file.readline()
            if not aryline:
                break
            str_array = aryline.split('\"')
            out_file.write(str_array[0])
            out_file.write('\"')
            coord_array = str_array[1].split(';')
            change_coord = ''
            for coords in coord_array:
                lon = float(coords.split(',')[0])
                lng = float(coords.split(',')[1])
                wgsLon,wgslat = gcj2_wgs84(lon,lng)
                #print(str(wgsLon) + str(wgslat))
                change_coord = change_coord + str(wgsLon) + ',' + str(wgslat) + ';'
                #out_file.write(str(wgsLon) + ',' + str(wgslat) + ';')
            change_coord = change_coord[:-1]
            out_file.write(change_coord)
            out_file.write('\"' + '\n')
            

if __name__ == '__main__':
    input_file = os.path.abspath(os.path.dirname(os.getcwd())) + '\\Output\\' + input('输入文件名:')
    ori_coords = input('原始坐标系：0:gjc02  1:wgs84  2:bd09\n')
    dest_coords = input('转换坐标系：0:gjc02  1:wgs84  2:bd09\n')
    output_file = input('输出文件名:')
    if ori_coords == '0' and dest_coords == '1':
        gcj2_wgs84_func(input_file,output_file)