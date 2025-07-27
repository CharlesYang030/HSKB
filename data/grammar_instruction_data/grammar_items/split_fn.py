import pandas as pd

file = '目标语法项目.xlsx'
df_dict = pd.read_excel(file,sheet_name=None)

outxlsx = pd.ExcelWriter('目标语法项目_拆分.xlsx')
for level, df in df_dict.items():
    record = []
    for i in range(len(df)):
        yufaneirong = df.loc[i,'语法内容']
        no = df.loc[i, 'No.']
        yufaxiangmu = df.loc[i, '语法项目']
        leibie = df.loc[i, '类别']
        ximu = df.loc[i, '细目']


        if '#' in yufaneirong:
            temp_text = yufaneirong.split('#')
            for text in temp_text:
                text = text.strip()
                if text != '':
                    temp_dict = {
                        'No.': int(no),
                        '语法项目': yufaxiangmu,
                        '级别': level,
                        '类别': leibie,
                        '细目': ximu,
                        '语法内容': text
                    }
                    record.append(temp_dict)
        elif '、' in yufaneirong:
            temp_text = yufaneirong.split('、')
            for text in temp_text:
                text = text.strip()
                if text != '':
                    temp_dict = {
                        'No.': int(no),
                        '语法项目': yufaxiangmu,
                        '级别': level,
                        '类别': leibie,
                        '细目': ximu,
                        '语法内容': text
                    }
                    record.append(temp_dict)
        else:
            temp_dict = {
                'No.': int(no),
                '语法项目': yufaxiangmu,
                '级别': level,
                '类别': leibie,
                '细目': ximu,
                '语法内容': yufaneirong
            }
            record.append(temp_dict)

    record_df = pd.DataFrame(record)
    record_df.to_excel(outxlsx,sheet_name=level,index=False)

outxlsx._save()