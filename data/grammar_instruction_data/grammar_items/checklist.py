import pandas as pd

file = '目标语法项目.xlsx'
df_dict = pd.read_excel(file,sheet_name=None)

columns = list(df_dict['3级'].columns)
columns = columns[:-1]

for cls, df in df_dict.items():
    print('############',cls)
    for i in range(len(df)):
        record = []
        for col in columns:
            value = df.loc[i,col]
            if pd.isna(value):
                value = '~'
            else:
                if col == '语法内容':
                    # value = "\makecell[l]{" + value.strip().replace('#','\\#') + '}'
                    value = value.strip().replace('#', '\\#')
            record.append(str(value))

        record = ' & '.join(record)
        record = record + '\\\\'
        print(record)

print()