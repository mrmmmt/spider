import requests
from bs4 import BeautifulSoup
import re
import os


def request_one_page(page, location, grade):
    """
    location: 地区编码，6位数字
    page: 页码 1/2/3/4...
    grade: 医院等级编码
           2  三级甲等
           3  三级乙等
           4  三级丙等
           12 三级医院
           5  二级甲等
           6  二级乙等
           7  二级丙等
           13 二级医院
    """

    url = 'https://y.dxy.cn/hospital/?&page={0}&location={1}&grade={2}'.format(page, location, grade)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise UserWarning('status_code: {}'.format(r.status_code))

    return r.content.decode('utf-8')


def get_info_from_html(html, grade):
    """
    error_code: 0 正确
    error_code: 1 无信息
    error_code: 2 div main-listsbox 大于1个
    error_code: 3 headers 不正确
    """

    grade_dict = {
        '2' :  '三级甲等',
        '3' :  '三级乙等',
        '4' :  '三级丙等',
        '12': '三级医院',
        '5' :  '二级甲等',
        '6' :  '二级乙等',
        '7' :  '二级丙等',
        '13': '二级医院',
    }

    headers_check = ['医院名称', '地区', '性质', '类别', '等级', '规模', '创办时间']
    soup = BeautifulSoup(html, 'lxml')
    soup = soup.find_all('div', {'class': 'main-listsbox'})
    if len(soup) == 0:
        return None, 1
    if len(soup) > 1:
        return None, 2

    soup = soup[0]
    div_header = soup.find_all('div', {'class': 'tr j-fixed-head'})[0]
    headers = re.findall('<div class="th">(.+?)</div>', str(div_header))
    if headers != headers_check:
        return None, 3

    div_tbody = soup.find_all('div', {'class': 'tbody', 'id': 'hospitallist'})[0]
    div_tr_lst = div_tbody.find_all('div', {'class': 'tr'})
    res = ''
    for i in range(len(div_tr_lst)):
        div_td_list = div_tr_lst[i].find_all('div', {'class': 'td'})
        try:
            div_name_info = div_td_list[0].find_all('a')[0]
            hospital_name = div_name_info.text
            href = div_name_info.get('href')
        except:
            hospital_name = div_td_list[0].find_all('div', {'class': 'hospital-title'})[0].text.strip('"').strip()
            href = '-'
        hospital_info = [grade_dict[grade], hospital_name]
        print(i, hospital_name)
        for j in range(1, 7):
            hospital_info.append(div_td_list[j].text)
        hospital_info.append(href+'\n')
        res += '|'.join(hospital_info)

    return res, 0


def record_data(page, location, grade):
    page = str(page)
    location = str(location)
    grade = str(grade)
    error_code = None

    if not os.path.exists('./dxy_spider/error_log.txt'):
        with open('./dxy_spider/error_log.txt', 'w', encoding='utf-8') as f:
            f.write('|'.join(['location', 'grade', 'page', 'error_info\n']))

    if not os.path.exists('./dxy_spider/result.txt'):
        with open('./dxy_spider/result.txt', 'w', encoding='utf-8') as f:
            f.write('|'.join(['医院等级', '医院名称', '地区', '性质', '类别', '等级', '规模', '创办时间', 'href\n']))

    try:
        html = request_one_page(page, location, grade)
    except Exception as e:
        with open('./dxy_spider/error_log.txt', 'a', encoding='utf-8') as f:
            f.write('|'.join([location, grade, page, '数据抓取错误：'+str(e).strip().replace('\n', ' ')+'\n']))
    
    try:
        info, error_code = get_info_from_html(html, grade)
    except Exception as e:
        with open('./dxy_spider/error_log.txt', 'a', encoding='utf-8') as f:
            f.write('|'.join([location, grade, page, '数据写入错误：'+str(e).strip().replace('\n', ' ')+'\n']))

    if error_code == 0:
        with open('./dxy_spider/result.txt', 'r', encoding='utf-8') as f:
            already_lst = f.readlines()
        if info not in already_lst:
            with open('./dxy_spider/result.txt', 'a', encoding='utf-8') as f:
                f.write(info)
    else:
        with open('./dxy_spider/error_log.txt', 'a', encoding='utf-8') as f:
            f.write('|'.join([location, grade, page, '数据写入错误：'+str(error_code)+'\n']))
        if error_code == 1:
            return 1



def main(location):
    for grade in [2, 3, 4, 5, 6, 7, 12, 13]:
        for page in range(1, 100):
            print('\n\nlocation: {0}; grade: {1}; page: {2}'.format(location, grade, page))
            res = record_data(page, location, grade)
            if res == 1:
                break
    

if __name__ == '__main__':
    for location in ['410000', '420000', '430000', '440000', '450000', '460000', '500000', '510000', '520000', '530000', '540000', '610000', '620000', '630000', '640000', '650000']:        
        main(location)
