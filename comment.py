import json
import time
import requests
import http.cookiejar as cookielib
from lxml import etree
import pandas as pd
import numpy as np


class WeiboComment(object):
    def __init__(self, cid):
        self.session = requests.Session()
        self.cid = cid
        self.page_num = 1
        self.sum_comment_number = 0
        self.headers = {'User-Agent': 'mozilla/5.0 (windowS NT 10.0; win64; x64) appLewEbkit/537.36 (KHTML, likE gecko) chrome/71.0.3578.98 safari/537.36'}
        self.cookies = self.get_cookies()
        self.url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&filter=all&from=singleWeiBo&__rnd=%d' % (self.cid,int(time.time()*1000))

    def get_cookies(self):
        """ 读取cookies"""
        cookies = cookielib.LWPCookieJar("Cookie.txt")
        cookies.load(ignore_discard=True, ignore_expires=True)
        return requests.utils.dict_from_cookiejar(cookies)


    def get_next_comment(self,html):
        """获得下一页的url"""
        com_ls = html.xpath('//div[@node-type="root_comment"]')
        # 评论为空时的容错
        try:
            com_max_id = com_ls[-1].xpath('./@comment_id')[0]
        except:
            return 'NO'

        com_max_id = str(int(com_max_id)-1)
        length = len(com_ls)
        self.sum_comment_number += length
        self.page_num +=1
        # print(com_max_id, length)
        next_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={cid}&root_comment_max_id={mid}&root_comment_max_id_type=&root_comment_ext_param=' \
                   '&page={page_num}&filter=all&sum_comment_number={count_num}&filter_tips_before=1&from=singleWeiBo&__rnd=1574357153056'.format(cid=self.cid,mid=com_max_id,page_num=self.page_num,count_num=self.sum_comment_number)
        print(next_url)
        return next_url

    def get_comment_data(self,html):
        """提取评论   用户名+内容+时间+主页url"""
        uls = html.xpath('//div[@class="list_con"]')
        datas = []
        for ul in uls:
            data = []
            user = ul.xpath('./div[@class="WB_text"]/a/text()')[0]
            data.append(user)
            comment = ul.xpath('./div[@class="WB_text"]/text()')[1]
            comment = comment.split('：',maxsplit=1)[-1].strip()
            data.append(comment)
            time = ul.xpath('./div[contains(@class,"WB_func")]/div[contains(@class,"WB_from")]/text()')[0]
            data.append(time)
            user_url = 'https:'+ul.xpath('./div[@class="WB_text"]/a/@href')[0]
            data.append(user_url)
            datas.append(data)
        return datas

    def save_data_to_csv(self,data):
        """将数据存储成csv"""
        print(data)
        data = np.array(data).reshape(-1, 4)
        result_weibo = pd.DataFrame(data)
        result_weibo.to_csv('weibo_comment.csv', mode='a', index=False, encoding='gb18030', header=False)

    def run(self):
        n = 0
        column = pd.DataFrame({}, columns=['用户名', '评论内容', '评论时间', '用户主页url'])
        column.to_csv('weibo_comment.csv', index=False, encoding='gb18030')
        while True:
            com_data = self.session.get(url=self.url, headers=self.headers, cookies=self.cookies)
            text = json.loads(com_data.text)
            # print(type((text)))
            html = etree.HTML(text['data']['html'])
            self.url = self.get_next_comment(html)
            data = self.get_comment_data(html)

            self.save_data_to_csv(data)
            n += 1
            print('第%d页'%n)
            time.sleep(1)

if __name__ == '__main__':
    cid = 4461440541391619
    weibo = WeiboComment(cid = cid)
    weibo.run()


