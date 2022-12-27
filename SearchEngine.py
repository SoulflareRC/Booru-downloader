import os
import re

class SearchEngineBase(object):
    def __init__(self,data_path):
        print('Initializing search engine')
        with open(data_path,'r') as f:
            taglist = [ line.rstrip() for line in f]
        print(taglist[:10])
        print(f'Done reading dictionary. {len(taglist)} tags loaded.')
        self.taglist = taglist
    def search_in_tag(self,input:str):
        return [ tag for tag in self.taglist if tag.find(input)>=0 ]



