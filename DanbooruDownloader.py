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
from Query import Query

class DanbooruDownloader(object):
    dl_img = True
    dl_info = False
    score_filter = 0
    max_pages = 30
    executor = ThreadPoolExecutor(max_workers=16)
    query = None
    def dl_query(self,tags,max_pages = max_pages):
        q = Query(tags)
        q.score_filter = self.score_filter
        q.max_page = max_pages
        q.query_all()
        print(len(q.posts))
        base_dir = os.path.join("images",str(tags))
        dl_tasks = []
        progress = 0
        progress_todo = len(q.posts)
        for post in q.posts:
            dl_task = self.executor.submit(post.dl_post,base_dir,self.dl_img,self.dl_info)
            dl_tasks.append(dl_task)
        for t in as_completed(dl_tasks):
            progress+=1
            print(f'Finished downloading post {progress}/{progress_todo}')

# post = Post('205988')
# post.dl_post('test',False,True)
#
# tags = ['1girl']
# query = Query(tags)
# query.query_page(1)
# print(len(query.posts))
# d = DanbooruDownloader()
# d.dl_query(['bangs','arms_up'],1)


# query = Query(tags)
# query.dl_when_query = True
# query.max_page = 30
# query.query_all()
# print(len(query.posts))
