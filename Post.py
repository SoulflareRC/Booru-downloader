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
import validators

class Post(object):

    def __init__(self):
        self.post_id = None
        self.post_url = None
        self.img_url = None
        self.tag_info = {}
        self.post_info = {}
        self.valid = True
    def get_tag_list(self):
        tags = ""
        for key in self.tag_info.keys():
            tags += ','.join(self.tag_info[key]) + ","
        return tags
    def dl_post(self,base_dir,dl_img = True,dl_info = False):
        print(f'Start downloading post {self.post_url}')
        print('What?', self.valid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        }
        if not os.path.exists(base_dir):
            print(f'Creating base directory {base_dir}')
            os.makedirs(base_dir)

        if self.valid:
            print('Valid')
            img_url = self.img_url
            fname = img_url[img_url.rfind('/') + 1:]
            if  dl_img:
                print(f'Downloading image from {img_url}')
                content = rq.get(img_url,headers=headers).content
                fpath = os.path.join(base_dir, fname)
                if os.path.exists(fpath):
                    print(f'{fpath} already exists!')
                with open(fpath, 'wb') as f:
                    f.write(content)
            if  dl_info:
                tags = self.get_tag_list()
                print(tags)
                raw_fname = fname[:fname.rfind('.')]
                txt_fname = raw_fname + '.txt'
                tpath = os.path.join(base_dir, txt_fname)
                with open(tpath, 'w') as f:
                    f.write(tags)
        else:
            print(f'Invalid post!{self.post_url}')

class Post_Danbooru(Post):

    def __init__(self,post_id):
        super(Post_Danbooru, self).__init__()
        self.tag_info = {
            'meta': [],
            'artist': [],
            'copyright': [],
            'character': [],
            'general': [],
        }
        self.post_info = {
            "id": None,
            "uploader": None,
            "date": None,
            "size": None,
            "source": None,
            "rating": None,
            "score": None,
            "favorites": None,
            "status": None
        }
        head = 'https://danbooru.donmai.us/posts/'
        url = head + post_id
        self.post_id = post_id
        self.post_url = url
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
            print(f'Found invalid post {self.post_url}')
            return
        # get image src
        target = soup.find(name='section', attrs={'class': 'image-container'})
        # print(target)
        img = target.select_one('picture img')
        # print(img['src'])
        src = img['src']


        self.img_url = src
    # def dl_post(self,base_dir,dl_img = True,dl_info = False):
    #     print('Dl post(danbooru)')
    #     super(Post_Danbooru, self).dl_post(base_dir,dl_img,dl_img,dl_info)
class Post_Yandere(Post):

    def __init__(self, post_id):
        super(Post_Yandere, self).__init__()
        self.tag_info = {
        'faults': [],
        'circle': [],
        'artist': [],
        'copyright': [],
        'character': [],
        'general': [],
    }
        self.post_info = {}
        head = 'https://yande.re/post/show/'
        url = head + post_id
        # print(url)
        self.post_url = url
        self.post_id = post_id

        content = rq.get(url).content
        soup = bs(content, 'html.parser')

        img = soup.select_one("div.content>div>img#image")
        img_url = img["src"]
        # print(img_url)
        self.img_url = img_url

        sidebar = soup.select_one("#post-view > div.sidebar")
        tag_sidebar = sidebar.select_one("ul#tag-sidebar")

        for key in self.tag_info.keys():
            items = tag_sidebar.select(f"li.tag-type-{key}")
            for item in items:
                # print(item)
                a = item.find_all('a')
                a = a[len(a) - 1]
                text = a.get_text()
                # print(text)
                self.tag_info[key].append(text)

        stats_sidebar = sidebar.select_one("div#stats>ul")
        items = stats_sidebar.select("li")
        for item in items:
            text = item.get_text()
            text = str(text).replace('"', '')
            split_idx = text.find(':')
            key = text[:split_idx].strip().lower()
            value = text[split_idx + 1:].strip()
            # print(f'Key:{key}')
            # print(f'Value:{value}')
            # if key not in self.post_info.keys():
            #     self.post_info[key] = []
            if key == 'score':
                value = int(value)
            self.post_info[key] = value
        # print(self.post_info)
    # def dl_post(self,base_dir,dl_img = True,dl_info = False):
    #     super(Post_Yandere, self).dl_post(base_dir, dl_img, dl_img, dl_info)

class Post_Sankaku(Post):
    '''
        post_id = None
    post_url = None
    img_url = None
    tag_info = {

    }
    post_info = {

    }
    valid = True
    '''
    def __init__(self, json_dict,sample_only=True):
        super(Post_Sankaku, self).__init__()
        self.headers = {
            'referer': 'https://beta.sankakucomplex.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        }
        self.tag_filter = True #filter out all posts that have tagme tag
        self.post_info = json_dict
        self.post_id = json_dict['id']
        self.sample_only = sample_only
        if self.sample_only:
            url = str(json_dict['sample_url'])
        else:
            url = str(json_dict['file_url'])
        # url = url[ :url.rfind('?') ]
        self.post_url = url

        if not validators.url(self.post_url):
            self.valid = False
        # else:
        #     self.valid = False
        self.img_url = self.post_url
        # print('Url:',url)
        # print('Valid:',self.valid)
        tags = [ d['tagName'] for d in json_dict['tags'] ]
        if self.tag_filter:
            if 'tagme' in tags:
                print(f'Filtered post {self.post_url}')
                self.valid = False
        self.tag_info['general'] = tags


    def dl_post(self, base_dir, dl_img=True, dl_info=False):
        # print(f'Start downloading post {self.post_url}')
        print(f'dl post in Sankaku to {base_dir} {dl_img} {dl_info}')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        if self.valid:
            img_url = self.img_url

            fname = img_url[ img_url.rfind('/')+1:img_url.rfind('?') ] #special
            if dl_img:
                content = rq.get(img_url,headers=self.headers).content
                fpath = os.path.join(base_dir, fname)
                print(f'downloading {fname} from: {img_url} to {fpath}')
                if os.path.exists(fpath):
                    print(f'{fpath} already exists!')
                with open(fpath, 'wb') as f:
                    f.write(content)
            if dl_info:
                tags = self.get_tag_list()
                # print(tags)
                raw_fname = fname[:fname.rfind('.')]
                txt_fname = raw_fname + '.txt'
                tpath = os.path.join(base_dir, txt_fname)
                with open(tpath, 'w') as f:
                    f.write(tags)
        else:
            print(f'Invalid post!{self.post_url}')
# id = "30890271"
# post_s = Post_Sankaku(id)
