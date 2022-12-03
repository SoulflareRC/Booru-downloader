import json
from SearchEngine import *
import gradio
import gradio as gr
import html

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
from Post import Post
from Query import Query
from DanbooruDownloader import DanbooruDownloader
downloader = DanbooruDownloader()
score_filter = 0
ddict = SearchEngineBase('dictionary/danbooru_tags.txt')
taglist_all = ddict.taglist.copy()

num_tags_per_page = 100
def update_tags_by_page(page_num: int):
    global taglist_all
    print(f'Jump to page {page_num}')
    print(f'all tag in page {taglist_all[:10]}')
    tags_list = taglist_all[int((page_num - 1) * num_tags_per_page):
                            int(min(len(taglist_all), page_num * num_tags_per_page))]
    print(tags_list[:10])
    print(len(tags_list))
    while len(tags_list) < num_tags_per_page:
        tags_list.append("")
    return tags_list

def update_tags_by_search(keyword):
    global  taglist_all
    taglist_all = ddict.search_in_tag(keyword)
    print(f'Found {len(taglist_all)} results')
    print(taglist_all[:10])
    return update_tags_by_page(1)

def tags_to_link(tags):
    head = 'https://danbooru.donmai.us/posts?tags='
    result = head
    for tag in tags:
        result += tag + "+"
def preview(tags_str:str):
    tags = tags_str.split(sep=',')
    print(f'Got {len(tags)} tags:{tags}')
    q = Query(tags)
    q.score_filter = score_filter
    print(q.query_url)
    imgs = q.get_preview_img()
    return f'<a target="_blank" href = "{q.query_url}">{q.query_url}</a>',imgs
def update_dl_config(input):
    print(input)
    downloader.dl_img = 'Download Image' in input
    downloader.dl_info = 'Download Tags' in input
def update_max_page(input):
    print(input)
    downloader.max_pages = input
def update_score_filter(input):
    print("Set score filter to:",input)
    score_filter = input
    downloader.score_filter = score_filter
def interface():
    # declare outside of interface, render inside when use
    img_input = gr.Image(label="Upload image")
    pred_result = gr.Label(value=None, label="Result")
    with gr.Blocks() as demo:
        with gr.Tab("Query and Download"):
            with gr.Row():
                tags_input = gr.Textbox(placeholder="Search Danbooru Tags",
                                        label="Tags(split by ',')")
                score_threshold = gr.Number(value=0,label = "Score filter(enabled when set to a positive number)")
                score_threshold.change(fn = update_score_filter,inputs = score_threshold)
                preview_url = gr.HTML(interactive=False,label = "Preview URL",value="None")
                get_url = gr.Button(value="Get Preview" )
            with gr.Row():
                configs = gr.CheckboxGroup( ['Download Image','Download Tags'])
                configs.change(fn=update_dl_config,inputs=configs)
            with gr.Row():
                max_page = gr.Number(value=downloader.max_pages, label="Max amount of downloaded pages")
                max_page.change(fn=update_max_page,inputs = max_page)

            with gr.Row():
                # img = gr.Image(value = "test/__konjiki_no_yami_to_love_ru__a34eed7ba8e96d80cb45273510a02757.jpg")
                preview_gallery = gr.Gallery(value=None,label ="Gallery Preview")
                preview_gallery.style(grid=4,container=True)
                # preview_gallery.
            with gr.Row():
                submit_btn = gr.Button(value="Submit")
                # submit_btn.click(fn=test_fn,inputs = tags_input,outputs = preview_url)
            tags_input.submit(fn=preview, inputs=tags_input, outputs=[preview_url,preview_gallery])
            get_url.click(fn=preview, inputs=tags_input, outputs=[preview_url,preview_gallery])
            submit_btn.click(fn = downloader.dl_query,inputs = tags_input )


        with gr.Tab("Danbooru tags dictionary"):
            with gr.Row():
                search_box = gr.Textbox(label = "Search danbooru tag",placeholder="Search if tag exists...")
                # test_unrender = gr.Button(value="Unrender")
            with gr.Row():
                tags_list = taglist_all[:num_tags_per_page]
                tags_display = []
                for tag in tags_list:

                    display = gr.Textbox(value = tag,interactive=False,show_label=False)
                    tags_display.append(display)
                page_tags = gr.Number(value = 1,label="Showing Page",interactive=True)
                page_tags.submit(fn = update_tags_by_page,inputs = page_tags,outputs=tags_display)
                search_box.submit(fn = update_tags_by_search,inputs=search_box,outputs=tags_display)

                # col = 10
                # taglist = [ ddict.taglist[i:i+col] for i in range(0,len(ddict.taglist),col) ]
            with gr.Row():
                gr.HTML('<a href ="https://danbooru.donmai.us/posts?tags=barefoot+&z=5" >https://danbooru.donmai.us/posts?tags=barefoot+&z=5</a>',)

            # def update_tags_display():
            #     tags_display.unrender()
            #     for child in tags_display.children:
            #         print(child)
            # test_unrender.click(fn =update_tags_display)
        with gr.Tab("Deepdanbooru"):
            with gr.Row():
                img_input.render()
                pred_result.render()

    demo.launch(server_port=9000)
# gradio.close_all()
interface()