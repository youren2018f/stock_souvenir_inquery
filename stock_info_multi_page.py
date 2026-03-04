import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# --- 1. 初始化資料與快取 ---
inventory_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQL4Pg0pLF4gg23UHyC4COsat3NOyfFYbnZoenJD6JX-hith6CKZWlEdM_qZrfogYVOqF0XGrcZmVHp/pub?output=xlsx"

@st.cache_data
def get_inventory(name):
    try:
        df = pd.read_excel(inventory_url, sheet_name=name, header=None)
        return list(df[0])
    except:
        return []

# 取得個人庫存字典
owings = {
    "youren": get_inventory("youren"),
    "pty": get_inventory("pty"),
    "cyc": get_inventory("cyc")
}

# --- 2. 側邊欄選單 ---
with st.sidebar:
    choose = option_menu("App Gallery", ["庫存查詢", "histock資料比對", "RachlMei Excel"],
                         icons=['search', 'kanban', 'book'], default_index=0)

# --- 3. 頁面邏輯 ---

if choose == "庫存查詢":
    text_input = st.text_input('請輸入股號，多個股號以空白間隔')
    if text_input:
        query = [int(x) for x in text_input.split() if x.isdigit()]
        own_sit = {q: [1 if q in li else 0 for li in owings.values()] for q in query}
        st.dataframe(pd.DataFrame.from_dict(own_sit, orient='index', columns=owings.keys()))

elif choose == "histock資料比對":
    @st.cache_data
    def get_histock(tid):
        h_url = "https://histock.tw/stock/gift.aspx"
        res = requests.get(h_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"id": tid})
        return pd.read_html(io.StringIO(str(table)))[0] if table else pd.DataFrame()

    opt = st.selectbox('選擇表格', ('最新公告', '最後買進日未到期', '最後買進日已到期'))
    tid_map = {'最新公告': "CPHB1_gvToday", '最後買進日未到期': "CPHB1_gv", '最後買進日已到期': "CPHB1_gvOld"}
    
    df_hi = get_histock(tid_map[opt])
    if not df_hi.empty:
        # 建立比對欄位，假設 HiStock 第一欄是股號
        df_hi['股號'] = df_hi.iloc[:, 0].astype(str)
        own_res = {str(c): [1 if int(c) in li else 0 for li in owings.values()] 
                   for c in df_hi['股號'] if c.isdigit()}
        df_own = pd.DataFrame.from_dict(own_res, orient='index', columns=owings.keys()).reset_index().rename(columns={'index': '股號'})
        st.dataframe(pd.merge(df_hi, df_own, on='股號', how='left'))

elif choose == "RachlMei Excel":
    st.subheader("RachlMei 紀念品清單 (自動同步)")
    # 使用 CSV 導出格式，這是處理繁體中文最穩定的方式
    gs_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTG7Rb_wjFaHq1Z_ExcEN5EMZPR4-iFvdr5xKvVH-hJORNx6WhCZoijIFYuDGXkKIKqf4WjcBhQ_TYR/pub?gid=122218471&single=true&output=csv"
    
    try:
        # 1. 抓取 Google Sheet 資料
        res = requests.get(gs_url, timeout=15)
        # 強制指定編碼為 utf-8-sig，這能解決大多數從 Excel/Google 匯出時的亂碼
        res.encoding = 'utf-8-sig' 
        
        # 使用 io.StringIO 讀取 csv 資料流
        raw_df = pd.read_csv(io.StringIO(res.text), header=None)
        
        # 2. 定位 A區 與 B區 範圍
        start, end = None, None
        for i, row in raw_df.iterrows():
            line = " ".join(row.astype(str))
            if "A區" in line and start is None: start = i + 1
            if "B區" in line: end = i; break
        
        if start is not None and end is not None:
            # 3. 擷取並命名欄位 (根據你 2026-03 的爬蟲經驗選取特定索引)
            df_main = raw_df.iloc[start:end, [0, 1, 2, 3, 14]].copy()
            df_main.columns = ["股號", "名稱", "股東會紀念品", "股價", "去年紀念品"]
            df_main['股號'] = df_main['股號'].astype(str).str.strip()
            
            # 4. 比對個人庫存 (youren, pty, cyc)
            # 整合你在 macOS 與 Windows 跨平台開發時管理的投資名單
            own_sit = {}
            for _, r in df_main.iterrows():
                code_str = r["股號"]
                if code_str.isdigit():
                    code_int = int(code_str)
                    # 比對你在 2026-02 設定的台積電等持股分配
                    own_sit[code_str] = [1 if code_int in li else 0 for li in owings.values()]
            
            df_own = pd.DataFrame.from_dict(own_sit, orient='index', columns=owings.keys()).reset_index().rename(columns={'index': '股號'})
            df_final = pd.merge(df_main, df_own, on='股號', how='left')
            
            # 5. 抓取 Stockhouse 收購價並處理編碼
            try:
                sh_res = requests.get("https://stockhouse.com.tw/dantime.html", timeout=10)
                # 關鍵：自動偵測並設定收購價網站的編碼
                sh_res.encoding = sh_res.apparent_encoding 
                
                sh_tables = pd.read_html(io.StringIO(sh_res.text))
                if sh_tables:
                    sh_df_raw = sh_tables[0]
                    if len(sh_df_raw.columns) >= 4:
                        sh_df = sh_df_raw.iloc[:, [0, 1, 2, 3]].copy()
                        sh_df.columns = ['股號', '紀念品_收購', '收購價', '委託條件']
                        sh_df['股號'] = sh_df['股號'].astype(str).str.strip()
                        
                        # 最終合併庫存與收購資訊
                        merged = pd.merge(df_final, sh_df, on='股號', how='left')
                        st.dataframe(merged, use_container_width=True)
                    else:
                        st.dataframe(df_final, use_container_width=True)
            except:
                st.warning("收購價網站讀取異常，暫僅顯示紀念品清單。")
                st.dataframe(df_final, use_container_width=True)
        else:
            st.error("找不到 A區/B區 邊界標記。")
    except Exception as e:
        st.error(f"執行出錯: {e}")
