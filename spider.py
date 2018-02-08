# coding: utf-8
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from PIL import Image
from io import BytesIO
import re

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': '211.70.149.135:88',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
}


def print_table(bs_obj):
    tbody = bs_obj.find('table', {'class': 'blacktab'})
    trs = tbody.select('tr')
    table = []
    for index in range(len(trs)):
        if index % 2 is not 1:
            tds = trs[index].select('td')
            row = [re.search('(?<=>).+?(?=<)', str(td)).group(0) for td in tds]
            table.append(row)
    for row in table:
        if row[0] == '上午' or row[0] == '下午' or row[0] == '晚上':
            row.remove(row[0])
    table.pop()

    pretty_table = PrettyTable()
    pretty_table.field_names = table[0]
    for index in range(1, len(table)):
        pretty_table.add_row(table[index])
    print(pretty_table)


def parse_table(table_url, session):
    response = session.get(table_url)
    bs_obj = BeautifulSoup(response.text, 'lxml')
    viewstate = bs_obj.find('input', {'name': '__VIEWSTATE'})['value']
    table = bs_obj.find('span', {'class': 'formbox'})

    tr = table.find('table', {'class': 'formlist noprint'}).find('tr')
    xn_options = tr.find('select').find_all('option')
    xn_options = [option.get_text() for option in xn_options]
    xq_options = ['1', '2']

    tr = table.find('table', {'class': 'formlist noprint'}).find('tr', {'class': 'trbg1'})
    infos = tr.find_all('span')
    infos = [info.get_text() for info in infos]
    print('---------------------------------------------------------------------------')
    for info in infos:
        print(info, end='  ')
    print('\n---------------------------------------------------------------------------')

    # while True:
    #     xn = input('请输入学年: '+str(xn_options)+' ')
    #     xq = input('请输入学期: '+str(xq_options)+' ')
    #     if xn in xn_options and xq in xq_options:
    #         break
    #     else:
    #         print('请输入选项内的信息')
    # post_data = {'__EVENTTARGET': 'xqd', '__EVENTARGUMENT': '', '__VIEWSTATE': viewstate,
    #              'xnd': '2017-2018', 'xqd': '1'}
    # table_page = session.post(table_url, post_data).text
    # bs_obj = BeautifulSoup(table_page, 'lxml')

    print_table(bs_obj)


def spider(response, session):
    url = response.url
    print('-------------------')
    base_url = url[:25]
    bs_obj = BeautifulSoup(response.text, 'lxml')

    xhxm_string = bs_obj.find('div', {'class': 'info'}).find('span', id='xhxm').get_text()
    usernumber = xhxm_string[:9]
    name = xhxm_string.split(' ')[-1:][0]
    print('你好！' + name)
    print('你的学号：' + usernumber)
    # name = name.replace('同学', '')
    print('-------------------')

    table_headers = HEADERS
    table_headers['Referer'] = url
    session.headers.update(table_headers)
    table_url = bs_obj.find('ul', {'class': 'nav'}).find('a', {'onclick': "GetMc('学生个人课表');"})
    table_url = base_url + table_url['href']
    parse_table(table_url, session)


def get_code(session):
    response = session.get('http://211.70.149.135:88/CheckCode.aspx')
    pic = BytesIO(response.content)
    pic = Image.open(pic)
    pic.show()
    code = input('验证码:')
    return code


def login(url, session):
    while True:
        username = input('请输入学号:')
        password = input('请输入密码:')
        html = session.get(url).text
        bs_obj = BeautifulSoup(html, 'html.parser')
        viewstate = bs_obj.find('input', {'name': '__VIEWSTATE'})['value']
        code = get_code(session)
        post_data = {'__VIEWSTATE': viewstate, 'TextBox1': username,
                     'TextBox2': password, 'TextBox3': code, 'RadioButtonList1': '',
                     'Button1': '', 'lbLanguage': ''}
        response = session.post(url, post_data)
        response.encoding = response.apparent_encoding
        bs_obj = BeautifulSoup(response.text, 'lxml')
        title = bs_obj.find('title').get_text()
        if '请' not in list(title):
            return response
        else:
            print('输入信息错误，请重试')
            continue


def main():
    session = requests.session()
    session.headers.update(HEADERS)
    try:
        response = login('http://211.70.149.135:88/default2.aspx', session)
        spider(response, session)
    except Exception as er:
        print('网络连接错误!\ninfomation:', end='')
        print(er)
    session.close()


if __name__ == '__main__':
    main()

