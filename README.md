# gradio-danbooru-downloader
This tiny project is a data scraping tool inspired by [AUTOMATIC 111'S Stable Diffusion Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui/). 
It's always a huge pain to manually annotate individual images when preparing training datasets for Stable Diffusion. Even though users can use [deepdanbooru](https://github.com/KichangKim/DeepDanbooru/tree/master/deepdanbooru)
to automate the process,it has poor performance on recognizing complicated illustrations and can mislabel the dataset, which can cause failure in training models.
This project aims to utilize the existing tagging system on mainstream boorus to get **accurate, manually-annotated, high quality dataset**.  
This tool allow users to scrape famous boorus with tag systems including  
 - [Danbooru](https://danbooru.donmai.us)
 - [Yande.re](https://yande.re/post)
 - [Sankaku Complex](https://beta.sankakucomplex.com/)  
   
 with both images and tags txt file ready to be trained on (WARNING:All of the links contain **NSFW** content, **open at your own risk**).  
 # How to use  
 1. Clone this repository ```git clone git@github.com:SoulflareRC/gradio-danbooru-downloader.git```
 2. Enter the directory ```cd gradio-danbooru-downloader```
 3. Run ui.py ```python ui.py```
 4. Wait till gradio launches, go to http://127.0.0.1:8001/ in your browser
