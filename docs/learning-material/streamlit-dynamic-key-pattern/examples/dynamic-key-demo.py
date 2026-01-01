"""
動態 Key 模式範例程式碼

此檔案展示如何在 Streamlit 應用程式中使用動態 Key 模式
解決第三方元件資料不更新的問題。
"""

import streamlit as st
from streamlit_sortables import sort_items


@st.fragment
def render_sortable_list_static_key():
    """
    ❌ 錯誤示範：使用靜態 Key
    
    當使用者新增或移除項目時，sort_items 元件不會更新，
    因為 Streamlit 認為它是同一個元件。
    """
    st.subheader("❌ 靜態 Key（有問題）")
    
    all_options = ["項目 A", "項目 B", "項目 C", "項目 D", "項目 E"]
    selected = st.multiselect(
        "選擇項目", 
        options=all_options, 
        default=["項目 A", "項目 B"],
        key="static_demo_multiselect"
    )
    
    if selected:
        st.caption("拖曳以重新排序：")
        # 靜態 Key - 不會在選取改變時更新
        ordered = sort_items(selected, key="static_sorter")
        st.write("排序結果:", ordered)


@st.fragment
def render_sortable_list_dynamic_key():
    """
    ✅ 正確示範：使用動態 Key
    
    當使用者新增或移除項目時，sort_items 元件會立即更新，
    因為動態 Key 讓 Streamlit 認為這是一個新元件。
    """
    st.subheader("✅ 動態 Key（正確）")
    
    all_options = ["項目 A", "項目 B", "項目 C", "項目 D", "項目 E"]
    selected = st.multiselect(
        "選擇項目", 
        options=all_options, 
        default=["項目 A", "項目 B"],
        key="dynamic_demo_multiselect"
    )
    
    if selected:
        st.caption("拖曳以重新排序：")
        # 動態 Key - 選取改變時強制重建
        dynamic_key = f"dynamic_sorter_{hash(tuple(selected))}"
        ordered = sort_items(selected, key=dynamic_key)
        st.write("排序結果:", ordered)
        st.caption(f"目前 Key: `{dynamic_key}`")


def main():
    """主程式入口。"""
    st.title("動態 Key 模式示範")
    st.markdown("""
    這個範例展示靜態 Key 和動態 Key 的差異。
    
    **操作步驟：**
    1. 在左邊（靜態 Key）新增或移除項目，觀察排序列表不會更新
    2. 在右邊（動態 Key）新增或移除項目，觀察排序列表會立即更新
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_sortable_list_static_key()
    
    with col2:
        render_sortable_list_dynamic_key()


if __name__ == "__main__":
    main()
