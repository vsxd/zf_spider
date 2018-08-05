
# 方正教务系统爬虫 for AHUT
---
## fz_spider 爬取学生教务信息

+ 爬取并显示课表信息
+ 爬取并显示考试时间
+ 抢课(developing)

+ 使用说明 
    1. 推荐使用python virtualenv虚拟环境
    > $ pip3 install virtualenv
    1. 在本项目目录下新建虚拟环境
    > $ virtualenv venv
    1. 进入虚拟环境   
    > $ source ./venv/bin/activate
    1. 初始化虚拟环境后，引入依赖
    > (venv) $ pip3 install -r requirements.txt
    1. 在虚拟环境中启动main程序
    > (venv) $ python3 ./main.py