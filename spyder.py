# -*- coding: utf-8 -*-  
import requests
from bs4 import BeautifulSoup
import random
import xlrd
import json
import csv
import sys
import time
import math
sys.path.append('8684BuslineName\\')
import Crawling_Busline_Name

LINE_IDLIST = []
#https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=17&city=320100&geoobj=118.956002%7C32.109411%7C118.971452%7C32.11639&key=45f832d3c04d3a1cb1145ea48798c3e6&keywords=1%E8%B7%AF
'''
    账号一： 45f832d3c04d3a1cb1145ea48798c3e6
    账号二： d0450526d259776e0f9fb8adaddf39a9
    账号三： 7a82040e0dc3f2e70e27d66fc16a872c
'''
output_File = ''
ip_add_url = 'http://www.xicidaili.com/'
ip_Mode = '0'
Crawling_Mode = '0'  #爬取方式 从头爬取 或 补充
coords = '0'
bd_api_key = 'KtmshjiGv5nDDvYwcWbF0GIfhZf1anvE'
def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

def get_random_ip(ip_list,ip_mode):
    proxy_list = []
    for ip in ip_list:
        if ip_mode == '1':
            proxy_list.append('http://' + ip)
        elif ip_mode == '2':
            proxy_list.append('https://' + ip)
    for i in range(0,len(proxy_list)):
        if ip_mode == '1':
            prox = {'http': proxy_list[i]}
        elif ip_mode == '2':
            prox = {'https': proxy_list[i]}
        try:
            result = requests.get('http://ip.chinaz.com/getip.aspx', proxies=prox)
            return prox
        except Exception as e:
            continue
def change_random_ip(ip_Url,ip_mode):
    #url = 'http://www.xicidaili.com/nn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    ip_list = get_ip_list(ip_Url, headers=headers)
    proxies = get_random_ip(ip_list,ip_mode)
    return proxies

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
def gcj2_bd09(coord_str):
    if coord_str == '':
        return 
    coord_str = coord_str[:-1]
    url = 'http://api.map.baidu.com/geoconv/v1/?coords=' + coord_str + '&from=3&to=5&ak=' + bd_api_key
    res = requests.get(url)
    res_json = res.json()
    return res_json['result']
def Analy_json(web_data):
    #print(web_data.text)
    res_json = web_data.json()
    if res_json['status'] != '1':
        print('网页请求返回错误代码')
        return 'failure'
    try:
        for i in range(0,len(res_json['data']['busline_list'])):
            #if i >= 2:
            #    return 'success'
            busline = res_json['data']['busline_list'][i]
            global LINE_IDLIST
            id = busline['id']
            if id in LINE_IDLIST:
                continue
            print(id)
            print(busline['name'])
            with open(output_File,'a+',encoding = 'utf-8') as csvFile:
                csvFile.write(busline['name'].replace('\n','') + ',')
                csvFile.write(busline['front_name'].replace('\n','') + ',')
                csvFile.write(busline['terminal_name'].replace('\n','') + ',')
                csvFile.write(busline['company'].replace('\n','') + ',')
                csvFile.write(busline['areacode'].replace('\n','') + ',')
                csvFile.write(busline['total_price'].replace('\n','') + ',')
                csvFile.write(busline['length'].replace('\n','') + ',')
                csvFile.write(busline['start_time'].replace('\n','') + ',')
                csvFile.write(busline['end_time'].replace('\n','') + ',')
                csvFile.write('\"')
                x_array = busline['xs'].replace('\n','').split(',')
                y_array = busline['ys'].replace('\n','').split(',')
                if coords == '1':
                    for j in range(0,len(x_array)-1):
                        log,lat = gcj2_wgs84(float(x_array[j]),float(y_array[j]))
                        csvFile.write(str(log) + ',' + str(lat) + ';')
                    log,lat = gcj2_wgs84(float(x_array[len(x_array)-1]),float(y_array[len(x_array)-1]))
                    csvFile.write(str(log) + ',' + str(lat))
                    csvFile.write('\"\n')
                elif coords == '0':
                    for j in range(0,len(x_array)-1):
                        csvFile.write(x_array[j] + ',' + y_array[j] + ';')
                    csvFile.write(x_array[len(x_array)-1] + ',' + y_array[len(x_array)-1])
                    csvFile.write('\"\n')
                elif coords == '2':
                    coord_str = ''
                    if len(x_array) % 90 == 0:
                        loop_time = int(len(x_array) / 90)
                    else:
                        loop_time = int(len(x_array) / 90) + 1
                    for j in range(0,loop_time):
                        coord_str = ''
                        for t in range(0,90):
                            index = j * 90 + t
                            if index < len(x_array):
                                coord_str += x_array[index] + ',' + y_array[index] + ';'
                        bd_Coord_json = gcj2_bd09(coord_str)
                        if j == (loop_time-1):
                            write_str = ''
                            for obj in bd_Coord_json:
                                write_str += str(obj['x']) + ',' + str(obj['y']) + ';'
                            write_str = write_str[:-1]
                            write_str += '\"\n'
                            csvFile.write(write_str)
                        else:
                            write_str = ''
                            for obj in bd_Coord_json:
                                write_str += str(obj['x']) + ',' + str(obj['y']) + ';'
                            csvFile.write(write_str)                        
        return 'success'
    except Exception as error:
        return 'UnFind'
def Set_Cookies():
    cook = 'guid=7606-554f-f717-c530; cna=BRjeEh+kRl0CAdOiUVBWHlUb; UM_distinctid=1627192d45230b-0d9b8c26b60724-3a614f0b-1fa400-1627192d45370d; _uab_collina=152232387196923751477499; Kdw4_5279_saltkey=IrjnwunZ; Kdw4_5279_lastvisit=1522813903; _ga=GA1.2.1998443450.1522844905; key=bfe31f4e0fb231d29e1d3ce951e2c780; _umdata=E2AE90FA4E0E42DE21AA530344996A7CC8E2B5D20F85EFCC9AC339B93CA82E9F31A5FFDE890EA6A6CD43AD3E795C914C218292EA82F9AAEBAC9E39100DE27572; passport_login=MTc4ODI5MzIxLGFtYXBfMTc3NTE3OTAyMDNCdE1tWENuT1EseTF3cXQ4cmN0YjBkcXd3bWlpN3EyaWR0dDFwOGRxNW0sMTUyMzE5MTQ1NyxOMlUzWTJRd056WTRObVV6T0RGbE9UVTFOakUzWmpNelpHTTRNVFJqTXpjPQ%3D%3D; CNZZDATA1255626299=2111130160-1522323229-https%253A%252F%252Fwww.baidu.com%252F%7C1523187728; isg=BLa23Qkx8MtyLYTZgZFL4QLWB-x4f_t28WRsjiCfohk0Y1b9iGdKIRwRfz8PUPIp'
    cookies={}#初始化cookies字典变量  
    for line in cook.split(';'):   #按照字符：进行划分读取  
        #其设置为1就会把字符串拆分成2份  
        name,value=line.strip().split('=',1)  
        cookies[name]=value  #为字典cookies添加内容
    return cookies 
def Crawing_Amap_busline_Agent(Amap_Busline_url,new_Pro):
    proxies = new_Pro
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 EXT/fb9181f0gqpxba1b11e7b69ae5c817801432/7.4',#random.choice(USER_AGENTS),
        'Connection': 'keep-alive',
        'accept': '*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9',
        'Referer':'https://www.amap.com/',
        'Host':'www.amap.com',
        'RA-Sid':'fb9181f0gqpxba1b11e7b69ae5c817801432',
        'RA-Ver':'7.4',
        'X-Requested-With':'XMLHttpRequest',
        'If-None-Match':'W/"27-LwlfEZRHu2oxqzu269xxfC1uJCs"W',
    }
    web_data = requests.get(Amap_Busline_url,headers = headers,cookies = Set_Cookies(),proxies=proxies)
    if Analy_json(web_data) == 'failure':
        new_Pro = change_random_ip(ip_add_url,ip_Mode)
        Crawing_Amap_busline_Agent(Amap_Busline_url,new_Pro)
def Crawing_Amap_busline(Amap_Busline_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 EXT/fb9181f0gqpxba1b11e7b69ae5c817801432/7.4',#random.choice(USER_AGENTS),
        'Connection': 'keep-alive',
        'accept': '*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9',
        'Referer':'https://www.amap.com/',
        'Host':'www.amap.com',
        'RA-Sid':'fb9181f0gqpxba1b11e7b69ae5c817801432',
        'RA-Ver':'7.4',
        'X-Requested-With':'XMLHttpRequest',
        'If-None-Match':'W/"27-LwlfEZRHu2oxqzu269xxfC1uJCs"W',
    }
    try:
        web_data = requests.get(Amap_Busline_url,headers = headers,timeout=5)
        result = Analy_json(web_data)
        return result
    except requests.exceptions.ConnectTimeout:
            Crawing_Amap_busline(Amap_Busline_url)

def get_adcode(city_name):
    Amap_adcode_city_excel = xlrd.open_workbook(r'AMap_adcode_citycode\AMap_adcode_citycode.xlsx')
    Amap_Sheet = Amap_adcode_city_excel.sheet_by_name('城市编码表')
    rows = Amap_Sheet.nrows
    for i in range(0,rows):
        if city_name == Amap_Sheet.cell_value(i,0):
            return Amap_Sheet.cell_value(i,1)
def Read_input_excel(xlsx_Address):
    ExcelFile = xlrd.open_workbook(xlsx_Address)
    sheet = ExcelFile.sheet_by_name('Busline_name')
    rows = sheet.nrows
    #pro = change_random_ip(ip_add_url,ip_Mode)
    #print(pro)
    for i in range(0,rows):
        city_name = sheet.cell_value(i,0)
        key_Words = sheet.cell_value(i,1)
        adcode = get_adcode(city_name)
        Amap_url = 'https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=17&city_limit=true&city=' + adcode + '&keywords=' + key_Words
        #print(Amap_url)
        result_str = Crawing_Amap_busline(Amap_url)
        if result_str == 'failure':
            while True:
                result_str = Crawing_Amap_busline(Amap_url)
                if result_str != 'failure':
                    break
        elif result_str == 'Unfind':
            with open('parser_error/' + city_name + 'error.csv','a+') as file:
                file.write(city_name + "," + key_Words + '\n')
        #if (i + 1) % 100 == 0:
            #time.sleep(100)
        '''
        if i % 50 == 0:
            pro = change_random_ip(ip_add_url,ip_Mode)
            print(pro)
        '''
        print('Crawing ' + str(i+1) + 'Busline' )

if __name__ == '__main__':
    '''
    ip_Mode = input('1：HTTP代理\t 2:HTTPS代理\t 3：混合高匿代理(不推荐)\n选择IP代理模式：')
    ip_add_url = 'http://www.xicidaili.com/'
    if ip_Mode == '1':
        ip_add_url = ip_add_url + 'wt/'
    elif ip_Mode == '2':
        ip_add_url = ip_add_url + 'wn/'
    else:
        ip_add_url = ip_add_url + 'nn/'
    '''

    LINE_IDLIST.clear()
    input_file_address = ''
    Crawling_Mode = input('选择模式,0:origin  1:supplement  2:return\n')
    if Crawling_Mode == '0':
        city_ch_name = input('输入城市中文名,例如:南京(不要带\'市\'):\n')
        Crawling_Busline_Name.Crawling_8684_busline_name(city_ch_name)
        input_file_address = '8684BuslineName\\'+city_ch_name+'公交地铁线路.xls'
        coords = input('输出坐标系：0:gcj02 1:wgs84 2:bd09\n')
        output_File = 'Output\\'
        output_File = output_File + input('输出文件名:  ')
        #if coords == '2':
            #bd_api_key = input('输入百度api_key:')
        Read_input_excel(input_file_address)
    elif Crawling_Mode == '1':
        input_file_address = '8684BuslineName\\input.xls'
        output_File = 'Output\\'
        coords = input('输出坐标系：0:gcj02 1:wgs84 2:bd09\n')
        output_File = output_File + input('输出文件名:  ')
        #if coords == '2':
            #bd_api_key = input('输入百度api_key:')
        Read_input_excel(input_file_address)
    elif Crawling_Mode == '2':
        city_ch_name = input('输入城市中文名,例如:南京(不要带\'市\'):\n')
        Crawling_Busline_Name.Crawling_8684_busline_name(city_ch_name)



    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    ip_list = get_ip_list(ip_add_url,headers)
    proxy_list = []
    for ip in ip_list:
        if ip_Mode == '1':
            proxy_list.append('http://' + ip)
        elif ip_Mode == '2':
            proxy_list.append('https://' + ip)
    for i in range(0,len(proxy_list)):
        if ip_Mode == '1':
            prox = {'http': proxy_list[i]}
        elif ip_Mode == '2':
            prox = {'https': proxy_list[i]}
        try:
            result = requests.get('http://ip.chinaz.com/getip.aspx', proxies=prox)
            print(prox)
        except Exception as e:
            print('failure')
            continue
    '''

# web_data = requests.get(url, headers=headers, proxies=proxies)
# 