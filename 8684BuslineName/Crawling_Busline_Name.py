import pypinyin
import requests
from bs4 import BeautifulSoup
from pypinyin import pinyin, lazy_pinyin
import xlwt

workbook = xlwt.Workbook() 
sheet = workbook.add_sheet("Busline_name")
row = 0
def Crawling_8684_busline_name(city_name):
    city_pinyin = ''.join(lazy_pinyin(city_name))
    url = 'http://' + city_pinyin + '.8684.cn'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Connection': 'keep-alive',
        'Host':'8684.cn',
        'Upgrade-Insecure-Requests':'1',
    }

    data = requests.get(url)
    soup = BeautifulSoup(data.text,'html.parser')
    
    number_div = soup.select('.bus_kt_r1')
    letter_div = soup.select('.bus_kt_r2')
    
    number_list = number_div[0].select('a')
    letter_list = letter_div[0].select('a')
    for num in number_list:
        Crawling_busline_name(url + num['href'],city_name)
    for let in letter_list:
        Crawling_busline_name(url + let['href'],city_name)

def Crawling_busline_name(url,city_name):
    global row
    try:
        data = requests.get(url,timeout = 5)
        soup = BeautifulSoup(data.text,'html.parser')
        stie_div = soup.select('.stie_list')
        stie_list = stie_div[0].select('a')
        stie_str = ''
        for stie in stie_list:
            stie_str = stie.text
            if stie.text.find('停运') != -1:
                continue
            if stie.text.find('(') != -1:
                stie_str = stie.text[0:stie.text.find('(')]
            sheet.write(row,0,city_name + '市')
            sheet.write(row,1,stie_str)
            row = row + 1
        workbook.save('8684BuslineName\\'+city_name+'公交地铁线路.xls')
    except requests.exceptions.ConnectTimeout:
        Crawling_busline_name(url,city_name)

if __name__ == '__main__':
    Crawling_8684_busline_name(u'南京')