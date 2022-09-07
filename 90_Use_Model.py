#!/usr/bin/env python
# coding: utf-8

# # Finetuning RoBERTa for NER: Use Model
#  

# ***

# ## Imports

# In[1]:


from transformers import (BertTokenizerFast,
                          RobertaTokenizerFast,
                          AutoTokenizer,
                          BertForTokenClassification,
                          RobertaForTokenClassification,
                          DataCollatorForTokenClassification, 
                          AutoModelForTokenClassification, 
                          TrainingArguments, Trainer)
from datasets import load_dataset, load_metric, concatenate_datasets, DatasetDict
from pprint import pprint
import numpy as np
import pickle
import torch
import os


# ## Load Dataset

# In[2]:


data_path = "./data/dataset_processed.pkl"
with open(data_path, 'rb') as pickle_file:
    dataset = pickle.load(file=pickle_file)


# ## Load Model and Tokenizer

# Information about model variants can be found here: https://huggingface.co/docs/transformers/model_doc/roberta

# In[3]:


import gc
gc.collect()
torch.cuda.empty_cache()


# In[4]:


label_list = dataset["train"].features[f"ner_tags"].feature.names


# In[5]:


model_name = "xlm-roberta-large" #"bert-base-multilingual-cased" #xlm-roberta-large
tokenizer = AutoTokenizer.from_pretrained(f"{model_name}", add_prefix_space=True) #AutoTokenizer(use_fast = True)
#model = AutoModelForTokenClassification.from_pretrained(f"{model_name}")


# ## Use Fine-tuned Model:

# Load checkpoint:

# In[6]:


model_tuned = AutoModelForTokenClassification.from_pretrained("./results/checkpoint-final/")


# In[7]:


model_tuned.config


# Set correct class labels:

# In[8]:


# label_names = dataset["train"].features[f"ner_tags"].feature.names

# id2label = {id : label for id, label in enumerate(label_names)}
# label2id = {label: id for id, label in enumerate(label_names)}

# model_tuned.config.id2label = id2label
# model_tuned.config.label2id = label2id


# In[9]:


model_tuned.config.id2label


# In[10]:


#predictions, labels, _ = model_tuned. .predict(dataset["test"])


# In[47]:


def printPrediction(inputs, predictions, tokenizer):
    token_ids = list(inputs["input_ids"][0])
    tokens_classes = predictions
    #results = []

    for token_id, token_class in zip(token_ids, tokens_classes): 

        token_text = tokenizer.decode(int(token_id))
        #print(int(token_id),"\t", token_text,"\t", token_class)
        print("{: >10} {: >10} {: >10}".format(int(token_id), token_text, token_class))
        #results.append((int(token_id), token_text, token_class))


# In[48]:


text = "Für Richard Phillips Feynman war es immer wichtig in New York, die unanschaulichen Gesetzmäßigkeiten der Quantenphysik Laien und Studenten nahezubringen und verständlich zu machen."

inputs = tokenizer(
    text, 
    add_special_tokens=False, return_tensors="pt"
)

with torch.no_grad():
    logits = model_tuned(**inputs).logits

predicted_token_class_ids = logits.argmax(-1)

# Note that tokens are classified rather then input words which means that
# there might be more predicted token classes than words.
# Multiple token classes might account for the same word
predicted_tokens_classes = [model_tuned.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

printPrediction(inputs, predicted_tokens_classes, tokenizer)


# In[49]:


text = "In December 1903 in France the Royal Swedish Academy of Sciences awarded Pierre Curie, Marie Curie, and Henri Becquerel the Nobel Prize in Physics"

inputs = tokenizer(
    text, 
    add_special_tokens=False, return_tensors="pt"
)

with torch.no_grad():
    logits = model_tuned(**inputs).logits

predicted_token_class_ids = logits.argmax(-1)

# Note that tokens are classified rather then input words which means that
# there might be more predicted token classes than words.
# Multiple token classes might account for the same word
predicted_tokens_classes = [model_tuned.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

printPrediction(inputs, predicted_tokens_classes, tokenizer)

