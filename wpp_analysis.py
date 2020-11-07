import re
import regex
import pandas as pd
import numpy as np
import emoji
import plotly
import plotly.express as px
import matplotlib.pyplot as plt
from os import path

def starts_with_date_time(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+)[ ]([0-9]+):([0-9]+)[ ]-'
    result = re.match(pattern, s)
    if result:
        return True
    return False

def has_author(s):
  s=s.split(":")
  if len(s) > 1:
    return True
  else:
    return False

def split_count(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            emoji_list.append(word)
    return emoji_list

def get_data_point(line):
    split_l = line.split(' - ')
    date_time = split_l[0]
    date, time = date_time.split(' ')
    message = ' '.join(split_l[1:])
    if has_author(message):
        split_msg = message.split(': ')
        author = split_msg[0]
        message = ' '.join(split_msg[1:])
    else:
        author = None
    return date, time, author, message

parsed = []
path = './input/wpp_input.txt'
with open(path, encoding="utf-8") as fp:
    fp.readline()
    msg_buffer = []
    date, time, author = None, None, None
    while True:
        line = fp.readline()
        if not line:
            break
        line = line.strip()
        if starts_with_date_time(line):
            if len(msg_buffer) > 0:
                parsed.append([date, time, author, ' '.join(msg_buffer)])
            msg_buffer.clear()
            date, time, author, message = get_data_point(line)
            msg_buffer.append(message)
        else:
            msg_buffer.append(line)

df = pd.DataFrame(parsed, columns=['date', 'time', 'author', 'message'])
df["date"] = pd.to_datetime(df["date"])

anon = df.copy()
anon = anon.dropna()
authors = anon.author.unique()

anon.author = anon.author.apply(lambda author: 'Author ' + str(np.where(authors == author)[0][0] + 1))
authors = anon.author.unique()

media_msgs = anon[anon['message'] == '<Arquivo de mídia oculto>']
text_msgs = anon.drop(media_msgs.index)
text_msgs['word_count'] = text_msgs['message'].apply(lambda s : len(s.split(' ')))
text_msgs["emoji"] = anon["message"].apply(split_count)
text_msgs['urlcount'] = text_msgs.message.apply(lambda x: re.findall(r'(https?://\S+)', x)).str.len()
text_msgs['greetings'] = anon.message.apply(lambda msg: True if re.match('([B|b]om dia)|([B|b]oa tarde)|([B|b]oa noite)', msg) else False)

author_group = text_msgs.groupby("author").sum()
author_group.reset_index(inplace=True)
fig = px.bar(author_group, y="author", x="greetings", color="author", color_discrete_sequence=["red", "green", "blue", "goldenrod", "magenta"])

plotly.offline.plot(fig, filename='output/wpp_analysis.html')
