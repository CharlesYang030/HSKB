import pandas as pd

file = '预训练数据目录.xlsx'
df = pd.read_excel(file)

columns = df.columns
columns = [col for col in columns if 'HSK5' in col or 'HSK6' in col]

for i in range(len(df)):
    record = []
    for col in columns:
        value = df.loc[i,col]
        if 'Titles' in col:
            pass
        else:
            if '题目' in col:
                hsk_level = col.replace('题目','')
                title_col = hsk_level + ' Titles'
                if pd.isna(value):
                    value = '~'
                else:
                    value = "\makecell[l]{" + value.strip() + ' \\\\ \\textit{' + df.loc[i,title_col] + '}' +  '}'

            if pd.isna(value):
                value = '~'

            if isinstance(value,float):
                value = int(value)

            record.append(str(value))

    record = ' & '.join(record)
    record += ' \\\\'
    print(record)

print()