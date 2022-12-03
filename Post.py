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
class Post(object):
    post_id = None
    post_url = None
    img_url = None
    tag_info = {
        'meta': [],
        'artist': [],
        'copyright': [],
        'character': [],
        'general': [],
        }
    post_info = {
        "id":None,
        "uploader":None,
        "date":None,
        "size":None,
        "source":None,
        "rating":None,
        "score":None,
        "favorites":None,
        "status":None
    }
    valid = True
    def __init__(self,post_id):
        head = 'https://danbooru.donmai.us/posts/'
        url = head + post_id
        # print(url)
        content = rq.get(url).content
        soup = bs(content, 'html.parser')
        # get post info
        sidebar = soup.select_one('#sidebar')
        # print(len(sidebar.children))
        children = sidebar.find_all(recursive=False)
        # for c in children:
        #     print(c)
        taglist = sidebar.select_one('#tag-list')
        # print('Tag list:',taglist)
        # exit(0)
        for key in self.tag_info.keys():
            ul = taglist.select_one(f'ul.{key}-tag-list')
            if ul:
                for li in ul.find_all(recursive=False):
                    a = li.select_one('a.search-tag')
                    text = a.get_text()
                    self.tag_info[key].append(text)
        postinfo = sidebar.select_one("#post-information")

        for key in self.post_info.keys():
            li = postinfo.select_one(f'li#post-info-{key}')
            if key == "score":
                text = li.select_one("span.post-score").get_text()
            else :
                a = li.select_one('a')
                if a:
                    text = a.get_text()
                else:
                    text = li.get_text()
            text = str(text).strip()
            if key in ['score','favorites']:
                text = int(text)
            self.post_info[key] = text
        # print('Info:')
        # for key in tag_info.keys():
        #     print("---------------" + key + ":" + "--------------------")
        #     for tag in tag_info[key]:
        #         print(tag)

        if 'animated' in self.tag_info['meta']:
            self.valid = False
            return
        # get image src
        target = soup.find(name='section', attrs={'class': 'image-container'})
        # print(target)
        img = target.select_one('picture img')
        # print(img['src'])
        src = img['src']

        self.post_id = post_id
        self.post_url = url
        self.img_url = src
    def get_tag_list(self):
        tags = ""
        for key in self.tag_info.keys():
            tags += ','.join(self.tag_info[key]) + ","
        return tags
    def dl_post(self,base_dir,dl_img = True,dl_info = False):
        # print(f'Start downloading post {self.post_url}')

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        if self.valid:
            img_url = self.img_url
            fname = img_url[img_url.rfind('/') + 1:]
            if  dl_img:
                content = rq.get(img_url).content
                fpath = os.path.join(base_dir, fname)
                if os.path.exists(fpath):
                    print(f'{fpath} already exists!')
                with open(fpath, 'wb') as f:
                    f.write(content)
            if  dl_info:
                tags = self.get_tag_list()
                # print(tags)
                raw_fname = fname[:fname.rfind('.')]
                txt_fname = raw_fname + '.txt'
                tpath = os.path.join(base_dir, txt_fname)
                with open(tpath, 'w') as f:
                    f.write(tags)
        else:
            print('Invalid post!')

# post = Post('5868485')
# print(post.post_info)
