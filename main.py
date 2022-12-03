# # This is a sample Python script.
#
# # Press Ctrl+Shift+R to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# import gradio
#
#
# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
# import json
# import gradio as gr
# import requests as rq
# from bs4 import BeautifulSoup as bs
# import os
# from PIL import Image
# from io import BytesIO
# import random
# import threading as tr
# from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import *
#
# # class DanbooruQuery(object):
#
#
# class DanbooruDownloader(object):
#     def __init__(self):
#         self.query_tags = None
#         self.query_url = None
#         self.posts = []
#         # self.img_urls = []
#         # self.info_dicts = []
#         self.dl_img = True
#         self.dl_info = False
#         self.resize = False
#         self.base_dir = 'images'
#         self.max_page = 0
#         self.max_post = 1000
#         self.executor = ThreadPoolExecutor(max_workers=4)
#
#         self.progress_query_page = 0
#         self.task_query_page = 0
#
#         self.progress_dl_post = 0
#
#
#     def dl_all_post(self):
#         for post in self.posts:
#             self.dl_post(post)
#     def dl_post(self,post):
#         if self.progress_dl_post < self.max_post:
#             if not os.path.exists(self.base_dir):
#                 os.makedirs(self.base_dir)
#
#             img_url = post['img_url']
#             fname = img_url[img_url.rfind('/') + 1:]
#             if self.dl_img:
#                 content = rq.get(img_url).content
#                 with open(os.path.join(self.base_dir, fname), 'wb') as f:
#                     f.write(content)
#             if self.dl_info:
#                 tags = ""
#                 for key in post['tag_info'].keys():
#                     tags+=','.join(post['tag_info'][key])+","
#                 # print(tags)
#                 raw_fname = fname[ :fname.rfind('.') ]
#                 txt_fname=raw_fname + '.txt'
#                 with open(os.path.join(self.base_dir, txt_fname), 'w') as f:
#                     f.write(tags)
#             # self.progress_dl_post+=1
#             # print(f"Done downloading post {post['post_url']},({self.progress_dl_post}/{self.max_post})")
#     def get_post(self,post_id):
#
#         head = 'https://danbooru.donmai.us/posts/'
#         url = head + post_id
#         # print(url)
#         content = rq.get(url).content
#         soup = bs(content, 'html.parser')
#         # get post info
#         sidebar = soup.select_one('#sidebar')
#         # print(len(sidebar.children))
#         children = sidebar.find_all(recursive=False)
#         # for c in children:
#         #     print(c)
#         taglist = sidebar.select_one('#tag-list')
#         # print('Tag list:',taglist)
#         # exit(0)
#         tag_info = {
#             'meta':[],
#             'artist': [],
#             'copyright': [],
#             'character': [],
#             'general': [],
#         }
#         for key in tag_info.keys():
#             ul = taglist.select_one(f'ul.{key}-tag-list')
#             if ul:
#                 for li in ul.find_all(recursive=False):
#                     a = li.select_one('a.search-tag')
#                     text = a.get_text()
#                     tag_info[key].append(text)
#         # print('Info:')
#         # for key in tag_info.keys():
#         #     print("---------------" + key + ":" + "--------------------")
#         #     for tag in tag_info[key]:
#         #         print(tag)
#
#         if 'animated' in tag_info['meta']:
#             return None, tag_info
#         # get image src
#         target = soup.find(name='section', attrs={'class': 'image-container'})
#         # print(target)
#         img = target.select_one('picture img')
#         # print(img['src'])
#         src = img['src']
#         return src, tag_info, url
#     def query_page(self,page_num):
#         #     https://danbooru.donmai.us/posts?page=2&tags=1girl
#         tags = self.query_tags
#         tag_str = ""
#         if type(tags) == str:
#             tag_str += tags
#         elif type(tags) == list:
#             for tag in tags:
#                 tag_str += tag + "+"
#         url = f'https://danbooru.donmai.us/posts?page={str(page_num)}&tags={tag_str}'
#         # print(f'Page {page_num}:{url}')
#         content = rq.get(url).content
#         soup = bs(content, 'html.parser')
#
#         articles = soup.find_all(name='article', attrs={'class': 'post-preview'})
#         print(f'{len(articles)} articles on page {page_num} {url}')
#         for a in articles:
#             post_id = a['data-id']
#             img_url, tag_info, post_url = self.get_post(post_id)
#             post = {
#                 'post_url':post_url,
#                 'img_url':img_url,
#                 'tag_info':tag_info
#             }
#             self.posts.append(post)
#             # self.executor2.submit(self.dl_post,post)
#             # self.dl_post(post)
#         # self.progress_query_page+=1
#         # print(f"Done querying page {page_num},({self.progress_query_page}/{self.task_query_page})")
#
#     # input tags, save posts in object
#     def process_query(self,tags):
#         head = 'https://danbooru.donmai.us/posts?tags='
#         self.query_tags = tags
#         if type(tags) == str:
#             result = head + tags
#         elif type(tags) == list:
#             result = head
#             for tag in tags:
#                 result += tag + "+"
#         else:
#             return None
#         print('Query url:',result)
#         self.query_url = result
#
#         if not self.max_page:
#             content = rq.get(result).content
#             soup = bs(content,'html.parser')
#             max_page = soup.find_all('a', {'class': 'paginator-page'})
#             max_page = max_page[ len(max_page)-1 ]
#             print("Max page:", max_page.getText())
#             self.max_page =min(1000,int(max_page.getText()))
#
#     # get PIL images from
#     def get_preview_img(self):
#         dl_img = self.dl_img
#         dl_info = self.dl_info
#         self.dl_img = False
#         self.dl_info = False
#         self.query_page( random.randint(1,min(self.max_page,1000) ))
#         imgs = []
#         for post in self.posts:
#             img_url = post['img_url']
#             if img_url:
#                 content = rq.get(img_url).content
#                 imgs.append(Image.open( BytesIO(content) ))
#         self.posts.clear()
#         # clear posts
#         self.dl_img = dl_img
#         self.dl_info = dl_info
#         return imgs
#     def query(self,tags):
#         self.process_query(tags)
#         result = self.query_url
#         # print(self.query_url)
#         content = rq.get(result).content
#         soup = bs(content, 'html.parser')
#         # print(soup.prettify())
#         articles = soup.find_all(name='article', attrs={'class': 'post-preview'})
#         # print(len(articles))
#         max_page = soup.find_all('a', {'class': 'paginator-page'})
#         max_page = max_page[len(max_page) - 1]
#         print("Max page:", max_page.getText())
#         self.max_page = int(max_page.getText())
#         self.task_query_page = min(self.max_page,1000)
#         query_page_tasks = []
#         dl_post_tasks = []
#         for i in range(self.task_query_page):
#             query_page_task = self.executor.submit(self.query_page,i)
#             query_page_tasks.append(query_page_task)
#         for t in as_completed(query_page_tasks):
#             self.progress_query_page+=1
#             print(f'Done querying page {self.progress_query_page}/{self.max_page}')
#         print(f'Number of post:{len(self.posts)}')
#         return
#         for post in self.posts:
#             dl_post_task = self.executor.submit(self.dl_post,post)
#             dl_post_tasks.append(dl_post_task)
#         for t in as_completed(dl_post_tasks):
#             self.progress_dl_post+=1
#             print(f'Done downloading post {self.progress_dl_post}/{self.max_post}')
#
#         # self.dl_all_post()
#         print('Finished downloading all posts')
#
#         return result
#
#
#
# # def dl(img_url:str):
# #
# #     if not os.path.exists('images'):
# #         os.makedirs('images')
# #     content = rq.get(img_url).content
# #     fname = img_url[ img_url.rfind('/')+1:]
# #     with open( os.path.join('images',fname),'wb') as f:
# #         f.write(content)
# #
# # def get_img_url_from_post(post_id):
# #     head = 'https://danbooru.donmai.us/posts/'
# #     url = head+post_id
# #     print(url)
# #     content = rq.get(url).content
# #     soup = bs(content,'lxml')
# #     # get post info
# #     sidebar = soup.select_one('#sidebar')
# #     # print(len(sidebar.children))
# #     children = sidebar.find_all(recursive=False)
# #     # for c in children:
# #     #     print(c)
# #     taglist = sidebar.select_one('#tag-list')
# #     tag_info = {
# #         'artist':[],
# #         'copyright':[],
# #         'character':[],
# #         'general':[],
# #     }
# #     for key in tag_info.keys():
# #         ul = taglist.select_one(f'ul.{key}-tag-list')
# #         for li in ul.find_all(recursive=False):
# #             a = li.select_one('a.search-tag')
# #             text = a.get_text()
# #             tag_info[key].append(text)
# #     print('Info:')
# #     for key in tag_info.keys():
# #         print("---------------"+key+":"+"--------------------")
# #         for tag in tag_info[key]:
# #             print(tag)
# #
# #
# #     # get image src
# #     target = soup.find(name='section',attrs={'class':'image-container'})
# #     # print(target)
# #     img = target.select_one('picture img')
# #     print(img['src'])
# #     src = img['src']
# #     return src,tag_info
# # def search(tags):
# #     head = 'https://danbooru.donmai.us/posts?tags='
# #     if type(tags)==str:
# #         result = head+tags
# #     elif type(tags) == list:
# #         result = head
# #         for tag in tags:
# #             result += tag+"+"
# #     else: return None
# #     print(result)
# #     content = rq.get(result).content
# #     soup = bs(content,'lxml')
# #     # print(soup.prettify())
# #     # with open('vis.html','wb') as f:
# #     #     f.write(content)
# #     selector = "article.post-preview"
# #     articles = soup.find_all(name='article',attrs={'class':'post-preview'} )
# #     print(len(articles))
# #     for a in articles:
# #         post_id = a['data-id']
# #         img_url,tag_info = get_img_url_from_post(post_id)
# #         # exit(0)
# #         # dl(img_url)
# #         # exit(0)
# #         # print(a['data-id'])
# #     return result
#
# # downloader = DanbooruDownloader()
# # tags = ['bangs','feet']
# # downloader.dl_img = False
# # downloader.dl_info = True
# # downloader.query(tags)
# # print(len(downloader.posts))
# # downloader.dl_all_post()
#
# downloader = DanbooruDownloader()
#
# def preview(tags_str:str):
#     tags = tags_str.split(sep=',')
#     print(f'Got {len(tags)} tags:{tags}')
#     downloader.process_query(tags)
#     print(downloader.query_url)
#     imgs = downloader.get_preview_img()
#     return downloader.query_url,imgs
# def update_dl_config(input):
#     print(input)
#     downloader.dl_img = 'Download Image' in input
#     downloader.dl_info = 'Download Tags' in input
# def update_max_post(input):
#     print(input)
#     downloader.max_post = input
# def interface():
#     with gradio.Blocks() as demo:
#         with gradio.Row():
#             tags_input = gr.Textbox(placeholder="Search Danbooru Tags",
#                                     label="Tags(split by ',')")
#             preview_url = gr.Textbox(interactive=False,label = "Preview URL",value="None")
#             get_url = gr.Button(value="Get Preview" )
#         with gr.Row():
#             configs = gr.CheckboxGroup( ['Download Image','Download Tags'])
#             configs.change(fn=update_dl_config,inputs=configs)
#         with gr.Row():
#             max_post = gr.Number(value=downloader.max_post, label="Max amount of downloaded posts")
#             max_post.change(fn=update_max_post,inputs = max_post)
#         with gr.Row():
#             preview_gallery = gr.Gallery(value=None,label ="Gallery Preview")
#             preview_gallery.style(grid=4,container=True)
#
#         with gradio.Row():
#             submit_btn = gr.Button(value="Submit")
#             # submit_btn.click(fn=test_fn,inputs = tags_input,outputs = preview_url)
#         get_url.click(fn=preview, inputs=tags_input, outputs=[preview_url,preview_gallery])
#         submit_btn.click(fn = downloader.query,inputs = tags_input )
#     demo.launch(server_port=9000)
#
# interface()
# # res = search()
# # print(res)
#
#
#
# # with gr.Blocks() as interface:
# #     with gr.Row():
# #         search_term = gr.Textbox()
# #         lb = gr.Label()
# #     submit_btn = gr.Button()
# #     submit_btn.click(fn = test_fn,inputs = search_term,outputs =lb )
# # interface.launch()