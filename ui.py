import base64
import io
import json
import tempfile

import gradio
import gradio as gr
import html
import shutil
import requests as rq
from bs4 import BeautifulSoup as bs
import os
import numpy as np
from PIL import Image
from io import BytesIO
import random
import threading as tr
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import *
from Post import *
from Query import *
import deepdanbooru_onnx as dd
from io import StringIO
from SearchEngine import SearchEngineBase
class gradio_ui(object):
    def __init__(self):
        self.mode = "Danbooru"
        # ['Danbooru', 'yande.re']
        # download config
        self.score_filter = 0.6
        self.dl_img = True
        self.dl_info = False
        self.max_pages = 1000
        self.d = dd.DeepDanbooru()
        self.seb = SearchEngineBase('dictionary/danbooru_tags.txt')
        self.taglist_all = self.seb.taglist
        self.num_tags_per_page = 100
    def update_tags_by_page(self,page_num: int):
        print(f'Jump to page {page_num}')
        print(f'all tag in page {self.taglist_all[:10]}')
        tags_list = self.taglist_all[int((page_num - 1) * self.num_tags_per_page):
                                int(min(len(self.taglist_all), page_num * self.num_tags_per_page))]
        print(tags_list[:10])
        print(len(tags_list))
        while len(tags_list) < self.num_tags_per_page:
            tags_list.append("")
        return tags_list
    def update_tags_by_search(self,keyword):
        self.taglist_all = self.ddict.search_in_tag(keyword)
        print(f'Found {len(self.taglist_all)} results')
        print(self.taglist_all[:10])
        return self.update_tags_by_page(1)
    def dl_query(self, tags, max_pages=1000):
        print('DL query')
        tags = tags.split(sep=',')
        print(f'Got {len(tags)} tags:{tags}, Max Pages set to {max_pages}')
        if self.mode == "Danbooru":
            q = Query_Danbooru(tags)
        elif self.mode == "yande.re":
            q = Query_Yandere(tags)
        elif self.mode == "Sankaku":
            q = Query_Sankaku(tags)
            # q.base_dir = 'Sankaku-test'
        print(f'Querying {self.mode}')

        q.score_filter = self.score_filter
        q.dl_img = self.dl_img
        q.dl_info = self.dl_info
        q.max_page = min( int(max_pages),q.max_page)
        print(f'Max page from ui:{q.max_page}')
        # q.dl_when_query = True
        q.query_all()
        q.dl_all_posts()
        # print(len(q.posts))
        # base_dir = os.path.join("images", str(tags))
        # dl_tasks = []
        # progress = 0
        # progress_todo = len(q.posts)
        # for post in q.posts:
        #     dl_task = self.executor.submit(post.dl_post, base_dir, self.dl_img, self.dl_info)
        #     dl_tasks.append(dl_task)
        # for t in as_completed(dl_tasks):
        #     progress += 1
        message =f'Finished downloading {len(q.posts)} posts!Results saved to {q.base_dir}'
        print(message)

    def preview(self, tags_str: str):
        tags = tags_str.split(sep=',')
        print(f'Got {len(tags)} tags:{tags}')
        if self.mode == "Danbooru":
            q = Query_Danbooru(tags)
        elif self.mode == "yande.re":
            q = Query_Yandere(tags)
        elif self.mode == "Sankaku":
            q = Query_Sankaku(tags)
        print(q.max_page)
        q.score_filter = self.score_filter
        print(q.query_url)
        imgs = q.get_preview_img()
        print('Images:',imgs)
        return f'<a target="_blank" href = "{q.query_url}">{q.query_url}</a>', imgs
    def update_downloader_config(self,mode_input,score_threshold,dl_config_input,max_page_input):
        print(mode_input)
        print(score_threshold)
        print(dl_config_input)
        print(max_page_input)

        self.mode = mode_input
        self.score_filter = score_threshold
        self.dl_img = 'Download Image' in dl_config_input
        self.dl_info = 'Download Tags' in dl_config_input
        self.max_pages = max_page_input
        return gr.Textbox.update(placeholder=f"Search {self.mode} Tags"
                                 # ,label="Tags(split by ',')"
                                 )
    def deepdanbooru_predict(self,img_input,save_result,threshold = 0.6):
        print('Save result ',save_result)
        self.d.threshold = threshold
        print(self.d.threshold)
        print(type(img_input))
        res_dict_html = ""

        temp = "temp/images"
        if os.path.exists(temp):
            shutil.rmtree(temp)
        os.makedirs(temp)

        result_txt_dir = "deepdanbooru/results"
        if not os.path.exists(result_txt_dir):
            os.makedirs(result_txt_dir)
        tags = ""
        if type(img_input)==list:
            for img in img_input:
                img_name = img.name[ str(img.name).rfind('\\')+1: ]
                img = Image.open(img)
                temp_path = os.path.join(temp,img_name)
                print(temp_path)
                img.save(temp_path)
                img = dd.process_image(img)
                res_dict = self.d(img)
                res_dict = {k: v.item() for k, v in res_dict.items()}
                img_html = f"<img src='file/{temp_path}'/>"
                res_dict_html+=img_html+"<br>"
                sorted_items = sorted(res_dict.items(),key=lambda item:item[1],reverse=True)
                for k,v in sorted_items:
                    wiki_link = f'https://danbooru.donmai.us/wiki_pages/{k}'
                    label_html = f'<strong><a target="_blank" href="{wiki_link}">{k}</a></strong>' \
                                 f'<span style="position:absolute;right:0px;" > { round(v,2)} </span><br>'
                    res_dict_html+=label_html
                    tags+=k+","
                res_dict_html+="<hr>"
                if save_result:
                    txt_path = os.path.join(result_txt_dir,img_name[ :str(img_name).rfind(".") ]+".txt")
                    with open(txt_path,'w') as f:
                        f.write(tags)
        return res_dict_html

    def test_change(self,deepdanbooru_mode):
        print(deepdanbooru_mode)
        return gr.Textbox().update(value=deepdanbooru_mode)

    def interface(self):
        mode_list = gr.Dropdown(['Danbooru', 'yande.re','Sankaku'],label="Booru",value=self.mode)

        tags_input = gr.Textbox(placeholder=f"Search {self.mode} Tags",
                                                label="Tags(split by ',')")
        score_threshold = gr.Number(value=0, label="Score filter(enabled when set to a positive number)")

        preview_url = gr.HTML(interactive=False, label="Preview URL", value="None")
        get_preview = gr.Button(value="Get Preview")
        configs = gr.CheckboxGroup(['Download Image', 'Download Tags'],label='Download Options')

        max_page = gr.Number(value=self.max_pages, label="Max amount of downloaded pages")

        preview_gallery = gr.Gallery(value=None, label="Gallery Preview")
        preview_gallery.style(grid=4, container=True)
        submit_btn = gr.Button(value="Submit")


        # tag knowledge base
        search_box = gr.Textbox(label = "Search danbooru tag",placeholder="Search if tag exists...")
        tags_list = self.taglist_all[:self.num_tags_per_page]
        tags_display = []
        for tag in tags_list:
            display = gr.Textbox(value=tag, interactive=False, show_label=False)
            tags_display.append(display)
        page_tags = gr.Number(value=1, label="Showing Page", interactive=True)

        # deepdanbooru
        deepdanbooru_mode = gr.Dropdown(choices=["single image",'batch files'],value = "single image",interactive=True)
        test_text = gr.Textbox(value = "Test",interactive=True)
        # img_input = gr.Image(label="Upload image")
        img_input = gr.File(label="Upload image",file_count="multiple")
        deepdanbooru_threshold = gr.Number(value = 0.6,label="Threshold (probability score of a tag)")
        pred_result = gr.HTML(value=None, label="Result")
        save_result = gr.Checkbox(label="Save as txt")
        deepdanbooru_submit = gr.Button(value = "Predict!")


        with gr.Blocks() as demo:
            with gr.Row():
                mode_list.render()
            with gr.Tab("Booru-dl"):
                with gr.Tab("Query and Download"):
                    with gr.Row():
                        tags_input.render()
                        score_threshold.render()
                        preview_url.render()
                        get_preview.render()
                    with gr.Row():
                        configs.render()
                    with gr.Row():
                        max_page.render()
                    with gr.Row():
                        preview_gallery.render()
                    with gr.Row():
                        submit_btn.render()
            with gr.Tab('Deepdanbooru'):
                # with gr.Row():
                #     deepdanbooru_mode.render()
                #     test_text.render()
                with gr.Column():
                    img_input.render()
                    deepdanbooru_threshold.render()
                    deepdanbooru_submit.render()
                    save_result.render()
                    pred_result.render()

            score_threshold.change(fn=self.update_downloader_config, inputs=[mode_list,score_threshold, configs, max_page],outputs=[tags_input])
            max_page.change(fn=self.update_downloader_config, inputs=[mode_list,score_threshold, configs, max_page],outputs=[tags_input])
            configs.change(fn=self.update_downloader_config, inputs=[mode_list,score_threshold, configs, max_page],outputs=[tags_input])
            mode_list.change(fn=self.update_downloader_config, inputs=[mode_list,score_threshold, configs, max_page],outputs=[tags_input])
            get_preview.click(fn = self.preview,inputs = tags_input,outputs = [preview_url,preview_gallery])
            submit_btn.click(fn = self.dl_query,inputs = [tags_input,max_page])
            deepdanbooru_submit.click(fn=self.deepdanbooru_predict,
                                  inputs=[img_input, save_result, deepdanbooru_threshold],
                                  outputs=pred_result)
            deepdanbooru_mode.change(fn=self.test_change,inputs = deepdanbooru_mode, outputs=test_text)
            page_tags.submit(fn=self.update_tags_by_page, inputs=page_tags, outputs=tags_display)
            search_box.submit(fn=self.update_tags_by_search, inputs=search_box, outputs=tags_display)

        demo.launch(server_port=8001)
g = gradio_ui()
g.interface()




