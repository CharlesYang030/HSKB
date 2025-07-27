import json
import os.path
from tqdm import tqdm
import pandas as pd
import re


#中文句子分句
def split_sentences(text):
    # 定义分句的正则表达式
    pattern = r'([^。！？…]*[。！？…]+)'

    # 使用re.findall()方法找到所有匹配的句子
    sentences = re.findall(pattern, text)
    if len(sentences) > 1:
        return sentences
    else:
        return [text]

def grammar_sft_fn(data,outdir):
    grammar_points = pd.read_excel('utils/目标语法项目_拆分.xlsx',sheet_name=None)
    grammar_points_dict = {
        '3级': [],
        '4级': [],
        '5级': [],
        '6级': [],
        '高等': [],
    }
    for level, df in grammar_points.items():
        for i in range(len(df)):
            no = df.loc[i, 'No.']
            level = df.loc[i, '级别']
            yufaxiangmu = df.loc[i, '语法项目']
            leibie = df.loc[i, '类别']
            ximu = df.loc[i, '细目']
            yufaneirong = df.loc[i, '语法内容']

            instruction = f'你是一个HSK语法点检测器，请你对以下句子进行判断是否符合当前语法点：No:{no}, 级别:{level}, 语法项目:{yufaxiangmu}, 类别:{leibie}, 细目:{ximu}, 语法内容:{yufaneirong}。'
            grammar_points_dict[level].append(instruction)

    grammar_detection_data = []
    for d in tqdm(data,desc='形成 语法点检测 数据...'):
        essay_chunks = d['predict'].split('\n')
        essay_chunks = [chunk for chunk in essay_chunks if chunk!='']
        sentences = []
        for chunk in essay_chunks:
            sentences += split_sentences(chunk)

        ## 逐条句子形成3-6级语法点检测数据
        for sent in sentences:
            for level, grammar_list in grammar_points_dict.items():
                for gram_instruction in grammar_list:
                    temp_dict = {
                        'instruction': gram_instruction,
                        'input': f'句子：{sent}',
                        'output': ''
                    }
                    grammar_detection_data.append(temp_dict)

    outfile = os.path.join(outdir,'_'.join(outdir.split('/')[-2:])+'_grammar_detection.json')
    with open(outfile,'w',encoding='utf-8') as f:
        json.dump(grammar_detection_data,f,indent=3,ensure_ascii=False)

    print('语法点检测数据已生成，个数：',len(grammar_detection_data))

def error_correction_AND_grade_fn(data,outdir):
    correction_data = []
    grade_data = []
    for d in tqdm(data,desc='形成 纠错 数据...'):
        title = d['prompt'].split('《')[-1].split('》')[0]
        essay = d['predict']

        temp_dict = {
            'instruction': '你是一个HSK作文纠错器，请你对以下作文进行纠错：',
            'input': f'原始作文：{essay}',
            'output': ''
        }
        correction_data.append(temp_dict)

        temp_dict_grade = {
            'instruction': f'你是一个HSK作文评分器，请你对以下作文（题目为：《{title}》）进行评分：',
            'input': f'原始作文：{essay}',
            'output': ''
        }
        grade_data.append(temp_dict_grade)

    outfile = os.path.join(outdir, '_'.join(outdir.split('/')[-2:]) + '_error_correction.json')
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(correction_data, f, indent=3, ensure_ascii=False)

    print('纠错数据已生成，个数：', len(correction_data))

    outfile_grade = os.path.join(outdir, '_'.join(outdir.split('/')[-2:]) + '_grade_assessment.json')
    with open(outfile_grade, 'w', encoding='utf-8') as f:
        json.dump(grade_data, f, indent=3, ensure_ascii=False)

    print('评分数据已生成，个数：', len(grade_data))


if __name__ == '__main__':

    file = '1.模型的作文产出/case/case.jsonl'
    file = open(file, 'r', encoding='utf-8')

    outdir = '2.形成各类sft数据/case'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    data = [json.loads(line) for line in file]

    print(outdir)
    grammar_sft_fn(data,outdir)  ## 语法点检测sft
    error_correction_AND_grade_fn(data,outdir) ## 作文纠错和评分sft
