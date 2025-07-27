import pandas as pd

file = '1.目标语法点整理/HSK_语法点全集.xlsx'
df_dict = pd.read_excel(file,sheet_name=None)

writer = pd.ExcelWriter('1.目标语法点整理/目标语法项目.xlsx')
target_grammars = ['词类','短语','固定格式','句子成分','句子的类型','强调的方法']
for level,df in df_dict.items():
    level_record = []
    for gram in target_grammars:
        sub_df = df[df['语法项目'] == gram].reset_index(drop=True)
        level_record.append(sub_df)
    level_df = pd.concat(level_record,axis=0).reset_index(drop=True)
    level_df.to_excel(writer,sheet_name=level,index=False)

writer._save()
