import json
import os
import re
import tiktoken

root = 'pretrain-data'
cls_dir = os.listdir(root)


# file3 = json.load(open('pretraining_data_3.json','r',encoding='utf-8'))
# file4 = json.load(open('pretraining_data_4.json','r',encoding='utf-8'))
# file5 = json.load(open('pretraining_data_5.json','r',encoding='utf-8'))
# file6 = json.load(open('pretraining_data_6.json','r',encoding='utf-8'))
enc = tiktoken.encoding_for_model("gpt-4-0314")
# token_3 = len(enc.encode(str(file3)))
# token_4 = len(enc.encode(str(file4)))
# token_5 = len(enc.encode(str(file5)))
# token_6 = len(enc.encode(str(file6)))
# print()


# 中文句子分句
def split_sentences(text):
    # 定义分句的正则表达式
    pattern = r'([^。！？…]*[。！？…]+)'

    # 使用re.findall()方法找到所有匹配的句子
    sentences = re.findall(pattern, text)

    return sentences

cls_token_dict = {}
cls_sent_dict = {}
for cls in cls_dir:
    cls_path = os.path.join(root,cls)
    filelist = os.listdir(cls_path)

    cls_sentences_record = []
    cls_tokens = 0
    for file in filelist:
        file_path = os.path.join(cls_path,file)
        content = open(file_path,'r',encoding='utf-8').read()

        file_tokens = len(enc.encode(content))
        cls_tokens += file_tokens

        sentences = split_sentences(content)

        print(file_tokens)

        for sent in sentences:
            cls_sentences_record.append(
                {
                    'text': sent
                }
            )
    cls_token_dict[cls] = cls_tokens
    cls_sent_dict[cls] = cls_sentences_record
    print('####',cls,cls_tokens)
    # outpath = f'pretraining_data_{cls}.json'
    # with open(outpath,'w',encoding='utf-8') as f:
    #     json.dump(cls_sentences_record,f,ensure_ascii=False)


print()