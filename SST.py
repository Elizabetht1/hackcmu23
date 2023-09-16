#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##libraries for SST
import whisper
##requires brew install ffmpeg
##requires pip install -U openai-whisper


#import general libraries 
import os, glob
import pandas as pd
import re 
import json


##get audio file and transicrbe into speech to text

def transcribe(file_path,model):
    ##requires file_path is a file path 
    ##ensures \result is
    save_json("./SST_output.json",model.transcribe(file_path))

def save_json(destination_path,content):
    save_file = open(destination_path, "w")  
    json.dump(content, save_file, indent = 6)  
    save_file.close()  

def main():
    model = whisper.load_model("base.en")
    transcribe(fp,m)


# In[1]:


import sys
sys.executable


# In[ ]:





# In[ ]:




