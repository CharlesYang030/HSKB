import json
import time
import pandas as pd
from tqdm import tqdm
from openai import OpenAI

## openrouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="your key",
)

def chatgpt_fn(now_prompt):
    try:
        messages = [
            {"role": "system", "content": '你是一位经验丰富的中文写作教学专家，擅长设计写作型语法教学任务。'},
            {"role": "user", "content": now_prompt}
        ]

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            extra_body={},
            model="google/gemini-2.5-flash-preview",
            messages=messages,
            temperature=1.6,
            max_tokens=1200,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )

        ## 记录结果
        result_raw = response.choices[0].message.content

        try:
            # 获取dict内容
            result_verified = json.loads(result_raw)
            keys = list(result_verified.keys())
            if keys != ['instruction', 'input', 'output']:
                return 'broken', result_raw
            json_result = result_verified
            return 'completed', json_result
        except Exception as e:  # 如果上面的代码报错，则会将该错误打印出来，并且返回'broken'
            print(e)
            return 'broken', result_raw
    except Exception as e:
        print('BAD FOR CALLING', e)
        return 'broken', 'BAD FOR CALLING'

def main_fn(df_dict,prompt):
    error_num = 0
    valid_count = 0
    result_df = []

    outjsonl = open(f'2.gpt对目标语法点生成sft数据/gemini_教学指令数据生成0626.jsonl', 'a+', encoding='utf-8')

    for level,df in df_dict.items():
        loop = tqdm(range(0,len(df)),desc=f'Processing {level}... [Text ID: X] [Valid Num: {valid_count}]',colour='green')
        instruction_record = []
        for i in loop:
            if level == '3级':
                continue
            if level == '4级' and i < 74:
                continue

            no = df.loc[i,'No.']
            yufaxiangmu = df.loc[i,'语法项目']
            leibie = df.loc[i,'类别']
            if pd.isna(leibie):
                leibie = ''
            ximu = df.loc[i,'细目']
            if pd.isna(ximu):
                ximu = ''
            yufaneirong = df.loc[i,'语法内容']

            input_dict = {
                "HSK等级": level,
                "语法项目": yufaxiangmu,
                "类别": leibie,
                "细目": ximu,
                "语法内容": yufaneirong
            }
            input_str = json.dumps(input_dict,indent=3,ensure_ascii=False)

            instruction_num = 10 ## 每个语法点控制生成的指令数据条数
            for pool_num in tqdm(range(instruction_num)):
                # time.sleep(1.5)
                now_prompt = prompt.replace('[Instruction Pool]',str(instruction_record)).replace('[New Grammar Point]',input_str)

                gpt_flag, gpt_result = chatgpt_fn(now_prompt)
                times = 1
                while gpt_flag == 'broken':
                    time.sleep(2)
                    gpt_flag, gpt_result = chatgpt_fn(now_prompt)
                    times += 1
                    if gpt_flag == 'broken' and times >= 3:
                        error_num += 1
                        print('Error Num: ', error_num)
                        temp_dict = {
                            'No.': int(no),
                            '级别': level,
                            "语法项目": yufaxiangmu,
                            "类别": leibie,
                            "细目": ximu,
                            "语法内容": yufaneirong,
                            'gpt_result': json.dumps(gpt_result, ensure_ascii=False, indent=3),
                            "instruction": 'ERROR',
                            "input": 'ERROR',
                            "output": 'ERROR',
                        }
                        break
                else:
                    temp_dict = {
                        'No.': int(no),
                        '级别': level,
                        "语法项目": yufaxiangmu,
                        "类别": leibie,
                        "细目": ximu,
                        "语法内容": yufaneirong,
                        'gpt_result': json.dumps(gpt_result, ensure_ascii=False, indent=3),
                        "instruction": gpt_result['instruction'],
                        "input": gpt_result['input'],
                        "output": gpt_result['output'],
                    }
                    valid_count += 1
                    ## 记录当前的指令数据
                    now_instruction = {
                        '指令序号': pool_num + 1,
                        'instruction': gpt_result['instruction'],
                        'input': gpt_result['input'],
                        'output': gpt_result['output']
                    }
                    instruction_record.append(now_instruction)

                loop.set_description(f'Processing {level}... [Text ID: {i}] [Valid Num: {valid_count}]')
                result_df.append(temp_dict)
                json_str = json.dumps(temp_dict, ensure_ascii=False,indent=3)  # 确保非 ASCII 字符能正常写入
                outjsonl.write(json_str + "\n")  # 每个 JSON 对象写入一行

        #     if i == 4:
        #         break
        #
        # break

    result_df = pd.DataFrame(result_df)
    result_df.to_excel(f'2.gpt对目标语法点生成sft数据/gemini_教学指令数据生成0626.xlsx', index=False)

if __name__ == '__main__':
    df_dict = pd.read_excel('1.目标语法点整理/目标语法项目_拆分.xlsx',sheet_name=None)
    prompt = open('2.gpt对目标语法点生成sft数据/prompts/1.对语法项目生成sft数据_gemini.txt', 'r', encoding='utf-8').read()
    main_fn(df_dict,prompt)