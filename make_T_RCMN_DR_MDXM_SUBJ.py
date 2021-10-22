import pandas as pd
import re
from tqdm import tqdm

folder_path = 'C:/Users/mhcho/Documents/2021/04_데이터 마트/03_DB화/의사정보DB/'
file_3 = '211019_병원정보.xlsx'

df = pd.read_excel(folder_path + file_3, sheet_name='T_RCMN_HOSP_MDXM_SUBJ_HIS', engine='openpyxl')

new_df = pd.DataFrame(columns=['RCMN_HOSP_ID', 'REG_SEQ', 'MDXM_SUBJ_NM'])

for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    line = row['MDXM_SUBJ_NM']
    if type(line) is float:
        continue
    if type(line) is int:
        continue
    check_comma = [i for i in range(len(line)) if line.startswith(',', i)]
    check_open = [i for i in range(len(line)) if line.startswith('(', i)]
    check_close = [i for i in range(len(line)) if line.startswith(')', i)]
    remove_comma = []
    open_number = 0
    close_number = 0
    if len(check_open) != 0:
        for com_idx in check_comma:
            open_flag = check_open[open_number]
            if len(check_close) == 0:
                continue
            elif len(check_close) != len(check_open):
                if close_number == len(check_open) - 1:
                    continue
            close_flag = check_close[close_number]

            if open_flag <= com_idx & com_idx <= close_flag:
                remove_comma.append(com_idx)
            elif com_idx > close_flag and open_number != len(check_open) - 1:
                open_number = open_number + 1
                close_number = close_number + 1

    result = list(set(check_comma) - set(remove_comma))
    result.append(0)
    indices = sorted(result)

    parts = [line[i:j] for i, j in zip(indices, indices[1:] + [None])]
    parts = [re.sub(r"^,\s*", "", w) for w in parts]
    parts = [w.replace('(수정)', '') for w in parts]

    for input_idx in range(len(parts)):
        new_df.loc[len(new_df)] = [row['RCMN_HOSP_ID'], input_idx + 1, parts[input_idx]]

new_df.to_csv(folder_path + 'T_RCMN_HOSP_MDXM_SUBJ_211019-utf-8-sig', encoding='utf-8-sig')
new_df.to_csv(folder_path + 'T_RCMN_HOSP_MDXM_SUBJ_211019-utf-8', encoding='utf-8')
