# coding: utf-8
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from PIL import Image
from io import BytesIO
import re
import getpass


class InfoStorage:
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Host': '211.70.149.135:88',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
    }
    URL = 'http://211.70.149.135:88/default2.aspx'
    VCODE_URL = 'http://211.70.149.135:88/CheckCode.aspx'
    LOGIN_INFO = {'logined': False,
                  'bsobj': None,
                  'response': None}

    COURSE_TABLE_INFO = {}
    EXAM_TABLE_INFO = {}
    SELECT_COURSE_INFO = {}
    SESSION = None

    @staticmethod
    def print_student_info():
        url = InfoStorage.LOGIN_INFO['response']
        print('-------------------')
        # base_url = url[:25]
        xhxm_string = InfoStorage.LOGIN_INFO['bsobj'].find('div', {'class': 'info'}).find(
            'span', id='xhxm').get_text()
        usernumber = xhxm_string[:9]
        name = xhxm_string.split(' ')[-1:][0]
        print('你好！' + name)
        print('你的学号：' + usernumber)
        print('-------------------')


    @staticmethod
    def get_code():
        '''获取验证码并返回验证码字符串'''
        response = InfoStorage.SESSION.get(InfoStorage.VCODE_URL)
        pic = BytesIO(response.content)
        pic = Image.open(pic)
        pic.show()
        code = input('验证码:')  # 这里暂由用户手动输入验证码
        return code

    @staticmethod
    def login():
        if InfoStorage.SESSION is None:
            print('SESSION is None')
            return
        if InfoStorage.LOGIN_INFO['logined'] is True:
            print('Already Login')
            return
        InfoStorage.SESSION.headers.update(InfoStorage.HEADERS)
        while InfoStorage.LOGIN_INFO['logined'] is False:
            # username = input('请输入学号:')
            # password = getpass.getpass('请输入密码:')
            username = '169024014'
            password = '0714sxd'
            try:
                html = InfoStorage.SESSION.get(InfoStorage.URL).text
                bs_obj = BeautifulSoup(html, 'html.parser')
                viewstate = bs_obj.find('input', {'name': '__VIEWSTATE'})['value']
                validating_code = InfoStorage.get_code()
            except Exception as e:
                print(e)
                print('网络错误')
                continue
            post_data = {'__VIEWSTATE': viewstate, 'TextBox1': username,
                         'TextBox2': password, 'TextBox3': validating_code, 'RadioButtonList1': '',
                         'Button1': '', 'lbLanguage': ''}
            try:             
                InfoStorage.LOGIN_INFO['response'] = InfoStorage.SESSION.post(InfoStorage.URL, post_data)
                InfoStorage.LOGIN_INFO['response'].encoding = InfoStorage.LOGIN_INFO['response'].apparent_encoding
                InfoStorage.LOGIN_INFO['bsobj'] = BeautifulSoup(InfoStorage.LOGIN_INFO['response'].text, 'lxml')
                title = InfoStorage.LOGIN_INFO['bsobj'].find('title').get_text()
            except Exception as e:
                print(e)
                print('网络解析错误')
                return
            if '请' not in title:  # 判断是否登录成功
                print('登陆成功')
                InfoStorage.LOGIN_INFO['logined'] = True
                InfoStorage.print_student_info()
                input('按回车键继续操作')
            else:
                print('输入信息错误，请重试')
            


class CourseTableParser:
    def __init__(self):
        self.session = None
        self.table_url = None
        self.bs_obj = None
        self.pretty_table = None
    
    @staticmethod
    def start():
        if InfoStorage.LOGIN_INFO['logined'] is False:
            print('你还没有登陆，请登录后使用其他功能')
            return
        ctp = CourseTableParser()
        ctp.session = InfoStorage.SESSION
        response_url = InfoStorage.LOGIN_INFO['response'].url
        table_headers = InfoStorage.HEADERS
        table_headers['Referer'] = response_url
        ctp.session.headers.update(table_headers)
        table_url = InfoStorage.LOGIN_INFO['bsobj'].find('ul', {'class': 'nav'}).find(
        'a', {'onclick': "GetMc('学生个人课表');"})
        ctp.table_url = response_url[:25] + table_url['href']

        ctp.parse_table()
        ctp.print_table()


    def parse_table(self):
        '''与用户交互 解析基本信息 并请求响应的课表页面 传入默认的table的url 和session对象'''
        response = self.session.get(self.table_url)
        bs_obj = BeautifulSoup(response.text, 'lxml')
        viewstate = bs_obj.find('input', {'name': '__VIEWSTATE'})['value']
        table = bs_obj.find('span', {'class': 'formbox'})

        # 抽取学年学期选项信息
        tr = table.find('table', {'class': 'formlist noprint'}).find('tr')
        xn_options = tr.find('select').find_all('option')
        xn_options = [option.get_text() for option in xn_options]
        xq_options = ['1', '2']
        xn_default = tr.find('select', {'name': 'xnd'}).find(
            'option', {'selected': 'selected'}).string
        xq_default = tr.find('select', {'name': 'xqd'}).find(
            'option', {'selected': 'selected'}).string

        # 抽取并显示学生个人信息
        tr = table.find('table', {'class': 'formlist noprint'}).find(
            'tr', {'class': 'trbg1'})
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
            # if xn != xn_default and xq != xq_default:
            #     print('系统不支持同时更换学期与学年，请重新输入\n')
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
        table_response = self.session.post(self.table_url, post_data)  # 请求选择的课表页面
        self.bs_obj = BeautifulSoup(table_response.text, 'lxml')
        return

    def print_table(self):
        '''按格式输出页面中的课表信息 参数为beautifulsoup对象'''
        tbody = self.bs_obj.find('table', {'class': 'blacktab'}
                            )  # 注意tbody标签在html中实际并不存在 是browser自己加的
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
                        info += '\n' + infos[1] + '\n' + \
                            infos[2] + '\n' + infos[3] + '\n' # 课程的更多信息
                    row.append(info)  # 在行中加入信息
                table.append(row)  # 把行加入表格
        for row in table:
            # 清洗信息 删除多余
            if row[0] == '上午' or row[0] == '下午' or row[0] == '晚上':
                row.remove(row[0])
        table.pop()  # 清洗信息

        self.pretty_table = PrettyTable()  # 使用prettytable库打印表格
        self.pretty_table.field_names = table[0]
        for index in range(1, len(table)):
            self.pretty_table.add_row(table[index])
        print(self.pretty_table)


class CourseTimeTableParser():
    def __init__(self):
        self.session = None
        self.table_url = None
        self.bs_obj = None
        self.pretty_table = None
    
    @staticmethod
    def start():
        if InfoStorage.LOGIN_INFO['logined'] is False:
            print('你还没有登陆，请登录后使用其他功能')
            return
        cttp = CourseTimeTableParser()
        cttp.session = InfoStorage.SESSION
        response_url = InfoStorage.LOGIN_INFO['response'].url
        table_headers = InfoStorage.HEADERS
        table_headers['Referer'] = response_url
        cttp.session.headers.update(table_headers)
        table_url = InfoStorage.LOGIN_INFO['bsobj'].find('ul', {'class': 'nav'}).find(
        'a', {'onclick': "GetMc('学生考试查询');"})
        cttp.table_url = response_url[:25] + table_url['href']

        table_response = cttp.session.post(cttp.table_url)
        cttp.bs_obj = BeautifulSoup(table_response.text, 'lxml')

        cttp.print_table()


    
    def print_table(self):
        '''按格式输出页面中的课表信息 参数为beautifulsoup对象'''
        tbody = self.bs_obj.find('table', {'class': 'datelist'}
                            )
        trs = tbody.select('tr')
        table = []  # 用于存放信息的二维list
        for index in range(len(trs)):
            tds = trs[index].select('td')
            row = []  # 行
            for index in range(len(tds)):
                if index != 0 and index != 2 and index != 5:  # 数据清洗
                    infos = re.findall('(?<=>).+?(?=<)', str(tds[index])) 
                    row.append(infos[0])
            table.append(row)

        self.pretty_table = PrettyTable()  # 使用prettytable库打印表格
        self.pretty_table.field_names = table[0]
        for index in range(1, len(table)):
            self.pretty_table.add_row(table[index])
        print(self.pretty_table)