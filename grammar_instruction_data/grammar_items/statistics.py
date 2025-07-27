import pandas as pd

file = pd.read_excel('目标语法项目_拆分.xlsx',sheet_name=None)

for cls,df in file.items():
    projects = list(df['语法项目'].unique())
    pro_dict = {}
    for pro in projects:
        sub_df = df[df['语法项目']==pro]
        pro_dict[pro] = len(sub_df)
    print(cls)
    print(pro_dict)
    print(sum(list(pro_dict.values())))
