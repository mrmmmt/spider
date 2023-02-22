"""
丁香园网站查询医院信息
"""
from numpy import save
import requests
from urllib import parse
import json
import os
import pandas as pd
import re


def query_url_id(hospital_name):
    """得到医院id"""
    url = 'https://search.dxy.cn/cardSearch?query='+parse.quote(hospital_name)
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://search.dxy.cn/?words='+parse.quote(hospital_name),
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise UserWarning('status_code: {}'.format(r.status_code))
    s = json.loads(r.text)
    s = s['result']['hospital']
    if len(s) == 0:
        return None
    return s['entity_url'].split('/')[-1]


def get_hospital_info(hospital_name, id=None):
    if id is None:
        id = query_url_id(hospital_name)
        if id is None:
            return None
    id = re.findall(r'\d+', str(id))
    if len(id) == 0:
        return None

    id = id [0]

    url = 'https://y.dxy.cn/papi/hospital/detailInfo?hospital_id='+id
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://y.dxy.cn/hospital/{}/detail'.format(id),
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise UserWarning('status_code: {}'.format(r.status_code))
    s = json.loads(r.text)
    s = s['results']
    grade = str(s['grade'])
    begin_year = str(s['begin_year'])
    bed_num = s['bed_num']  # 核定床位数
    if bed_num == -1: bed_num = '-'
    employer_num = s['employer_num']  # 在职职工数
    if employer_num == -1: employer_num = '-'
    year_hospital_num = s['year_hospital_num']  # 年住院人次
    if year_hospital_num == -1: year_hospital_num = '-'
    year_outpatient = s['year_outpatient']  # 年门急诊量
    if year_outpatient == -1: year_outpatient = '-'

    trade = str(s['trade'] )  # 机构性质
    if trade == '0':
        trade = '未知'
    elif trade == '1':
        trade = '公立医院'
    elif trade == '2':
        trade = '民营医院'
    elif trade == '3':
        trade = '公私合营'
    else:
        trade = '-'
    
    scale = str(s['scale'])  # 机构规模
    if scale == '0':
        scale = '未知'
    elif scale == '1':
        scale = '20 人以下'
    elif scale == '2':
        scale = '20-99 人'
    elif scale == '3':
        scale = '100-399 人'
    elif scale == '4':
        scale = '500-999 人'
    elif scale == '5':
        scale = '1000 人以上'

    attribution = str(s['attribution'])  # 机构类别
    if attribution == '0':
        attribution = '未知'
    elif attribution == '1':
        attribution = '综合医院'
    elif attribution == '2':
        attribution = '专科医院'
    elif attribution == '3':
        attribution = '卫生站（含卫生服务中心）'
    elif attribution == '4':
        attribution = '卫生院（含卫生所、卫生室）'
    elif attribution == '5':
        attribution = '诊所（含门诊部）'
    elif attribution == '6':
        attribution = '公共卫生'
    elif attribution == '7':
        attribution = '其他'

    if len(begin_year) != 4:
        begin_year = '-'
    else:
        begin_year += '年'

    if grade == '0':
        level ='未知'
        grade = '未知'
    elif grade == '1':
        level = '三级'
        grade = '特等'
    elif grade == '2':
        level = '三级'
        grade = '甲等'
    elif grade == '3':
        level = '三级'
        grade = '乙等'
    elif grade == '4':
        level = '三级'
        grade = '丙等'
    elif grade == '5':
        level = '二级'
        grade = '甲等'
    elif grade == '6':
        level = '二级'
        grade = '乙等'
    elif grade == '7':
        level = '二级'
        grade = '丙等'
    elif grade == '8':
        level = '一级'
        grade = '甲等'
    elif grade == '9':
        level = '一级'
        grade = '乙等'
    elif grade == '10':
        level = '一级'
        grade = '丙等'
    elif grade == '12':
        level = '三级'
        grade = '未定等'
    elif grade == '13':
        level = '二级'
        grade = '未定等'
    elif grade == '14':
        level = '一级'
        grade = '未定等'
    elif grade == '15':
        level = '未定级'
        grade = '未定等'
    else:
        grade, level = '-', '-'

    res = {
        'key': hospital_name,
        '机构全称': s['full_name'],
        '机构简介': s['info'].strip().replace('\n', ''),
        '创办年份': begin_year,
        '医院级别': level,
        '医院等次': grade,
        '省': s['province'],
        '市': s['city'],
        '区': s['area'],
        '核定床位数': bed_num,
        '在职职工数': employer_num,
        '年住院人次': year_hospital_num,
        '年门急诊量': year_outpatient,
        '机构性质': trade,
        '机构规模': scale,
        '机构类别': attribution
    }

    return res


if __name__ == '__main__':
    df = pd.read_excel('./dxy_spider/丁香园医院数据.xlsx')
    save_name = './dxy_spider/dxy_info.json'
    if not os.path.exists(save_name):
        with open(save_name, 'w', encoding='utf-8') as f:
            json.dump({'res': [], 'success': [], 'noInfo': []}, f)
    
    flag = 0
    for i in df.index:
        hospital_name = df['医院名称'][i]
        href = df['href'][i]
        if href == '-':
            continue
        if not flag:
            with open(save_name, 'r', encoding='utf-8') as f:
                info_dict = json.load(f)
        if hospital_name in info_dict['success']:
            print(i, hospital_name, 'already')
            flag = 1
            continue
        if hospital_name in info_dict['noInfo']:
            print(i, hospital_name, 'already')
            flag = 1
            continue
        flag = 0
        try:
            r = get_hospital_info(hospital_name, href)
            if r is None:
                info_dict['noInfo'].append(hospital_name)
                print(i, hospital_name, 'None')
            else:
                info_dict['success'].append(hospital_name)
                info_dict['res'].append(r)
                print(i, hospital_name, 'success')
            with open(save_name, 'w', encoding='utf-8') as f:
                json.dump(info_dict, f)
        except Exception as e:
            print(i, hospital_name, e)
