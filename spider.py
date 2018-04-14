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
    'Connection': 'keep-alive',
    'Host': '211.70.149.135:88',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
}


def print_table(bs_obj):
    '''按格式输出页面中的课表信息 参数为beautifulsoup对象'''
    tbody = bs_obj.find('table', {'class': 'blacktab'})  # 注意tbody标签在html中实际并不存在 是browser自己加的
    trs = tbody.select('tr')
    table = []  # 用于存放课表信息的二维list
    for index in range(len(trs)):
        if index % 2 is not 1:  # 隔行选择课程信息 因为每节课均为两个课时 信息均在偶数行
            tds = trs[index].select('td')  # td标签存了表格中一行的数据
            row = []  # 行
            for td in tds:  # 本行中单个数据
                infos = re.findall('(?<=>).+?(?=<)', str(td))  # 正则匹配到课程信息
                info = infos[0]  # 第一个为课程名称 或 表头文字
                if len(infos) > 3:  # 表头文字没有更多信息
                    info += '\n' + infos[1] + '\n' + infos[2] + '\n' + infos[3]  # 课程的更多信息
                row.append(info)  # 在行中加入信息
            table.append(row)  # 把行加入表格
    for row in table:
        # 清洗信息 删除多余
        if row[0] == '上午' or row[0] == '下午' or row[0] == '晚上':
            row.remove(row[0])
    table.pop()  # 清洗信息

    pretty_table = PrettyTable()  # 使用prettytable库打印表格
    pretty_table.field_names = table[0]
    for index in range(1, len(table)):
        pretty_table.add_row(table[index])
    print(pretty_table)


def parse_table(table_url, session):
    '''与用户交互 解析基本信息 并请求响应的课表页面 传入默认的table的url 和session对象'''
    response = session.get(table_url)
    bs_obj = BeautifulSoup(response.text, 'lxml')
    viewstate = bs_obj.find('input', {'name': '__VIEWSTATE'})['value']
    table = bs_obj.find('span', {'class': 'formbox'})

    # 抽取学年学期选项信息
    tr = table.find('table', {'class': 'formlist noprint'}).find('tr')
    xn_options = tr.find('select').find_all('option')
    xn_options = [option.get_text() for option in xn_options]
    xq_options = ['1', '2']
    xn_default = tr.find('select', {'name': 'xnd'}).find('option', {'selected': 'selected'}).string
    xq_default = tr.find('select', {'name': 'xqd'}).find('option', {'selected': 'selected'}).string

    # 抽取并显示学生个人信息
    tr = table.find('table', {'class': 'formlist noprint'}).find('tr', {'class': 'trbg1'})
    infos = tr.find_all('span')
    infos = [info.get_text() for info in infos]
    print('---------------------------------------------------------------------------')
    for info in infos:
        print(info, end='  ')
    print('\n---------------------------------------------------------------------------')

    # 更改学年学期菜单
    print('当前参数为：{}学年 第{}学期'.format(xn_default, xq_default))
    while True:
        xn = input('>请输入学年: ' + str(xn_options) + ' ')
        if xn not in xn_options:
            print('请输入选项内的信息\n')
            continue
        xq = input('>请输入学期: ' + str(xq_options) + ' ')
        if xq not in xq_options:
            print('请输入选项内的信息\n')
            continue
        if xn != xn_default and xq != xq_default:
            print('系统不支持同时更换学期与学年，请重新输入\n')
        break

    # 构造post信息并获取页面
    if xq == xq_default and xn == xn_default:
        print_table(bs_obj)  # 直接获取默认课表页面
        return
    elif xn != xn_default:
        post_data = {'__EVENTTARGET': 'xnd', '__EVENTARGUMENT': xn, '__VIEWSTATE': viewstate,
                     'xnd': xn, 'xqd': xq}
    elif xq != xq_default:
        post_data = {'__EVENTTARGET': 'xqd', '__EVENTARGUMENT': xq, '__VIEWSTATE': viewstate,
                     'xnd': xn, 'xqd': xq}
    else:
        raise ValueError
    table_response = session.post(table_url, post_data)  # 请求选择的课表页面
    bs_obj = BeautifulSoup(table_response.text, 'lxml')
    print_table(bs_obj)
    return


def spider(response, session):
    '''爬虫入口 确认学生信息 扩展功能'''
    url = response.url
    print('-------------------')
    base_url = url[:25]
    bs_obj = BeautifulSoup(response.text, 'lxml')

    xhxm_string = bs_obj.find('div', {'class': 'info'}).find('span', id='xhxm').get_text()
    usernumber = xhxm_string[:9]
    name = xhxm_string.split(' ')[-1:][0]
    print('你好！' + name)
    print('你的学号：' + usernumber)
    print('-------------------')

    # 解析课表
    table_headers = HEADERS
    table_headers['Referer'] = url
    session.headers.update(table_headers)
    table_url = bs_obj.find('ul', {'class': 'nav'}).find('a', {'onclick': "GetMc('学生个人课表');"})
    table_url = base_url + table_url['href']
    parse_table(table_url, session)


def get_code(session):
    '''获取验证码并返回验证码字符串'''
    response = session.get('http://211.70.149.135:88/CheckCode.aspx')  # 因为教务系统验证码地址固定 所以写死了
    pic = BytesIO(response.content)
    pic = Image.open(pic)
    pic.show()
    code = input('验证码:')  # 这里暂由用户手动输入验证码
    return code


def login(url, session):
    '''登陆函数 获取学生信息 登陆建立session'''
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
        if '请' not in list(title):  # 判断是否登录成功
            return response
        else:
            print('输入信息错误，请重试')
            continue


def main():
    session = requests.session()
    session.headers.update(HEADERS)
    response = login('http://211.70.149.135:88/default2.aspx', session)
    spider(response, session)
    session.close()


if __name__ == '__main__':
    main()
