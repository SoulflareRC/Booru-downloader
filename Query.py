import json

import gradio
import gradio as gr
import requests as rq
from bs4 import BeautifulSoup as bs
import os
from PIL import Image
from io import BytesIO
import random
import threading as tr
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import *
from Post import *
class Query(object):

    def __init__(self):
        self.base_dir = None
        self.query_url = None
        self.posts = []
        self.query_tags = None
        self.progress_query_page = 0
        self.max_page = 0
        self.max_post = 1000
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.executor_decode_post = ThreadPoolExecutor(max_workers=4)
        self.executor_dl = ThreadPoolExecutor(max_workers=16)
        self.dl_when_query = False
        self.dl_img = True
        self.dl_info = False
        self.score_filter = 0
    # implement this
    def filter_score(self,threshold:int,max_posts:int = 0):pass
    # implement this
    def query_page(self,page_num):pass
    def query_all(self):
        print(f'Max page(from query all):{self.max_page}')
        query_tasks = []
        for i in range(1,self.max_page+1):
            task = self.executor.submit(self.query_page,i)
            query_tasks.append(task)
        for t in as_completed(query_tasks):
            self.progress_query_page+=1
            print(f'Done querying page {self.progress_query_page}/{self.max_page}')
        print(f'Number of post:{len(self.posts)}')
    def get_preview_img(self):
        print(f'Hey,max page is {self.max_page}')
        num = 10
        imgs = []
        attempt = 0
        print(f"{len(imgs)<num },{attempt<self.max_page}")
        while len(imgs)<num and attempt<self.max_page:
            # print('Here')
            self.query_page(random.randint(1, min(self.max_page, 1000)))
            for post in self.posts:
                img_url = post.img_url
                if img_url:
                    print(img_url)
                    content = rq.get(img_url).content
                    content = BytesIO(content)
                    img = Image.open(content)
                    imgs.append(img)
                    # imgs.add((Image.open(BytesIO(content))))
            # print(f"Got {len(self.posts)} posts")
            self.posts.clear()
            attempt += 1

        # clear posts
        return imgs
    def dl_all_posts(self):

        tasks = []
        progres = 0
        all = len(self.posts)
        print(f'Downloading {all} posts')
        if not self.dl_img and not self.dl_info:
            print("Nothing will be downloaded")
        else:
            for post in self.posts:
                if self.base_dir is None:
                    self.base_dir = str(self.query_tags)
                task = self.executor_dl.submit(post.dl_post, os.path.join('images',self.base_dir),
                                                   self.dl_img, self.dl_info)
                tasks.append(task)
            for t in as_completed(tasks):
                progres+=1
                print(f'Finished downloading post {progres}/{all}')
            print('Done!')

class Query_Danbooru(Query):
    def __init__(self, tags):
        super(Query_Danbooru, self).__init__()
        head = 'https://danbooru.donmai.us/posts?tags='
        if type(tags) == str:
            self.query_tags = [tags]
            result = head + tags
        elif type(tags) == list:
            self.query_tags = tags
            result = head
            for tag in tags:
                result += tag + "+"
        print('Query url:', result)
        self.query_tags = tags
        self.query_url = result

        if not self.max_page:
            content = rq.get(result).content
            soup = bs(content, 'html.parser')
            max_page = soup.find_all('a', {'class': 'paginator-page'})
            max_page = max_page[len(max_page) - 1]
            # print("Max page:", max_page.getText())
            self.max_page = min(1000, int(max_page.getText()))  # danbooru doesn't allow accessing the last page
            print(f'Max page set to:{self.max_page}')
    def filter_score(self,threshold:int,max_posts:int = 0):
        result = [post for post in self.posts if post.post_info['score']>=threshold]
        if max_posts:
            return result[:max_posts]
        return result
    def query_page(self, page_num):
        #     https://danbooru.donmai.us/posts?page=2&tags=1girl
        tags = self.query_tags
        tag_str = ""
        if type(tags) == str:
            tag_str += tags
        elif type(tags) == list:
            for tag in tags:
                tag_str += tag + "+"
        url = f'https://danbooru.donmai.us/posts?page={str(page_num)}&tags={tag_str}'
        # print(f'Page {page_num}:{url}')
        content = rq.get(url).content
        soup = bs(content, 'html.parser')
        articles = soup.find_all(name='article', attrs={'class': 'post-preview'})
        print(f'{len(articles)} articles on page {page_num} {url}')
        for a in articles:
            post_id = a['data-id']
            # post = self.executor_decode_post.submit(fn=Post_Danbooru,args=post_id).result()
            post = self.executor_decode_post.submit(Post_Danbooru,post_id).result()
            # post = Post_Danbooru(post_id)
            if self.score_filter:
                if post.post_info['score']>self.score_filter:
                    self.posts.append(post)
                    if self.dl_when_query:
                        self.executor_dl.submit(post.dl_post,os.path.join('images', str(self.query_tags)))
            else:
                self.posts.append(post)
                if self.dl_when_query:
                    self.executor_dl.submit(post.dl_post,os.path.join('images',str(self.query_tags)) )
    def get_preview_img(self):
        return super(Query_Danbooru, self).get_preview_img()
class Query_Yandere(Query):
    # make initial query, get preview and attributes
    def __init__(self, tags):
        super(Query_Yandere, self).__init__()
        head = 'https://yande.re/post?tags='
        if type(tags) == str:
            self.query_tags = [tags]
            result = head + tags
        elif type(tags) == list:
            self.query_tags = tags
            result = head
            for tag in tags:
                result += tag + "+"
        print('Query url:', result)
        self.query_tags = tags
        self.query_url = result

        if not self.max_page:
            content = rq.get(result).content
            soup = bs(content, 'html.parser')
            paginator = soup.select_one('div#paginator')
            a = paginator.find_all('a')
            aa = []
            for l in a:
                if l.has_attr('aria-label'):
                    aa.append(l)
            # print(aa)
            max_page = aa[len(aa)-1]
            text = max_page.get_text()
            self.max_page = int(text)
            print(self.max_page)
    def query_page(self, page_num):
        # https://yande.re/post?page=5&tags=feet+ass
        tags = self.query_tags
        tag_str = ""
        if type(tags) == str:
            tag_str += tags
        elif type(tags) == list:
            for tag in tags:
                tag_str += tag + "+"
        url = f'https://yande.re/post?page={str(page_num)}&tags={tag_str}'
        # print(f'Page {page_num}:{url}')
        content = rq.get(url).content
        soup = bs(content, 'html.parser')
        articles = soup.select('ul#post-list-posts>li')

        print(f'{len(articles)} articles on page {page_num} {url}')
        post_decode_tasks = []
        for li in articles:
            post_id = li['id'].replace('p','')
            post = self.executor_decode_post.submit(Post_Yandere,post_id).result()
            print(post.post_url)
            if self.score_filter:
                if post.post_info['score']>self.score_filter:
                    self.posts.append(post)
                    if self.dl_when_query:
                        self.executor_dl.submit(post.dl_post,os.path.join('images', str(self.query_tags)), )
            else:
                self.posts.append(post)
                if self.dl_when_query:
                    self.executor_dl.submit(post.dl_post,os.path.join('images',str(self.query_tags)) )
    def get_preview_img(self):
        return super(Query_Yandere, self).get_preview_img()
class Query_Sankaku(Query):
    def __init__(self, tags):
        self.executor_dl = ThreadPoolExecutor(max_workers=8)
        super(Query_Sankaku, self).__init__()
        self.headers ={
    'referer': 'https://beta.sankakucomplex.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
            }
        order = 'popularity'
        limit = 100
        search_term = ""

        if type(tags) == str:
            self.query_tags = [tags]
            search_term = tags
        elif type(tags) == list:
            self.query_tags = tags
            for tag in tags:
                search_term += tag + "%20"
        # rq_url = f'https://capi-v2.sankakucomplex.com/posts/keyset?page={0}limit={limit}&tags=order:{order}+{search_term}'
        rq_url = f'https://capi-v2.sankakucomplex.com/posts?lang=english&page={0}&limit={limit}&tags=order:{order}%20{search_term}'
        print('Query url:', rq_url)
        self.max_page = 1000
        self.query_tags = tags
        self.query_url = rq_url
        self.limit = limit
        self.search_term = search_term
        self.order = order
    def query_page(self,page_num):
        rq_url = f'https://capi-v2.sankakucomplex.com/posts?lang=english&page={page_num}&limit={self.limit}&tags=order:{self.order}%20{self.search_term}'
        res = rq.get(rq_url,headers=self.headers)
        data = res.json()
        cnt=0
        for post in data:
            p = Post_Sankaku(post)
            if(p.valid):
                print(p.img_url)
                self.posts.append(p)
                cnt+=1
        print(f'Found {cnt} valid posts on page {page_num}')
        return cnt
    # def query_all(self):
    #     print(f'Max page(from query all):{self.max_page}')
    #     query_tasks = []
    #     for i in range(1,self.max_page+1):
    #         task = self.executor.submit(self.query_page,i)
    #         query_tasks.append(task)
    #     for t in as_completed(query_tasks):
    #         self.progress_query_page+=1
    #         print(f'Done querying page {self.progress_query_page}/{self.max_page}')
    #     print(f'Number of post:{len(self.posts)}')
# gradio.close_all()
# exit(0)

# tags = ['haimura_kiyotaka','1girl','rating:s','rating:q']
# tags = ['remana']
# q = Query_Sankaku(tags)
# q.base_dir = 'remana-large'
# q.base_dir = 'casino'
# q.dl_img=True
# q.dl_info=True
# q.max_page=3
# q.query_all()
# # print(q.max_page)
# # q.max_page = 10
# # ps = set()
# q.base_dir = "test"
import time

# q.base_dir = "Sankaku_test"
# q.dl_all_posts()
# # post = q.posts[0]
# headers = {
#     'referer': 'https://beta.sankakucomplex.com/',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
# }
# for i,post in enumerate(q.posts[:3]):
#     print(post.img_url)
#     img_url = post.img_url
#     fname = img_url[img_url.rfind('/') + 1:img_url.rfind('?')]
#     content = rq.get(post.img_url,headers=headers).content
#     with open(f'temp/images/{fname}','wb') as f:
#         f.write(content)
#         time.sleep(1)
# q.dl_all_posts()
# q.query_page(2)
# q.query_page(3)
# q.dl_all_posts()


# for p in q.posts:
#     print(p.img_url)
# rq_url = 'https://capi-v2.sankakucomplex.com/posts?lang=english&page=1&limit=100&tags=order:popularity%20hitomaru'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
# }
# res = rq.get(rq_url,headers=headers).json()
# ps = set()
# for post in res:
#     # print(post['file_url'])
#     url = post['file_url']
#
#     if url is not None:
#         print(url)
#         ps.add(url)
# print(len(ps))
#
# rq_url = 'https://capi-v2.sankakucomplex.com/posts?lang=english&page=2&limit=100&tags=order:popularity%20hitomaru'
# res = rq.get(rq_url,headers=headers).json()
# for post in res:
#     # print(post['file_url'])
#     url = post['file_url']
#     # print(post['id'])
#     if url is not None:
#         print(url)
#         ps.add(url)
# print(len(ps))


'''
null_url happening
{"id":146460,"name":"Nigredo","avatar":"https://s.sankakucomplex.com/data/avatars/146460-l.jpg?1661137225161","avatar_rating":"s"},
"sample_url":null,
"sample_width":512,"sample_height":768,
"preview_url":null,
"preview_width":null,
"preview_height":null,
"file_url":null,
"width":512,"height":768,"file_size":552192,"file_type":"image/png","created_at":{"json_class":"Time","s":1669935776,"n":0},"has_children":false,"has_comments":false,"has_notes":false,"is_favorited":false,"user_vote":null,"md5":"b5d43ee2103db90f78f7fb47e50762b6","parent_id":null,"change":74142652,"fav_count":409,"recommended_posts":-1,"recommended_score":0,"vote_count":55,"total_score":263,"comment_count":null,"source":"https://i.pximg.net/img-original/img/2022/10/31/21/00/08/102397143_p5.png","in_visible_pool":false,"is_premium":false,"is_rating_locked":false,"is_note_locked":false,"is_status_locked":false,"redirect_to_signup":true,"sequence":null,"tags":

{"id":1513908,"name":"BattlequeenYume","avatar":"https://s.sankakucomplex.com/data/avatars/1513908-l.jpg?1667993324653","avatar_rating":"s"},"sample_url":"https://v.sankakucomplex.com/data/sample/2f/96/sample-2f966658c9e6c1c9f78007fcec0193cf.jpg?e=1670794250&expires=1670794249&m=L04ykJ4aOFCOL0ydAvUMew&token=rd_Ws4Q-Vn4TP9Y_jhqOH2MbiSgyweqXsZAIHRjd8w4","sample_width":679,"sample_height":1000,"preview_url":"https://v.sankakucomplex.com/data/preview/2f/96/2f966658c9e6c1c9f78007fcec0193cf.jpg?e=1670794250&expires=1670794249&m=ZqMYh45dkPE4ChdtleasZA&token=OJ_Se-Mao0HJqeQzJZeatm1fhnixbocP24jQakyHySM","preview_width":204,"preview_height":300,"file_url":"https://v.sankakucomplex.com/data/2f/96/2f966658c9e6c1c9f78007fcec0193cf.jpg?e=1670794250&expires=1670794249&m=I4CR5YEw02CZri51qcbfmA&token=9-PZDYU5qQSdTkiYS_gXT1A2KZtcxwCl_DorGANxMN4","width":2480,"height":3648,"file_size":4123958,"file_type":"image/jpeg","created_at":{"json_class":"Time","s":1670591382,"n":0},"has_children":false,"has_comments":false,"has_notes":false,"is_favorited":false,"user_vote":null,"md5":"2f966658c9e6c1c9f78007fcec0193cf","parent_id":32263329,"change":74298002,"fav_count":117,"recommended_posts":-1,"recommended_score":0,"vote_count":14,"total_score":70,"comment_count":null,"source":"","in_visible_pool":false,"is_premium":false,"is_rating_locked":false,"is_note_locked":false,"is_status_locked":false,"redirect_to_signup":false,"sequence":null,"tags"


'''

# posts = q.posts
# for post in posts:
#     if post.valid:
#         print(post.img_url)
#         print(post.tag_info)
#         post.dl_post('images/Sankaku/hitomaru',True,True)