import json
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
from Post import Post
class Query(object):
    query_url = None
    posts = []
    query_tags = None

    progress_query_page = 0
    max_page = 0

    max_post = 1000
    executor = ThreadPoolExecutor(max_workers=4)
    executor_dl = ThreadPoolExecutor(max_workers=16)
    dl_when_query = False
    score_filter = 0

    # make initial query, get preview and attributes
    def __init__(self,tags):
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
            print("Max page:", max_page.getText())
            self.max_page = min(1000, int(max_page.getText())) #danbooru doesn't allow accessing the last page
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
            post = Post(post_id)
            if self.score_filter:
                if post.post_info['score']>self.score_filter:
                    self.posts.append(post)
                    if self.dl_when_query:
                        self.executor_dl.submit(post.dl_post,os.path.join('images', str(self.query_tags)))
            else:
                self.posts.append(post)
                if self.dl_when_query:
                    self.executor_dl.submit(post.dl_post,os.path.join('images',str(self.query_tags)) )

    def query_all(self):
        query_tasks = []
        for i in range(1,self.max_page+1):
            task = self.executor.submit(self.query_page,i)
            query_tasks.append(task)
        for t in as_completed(query_tasks):
            self.progress_query_page+=1
            print(f'Done querying page {self.progress_query_page}/{self.max_page}')
        print(f'Number of post:{len(self.posts)}')


    # get PIL images from
    def get_preview_img(self):

        num = 20
        imgs = set()
        attempt = 0
        while len(imgs)<num & attempt<self.max_page:
            self.query_page(random.randint(1, min(self.max_page, 1000)))
            for post in self.posts:
                img_url = post.img_url
                if img_url:
                    content = rq.get(img_url).content
                    imgs.add((Image.open(BytesIO(content))))
            self.posts.clear()
            attempt += 1
        # clear posts
        return list(imgs)
