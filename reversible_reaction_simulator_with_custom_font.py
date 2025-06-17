import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from scipy.integrate import odeint
import os

# 設置字型
font_path = "font.otf"  # 確保 font.otf 在同一目錄
if not os.path.exists(font_path):
    st.error("字型檔案 font.otf 不存在！請確認檔案路徑。")
else:
    custom_font = FontProperties(fname=font_path)

# 設置頁面標題
st.title("可逆化學反應模擬器")

# 說明
st.write("此模擬器幫助化學老師繪製可逆反應中物種濃度隨反應進度的變化圖。請輸入反應物與產物的資訊，設定平衡常數K與反應速率，並選擇要顯示的物種。")

# 初始化 session state
if 'reactants' not in st.session_state:
    st.session_state.reactants = []
if 'products' not in st.session_state:
    st.session_state.products = []

# 輸入反應物
st.subheader("新增反應物")
reactant_name = st.text_input("反應物名稱", key="reactant_name")
reactant_initial = st.number_input("初始濃度 (mol/L)", min_value=0.0, value=1.0, step=0.1, key="reactant_initial")
if st.button("新增反應物"):
    if reactant_name:
        st.session_state.reactants.append({'name': reactant_name, 'initial': reactant_initial})
        st.success(f"已新增反應物: {reactant_name}")

# 顯示反應物列表
if st.session_state.reactants:
    st.write("反應物列表:")
    for i, r in enumerate(st.session_state.reactants):
        st.write(f"{r['name']}: 初始濃度 = {r['initial']} mol/L")
        if st.button(f"移除 {r['name']}", key=f"remove_reactant_{i}"):
            st.session_state.reactants.pop(i)
            st.experimental_rerun()

# 輸入產物
st.subheader("新增產物")
product_name = st.text_input("產物名稱", key="product_name")
product_initial = st.number_input("初始濃度 (mol/L)", min_value=0.0, value=0.0, step=0.1, key="product_initial")
if st.button("新增產物"):
    if product_name:
        st.session_state.products.append({'name': product_name, 'initial': product_initial})
        st.success(f"已新增產物: {product_name}")

# 顯示產物列表
if st.session_state.products:
    st.write("產物列表:")
    for i, p in enumerate(st.session_state.products):
        st.write(f"{p['name']}: 初始濃度 = {p['initial']} mol/L")
        if st.button(f"移除 {p['name']}", key=f"remove_product_{i}"):
            st.session_state.products.pop(i)
            st.experimental_rerun()

# 輸入反應參數
st.subheader("反應參數")
K = st.number_input("平衡常數 K", min_value=0.0, value=1.0, step=0.1)
kf = st.number_input("正向反應速率常數 (k_f)", min_value=0.0, value=1.0, step=0.1)
time_end = st.number_input("模擬時間 (秒)", min_value=1.0, value=10.0, step=1.0)

# 選擇顯示的物種
st.subheader("選擇顯示的物種")
species_options = [r['name'] for r in st.session_state.reactants] + [p['name'] for p in st.session_state.products]
selected_species = st.multiselect("選擇要顯示的物種濃度", species_options, default=species_options)

# 模擬反應
if st.button("運行模擬"):
    if not st.session_state.reactants or not st.session_state.products:
        st.error("請至少新增一個反應物和一個產物！")
    else:
        # 假設反應為：aA + bB ⇌ cC + dD
        # 簡單起見，假設係數均為1
        def reaction_rate(C, t, kf, K):
            kr = kf / K  # 逆向速率常數
            n_reactants = len(st.session_state.reactants)
            n_products = len(st.session_state.products)
            reactants_conc = C[:n_reactants]
            products_conc = C[n_reactants:]
            
            forward_rate = kf * np.prod(reactants_conc)
            reverse_rate = kr * np.prod(products_conc)
            
            dCdt = []
            for _ in range(n_reactants):
                dCdt.append(-forward_rate + reverse_rate)
            for _ in range(n_products):
                dCdt.append(forward_rate - reverse_rate)
            return dCdt

        # 初始濃度
        initial_concentrations = [r['initial'] for r in st.session_state.reactants] + [p['initial'] for p in st.session_state.products]
        
        # 時間點
        t = np.linspace(0, time_end, 1000)
        
        # 解微分方程
        solution = odeint(reaction_rate, initial_concentrations, t, args=(kf, K))
        
        # 使用 Matplotlib 繪圖
        fig, ax = plt.subplots()
        for i, species in enumerate([r['name'] for r in st.session_state.reactants] + [p['name'] for p in st.session_state.products]):
            if species in selected_species:
                ax.plot(t, solution[:, i], label=species)
        
        # 設置字型
        ax.set_title("物種濃度隨時間變化", fontproperties=custom_font)
        ax.set_xlabel("時間 (秒)", fontproperties=custom_font)
        ax.set_ylabel("濃度 (mol/L)", fontproperties=custom_font)
        ax.legend(prop=custom_font)
        ax.grid(True)
        
        # 在 Streamlit 中顯示圖表
        st.pyplot(fig)
