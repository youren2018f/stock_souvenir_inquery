import pandas as pd
import streamlit as st
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQL4Pg0pLF4gg23UHyC4COsat3NOyfFYbnZoenJD6JX-hith6CKZWlEdM_qZrfogYVOqF0XGrcZmVHp/pub?output=xlsx"

@st.cache
def get_list(name):
    df = pd.read_excel(url,sheet_name = name,header=None)
    return list(df[0])



#建立各別的持有清單
youren_owings = get_list("youren")
pty_owings = get_list("pty")
cyc_owings = get_list("cyc")

#建立持有的字典
owings = dict(youren = youren_owings, pty = pty_owings, cyc = cyc_owings) 

text_input  = st.text_input('請輸入股號，多個股號以空白間隔')
query = text_input.split()

#query = input("輸入股號\n").split() #
query = list(map(int, query))

#產生比對結果的字典
own_situation = {}

for q in query:
    result_list = []
    for p,li in owings.items():
        if q in li:
            result_list.append(1)
        else:
            result_list.append(0)
    own_situation[q] = result_list

if text_input:
    df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])
    df

