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

def find_author(s):
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

def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(' ')
    message = ' '.join(splitLine[1:])
    if find_author(message):
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
            date, time, author, message = getDataPoint(line)
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

media_messages = anon[anon['message'] == '<Arquivo de mídia oculto>']
chat_messages = anon.drop(media_messages.index)
chat_messages['word_count'] = chat_messages['message'].apply(lambda s : len(s.split(' ')))
chat_messages["emoji"] = anon["message"].apply(split_count)
chat_messages['urlcount'] = chat_messages.message.apply(lambda x: re.findall(r'(https?://\S+)', x)).str.len()
chat_messages['greetings'] = anon.message.apply(lambda msg: True if re.match('([B|b]om dia)|([B|b]oa tarde)|([B|b]oa noite)', msg) else False)

auth = chat_messages.groupby("author").sum()
auth.reset_index(inplace=True)
fig = px.bar(auth, y="author", x="greetings", color="author", color_discrete_sequence=["red", "green", "blue", "goldenrod", "magenta"])

plotly.offline.plot(fig, filename='output/wpp_analysis.html')
