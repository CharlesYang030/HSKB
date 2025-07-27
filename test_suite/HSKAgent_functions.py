import pandas as pd
import json
import re
from tqdm import tqdm
import os
from utils.error_detection import performAllRules
from utils.ltp_linguistic_metrics import ltp_fn,calculate_linguistic_metrics_fn

def evaluate_grammar_fn(target_dir):
    file = os.path.join(target_dir,'grammar_detection/generated_predictions.jsonl')
    file = open(file,'r',encoding='utf-8')

    data = [json.loads(line) for line in file]

    result_dict = {
        '3级': 0,
        '4级': 0,
        '5级': 0,
        '6级': 0,
        '高等': 0
    }

    for d in data:
        prompt = d['prompt']
        predict = d['predict'].strip().replace('<think>\n\n</think>\n\n', '')

        yufadian = prompt.split('\n')[1]

        if predict == '是':
            if '级别:3级' in yufadian:
                result_dict['3级'] += 1
            elif '级别:4级' in yufadian:
                result_dict['4级'] += 1
            elif '级别:5级' in yufadian:
                result_dict['5级'] += 1
            elif '级别:6级' in yufadian:
                result_dict['6级'] += 1
            elif '级别:高等' in yufadian:
                result_dict['高等'] += 1

    record = {}
    for k, v in result_dict.items():
        total = sum(list(result_dict.values()))
        if total > 0:
            ratio = round(v / total, 4)
            print(f'{k}语法点 占比:', ratio)
            record[f'{k}语法点 占比'] = ratio
        else:
            print(f'{k}语法点 占比:', 0.0)
            record[f'{k}语法点 占比'] = 0.0

    return record

def evaluate_error_fn(target_dir):
    file = os.path.join(target_dir, 'error_correction/generated_predictions.jsonl')
    file = open(file, 'r', encoding='utf-8')

    data = [json.loads(line) for line in file]

    multi_dimension_error_dict = {
        '字偏误': ['[C]', '[B]', '[L]', '[D]', '[F]', '[Y]', '[P]', '[#]', '[BC]', '[BQ]', '[BD]'],
        '词偏误': ['{CC}','{CLH}', '{W}', '{CQ}', '{CY}'],
        '句偏误': ['{CJ}','{CJba}', '{CJbei}', '{CJbi}', '{CJl}', '{CJy}', '{CJs}', '{CJsd}', '{CJcx}', '{CJjy}',
                   '{CJld}',
                   '{CJshb}', '{CJxw}', '{CJ-}', '{CJ-zhuy}', '{CJ-wy}', '{CJ-sy}', '{CJ-by}', '{CJ-buy}', '{CJ-dy}',
                   '{CJ-zy}', '{CJ-zxy}', '{CJ+}', '{CJ+zhuy}', '{CJ+wy}', '{CJ+sy}', '{CJ+by}', '{CJ+buy}', '{CJ+dy}',
                   '{CJ+zy}', '{CJ+zxy}', '{CJX}', '{CJZR}', '{CJcd}', '{CJgd}', '{WWJ}', '{CJ？}'],
        '篇章偏误': ['{CP}']
    }

    multi_dimension_error_result_dict = {
        '字偏误': 0,
        '词偏误': 0,
        '句偏误': 0,
        '篇章偏误': 0
    }

    error_num_per_essay = []
    for d in data:
        predict = d['predict'].strip().replace('<think>\n\n</think>\n\n', '')

        allLines = predict.split('\n')
        content_cleaned, error_detection_dict = performAllRules(allLines)
        error_num_per_essay.append(sum(list(error_detection_dict.values())))
        error_detection_dict = dict(sorted(error_detection_dict.items(), key=lambda x:x[1],reverse=True))

        for k, v in error_detection_dict.items():
            if v > 0:
                for mul_error_cls, mul_error_list in multi_dimension_error_dict.items():
                    mul_error_list_temp = [temp.replace('[','').replace(']','').replace('{','').replace('}','') for temp in mul_error_list]
                    k_temp = k.replace('[','').replace(']','').replace('{','').replace('}','')
                    # if k in mul_error_list:
                    if k_temp in mul_error_list_temp:
                        multi_dimension_error_result_dict[mul_error_cls] += 1

    record = {}
    record['平均偏误数'] = round(sum(list(multi_dimension_error_result_dict.values())) / len(error_num_per_essay), 4)

    print('每篇平均偏误数：', round(sum(error_num_per_essay)/len(error_num_per_essay),4))
    print('每篇平均偏误数2：', round(sum(list(multi_dimension_error_result_dict.values())) / len(error_num_per_essay), 4))
    for k, v in multi_dimension_error_result_dict.items():
        total = sum(list(multi_dimension_error_result_dict.values()))
        if total > 0:
            print(f'{k}, 个数:', v)
            ratio = round(v / total, 4)
            print(f'{k}, 占比:', ratio, '\n')
            record[f'{k}, 占比'] = ratio
        else:
            print(f'{k}, 个数:', v)
            ratio = 0.0
            print(f'{k}, 占比:', ratio, '\n')
            record[f'{k}, 占比'] = 0.0

    return record

def grade_assessment_fn(target_dir):
    file = os.path.join(target_dir, 'grade_assessment/generated_predictions.jsonl')
    file = open(file, 'r', encoding='utf-8')

    data = [json.loads(line) for line in file]

    ## 取范围
    range_grade_dict_predict = {
        '40-60': 0,
        '60-80': 0,
        # '80-90': 0,
        # '90-100': 0
        '80-100': 0
    }

    def range_fn(grade, range_dict):
        grade_temp = -1
        if 40 <= grade < 60:
            grade_temp = '40-60'
            range_dict['40-60'] += 1
        elif 60 <= grade < 80:
            grade_temp = '60-80'
            range_dict['60-80'] += 1
        # elif 80 <= grade < 90:
        #     grade_temp = '80-90'
        #     range_dict['80-90'] += 1
        # elif 90 <= grade:
        #     grade_temp = '90-100'
        #     range_dict['90-100'] += 1
        elif 80 < grade:
            grade_temp = '80-100'
            range_dict['80-100'] += 1
        return range_dict, grade_temp

    grades = []
    for d in data:
        predict = d['predict'].strip().replace('<think>\n\n</think>\n\n', '').replace('分数：','')
        predict_grade = int(predict)
        grades.append(predict_grade) ##记录每一篇的分数

        range_grade_dict_predict, range_grade = range_fn(predict_grade,range_grade_dict_predict)

    record = {}
    print('平均分：', round(sum(grades)/len(grades),4))
    for range_grades, num in range_grade_dict_predict.items():
        ratio = round(num/sum(list(range_grade_dict_predict.values())),4)
        print(f'分数段 {range_grades} 占比：',ratio)
        record[f'分数段 {range_grades} 占比'] = ratio

    record['平均分'] = round(sum(grades)/len(grades),4)
    return record

def linguistic_metrics_fn(target_dir):
    file = os.path.join(target_dir, 'error_correction/generated_predictions.jsonl')
    file = open(file, 'r', encoding='utf-8')

    data = [json.loads(line) for line in file]
    dfs = []
    for essay_id,d in enumerate(tqdm(data[:30],desc='正在计算复杂度指标')):
        essay = d['prompt'].split('你是一个HSK作文纠错器，请你对以下作文进行纠错：')[-1].replace('\n原始作文：','').replace('<|im_end|>\n<|im_start|>assistant','')
        df = ltp_fn(essay_id,essay)
        dfs.append(df)

    all_df = pd.concat(dfs,axis=0).reset_index(drop=True)
    metrics_result = calculate_linguistic_metrics_fn(all_df)
    print(metrics_result)
    return metrics_result

if __name__ == '__main__':
    target_dir = '3.Agent对模型作文的自动化评估/case'
    print(target_dir)

    print('#'*15)
    print('语法点检测结果:')
    record1 = evaluate_grammar_fn(target_dir)
    print('#' * 15)
    print('纠错结果:')
    record2 = evaluate_error_fn(target_dir)
    print('#' * 15)
    print('评分结果:')
    record3 = grade_assessment_fn(target_dir)
    print('#' * 15)
    print('语言学指标结果:')
    record4 = linguistic_metrics_fn(target_dir)

    all_record = {}
    for k,v in record1.items():
        all_record[k] = v
    for k,v in record2.items():
        all_record[k] = v
    for k,v in record4.items():
        all_record[k] = v
    for k,v in record3.items():
        all_record[k] = v

    print('\n',target_dir)
    for k,v in all_record.items():
        print(v,end='\t')