# -*- encoding: utf-8 -*-
'''
@File    :   spider.py
@Time    :   2024/01/08 20:43:16
@Author  :   rainday 
@Version :   1.0
@Description : 抓取boss直聘上工作信息
'''
import time
import sys
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main(jobs_info):
    # edge driver file
    driverfile_path = r'C:\Program Files\edgedriver_win64\msedgedriver.exe'
    driver = webdriver.Edge(executable_path=driverfile_path)

    # url informations
    city = '101220100'
    # job = '计算机视觉'
    job = '图像算法工程师'
    page = 10  # 1~10

    def get_jobs(url, jobs_info):
        # get page
        driver.get(url)
        # wait until 'job-card-body' appear
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job-card-body')))

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        jobs = soup.find_all('div', class_='job-card-body')

        

        for job in jobs:
            # 获取公司名称，薪资、人数、融资上市情况、公司属性（硬件or软件or金融...）、公司福利
            company_name = job.find(class_='company-name').text.strip()
            base_info = [info.text for info in job.find(class_='company-tag-list').find_all('li')]
            money = job.find(class_='salary').text.strip()  # xx-xxK.15薪
            # 将money转为年薪，没有后面的xx薪，按照12算
            try:
                # 找到K，没有找到就过滤到该岗位，一般没有K都是实习
                idx2 = money.index('K')
            except ValueError:
                continue
            idx1 = money.index('-')
            floor, upper = int(money[:idx1]), int(money[idx1+1:idx2])
            # 最低薪资小于12K直接pass
            if floor < 12:
                continue
            # 发多少月
            try:
                idx3 = money.index('.')
                # 找到了将其设为xxx
                count = money[idx3:-1]
            except ValueError:
                # 没找到则将应发薪资月数设为12
                count = 12

            money = [floor, upper, count, (floor+upper)/2*count/10]  # 最低月薪，最高月薪，应发月数，年薪W

            # a:进入该链接有具体的岗位职责、工作地点、成立日期
            sub_url = job.find('a', class_='job-card-left').get('href')
            sub_url = 'https://www.zhipin.com' + sub_url

            #time.sleep(1)  # 等待0.5s
            driver.get(sub_url)
            wait = WebDriverWait(driver, sys.maxsize)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'location-address')))

            page_source = driver.page_source
            # driver.close()
            soup = BeautifulSoup(page_source, 'html.parser')

            location = soup.find('div', class_='location-address').text.strip()
            try:
                cre_date = soup.find('li', class_='res-time').text.strip()[4:]  # 成立日期
            except:
                cre_date = '未知'
            job_require = soup.find('div', class_='job-sec-text').get_text(separator='\n')  # 岗位要求,保留换行

            # 储存该岗位信息
            if company_name not in jobs_info:
                jobs_info[company_name] = {
                    '基本信息':base_info,
                    '薪资待遇':money,
                    '最低月薪':money[0],
                    '年薪':money[-1],
                    '工作地点':location,
                    '成立日期':cre_date,
                    '岗位职责':job_require,
                    '投递链接':sub_url,
                }

    for i in range(1, page+1):
        url = f'https://www.zhipin.com/web/geek/job?query={job}&city={city}&page={i}'
        get_jobs(url, jobs_info)

    # close browser
    driver.quit()

    # save json file
    with open('test.json', 'w', encoding='utf-8') as f:
        json.dump(jobs_info, f, ensure_ascii=False)

def save_jobs_info_csv(file):
    # 将加载的jobs_info保存成csv
    with open(file, 'r', encoding='utf-8') as f:
        jobs_info = json.load(f)
    
    df = pd.DataFrame(columns=['公司名称', '基本信息', '薪资待遇', '最低月薪', '年薪', '工作地点', '成立日期', '岗位职责', '投递链接'])
    news_rows_data = []
    for key, val in jobs_info.items():
        temp = {}
        temp['公司名称'] = key
        temp.update(val)
        news_rows_data.append(temp)
    df = df._append(news_rows_data, ignore_index=True)
    print(df.shape)

    df.to_csv('test.csv', index=False)

if __name__ == "__main__":

    # jobs_info = {}
    # with open('合肥计算机视觉岗.json', 'r', encoding='utf-8') as f:
    #     jobs_info = json.load(f)

    # main(jobs_info)

    save_jobs_info_csv('test.json')
    







    



