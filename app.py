import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

# 페이지 기본 설정
st.set_page_config(page_title="패션 브랜드 원가 계산기 Pro", layout="wide")
# ... st.set_page_config(...) 아래에 추가

# 비밀번호 설정 (원하는 비밀번호로 바꾸세요)
PASSWORD = "5351"

# 로그인 화면
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("접속 비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # 화면 새로고침
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()  # 로그인 안 되면 아래 코드 실행 중지

# ... 이 아래부터 기존 def main(): 코드 시작
# ---------------------------------------------------------
# [기능 1] 엑셀 변환 함수 (스크랩된 데이터 전체 다운로드)
# ---------------------------------------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='원가계산_리스트')
        
        # 엑셀 서식 자동 조정 (열 너비 등)
        workbook = writer.book
        worksheet = writer.sheets['원가계산_리스트']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15) # 너비 조정

    processed_data = output.getvalue()
    return processed_data

# ---------------------------------------------------------
# [메인] 앱 실행
# ---------------------------------------------------------
def main():
    st.title("🧢 Smart Costing Master (Hat Edition)")
    
    # 세션 상태 초기화 (스크랩 저장소)
    if 'scraps' not in st.session_state:
        st.session_state.scraps = []
    
    # -----------------------------------------------------
    # 사이드바: 스크랩(저장)된 리스트 확인 및 엑셀 다운로드
    # -----------------------------------------------------
    with st.sidebar:
        st.header("🗂️ 스크랩 리스트 (Saved Items)")
        
        if len(st.session_state.scraps) > 0:
            # 스크랩된 데이터를 DataFrame으로 변환
            scrap_df = pd.DataFrame(st.session_state.scraps)
            
            # 화면에 간략히 표시
            st.dataframe(scrap_df[['상품명', '판매가', '순이익', '마진율']], hide_index=True)
            
            # [기능 2] 엑셀 다운로드 버튼
            excel_data = to_excel(scrap_df)
            st.download_button(
                label="📥 전체 리스트 엑셀 다운로드",
                data=excel_data,
                file_name=f"원가계산서_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            if st.button("🗑️ 리스트 전체 삭제"):
                st.session_state.scraps = []
                st.rerun()
        else:
            st.info("아직 저장된 계산 내역이 없습니다. 메인 화면에서 '현재 결과 스크랩하기'를 눌러보세요.")

    st.markdown("---")

    # -----------------------------------------------------
    # 메인 화면: 계산기 입력 폼
    # -----------------------------------------------------
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("1. 상품 정보 및 자재비")
        product_name = st.text_input("상품명 (Item Name)", value="2026 SS 시그니처 볼캡")
        produce_qty = st.number_input("생산 수량", min_value=1, value=100, step=10)

        # 자재비 초기값 설정
        if 'materials' not in st.session_state:
            st.session_state.materials = pd.DataFrame(
                [
                    {"항목": "겉감 (Main Fabric)", "단가": 4500, "요척": 0.3},
                    {"항목": "챙심 (Brim)", "단가": 500, "요척": 1.0},
                    {"항목": "땀받이 (Sweatband)", "단가": 800, "요척": 1.0},
                    {"항목": "탑버튼 & 아일렛", "단가": 150, "요척": 1.0},
                    {"항목": "메인 라벨", "단가": 120, "요척": 1.0},
                    {"항목": "케어 라벨", "단가": 80, "요척": 1.0},
                    {"항목": "폴리백 & 박스", "단가": 500, "요척": 1.0},
                ]
            )

        edited_materials = st.data_editor(
            st.session_state.materials,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "단가": st.column_config.NumberColumn(format="%d원"),
                "요척": st.column_config.NumberColumn(format="%.2f")
            }
        )
        
        # 총 자재비 계산
        material_sum = (edited_materials["단가"] * edited_materials["요척"]).sum()

    with col2:
        st.header("2. 공임비 및 설정")
        
        c1, c2 = st.columns(2)
        with c1:
            sewing = st.number_input("봉제 공임", value=6000, step=100)
            embroidery = st.number_input("자수/나염", value=1500, step=100)
        with c2:
            finish = st.number_input("시야게/포장", value=500, step=100)
            logistics = st.number_input("물류비/기타", value=300, step=100)
            
        fixed_cost = st.number_input("패턴/샘플 고정비 (전체)", value=300000, step=10000)
        
        # 총 원가 계산 로직
        fixed_per_unit = fixed_cost / produce_qty
        labor_sum = sewing + embroidery + finish + logistics + fixed_per_unit
        total_cog = material_sum + labor_sum

        st.markdown(f"### 🏷️ 개당 제조 원가: :blue[{int(total_cog):,}원]")

        st.markdown("---")
        
        # 판매가 및 수수료 설정
        target_price = st.number_input("판매 희망가", value=49000, step=1000)
        
        fee_options = {"자사몰 (3.5%)": 0.035, "무신사 (30%)": 0.30, "스마트스토어 (6%)": 0.06, "백화점 (35%)": 0.35}
        channel = st.selectbox("판매 채널", list(fee_options.keys()))
        fee_rate = fee_options[channel]
        
        vat_on = st.checkbox("VAT 포함 판매가", value=True)

        # 이익 계산
        if vat_on:
            vat = target_price - (target_price / 1.1)
        else:
            vat = target_price * 0.1
            
        fee = target_price * fee_rate
        profit = target_price - total_cog - fee - vat
        margin = (profit / target_price) * 100 if target_price > 0 else 0

        # 결과 표시 카드
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: {'#e6fffa' if profit > 0 else '#fff5f5'}">
            <h4>💰 순이익: {int(profit):,}원 ({margin:.1f}%)</h4>
            <small>판매가 {int(target_price):,}원 - 원가 {int(total_cog):,}원 - 수수료 {int(fee):,}원 - 부가세 {int(vat):,}원</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # 여백

        # -----------------------------------------------------
        # [기능 1] 내부 저장(스크랩) 버튼
        # -----------------------------------------------------
        if st.button("📌 현재 결과 스크랩하기 (Save to List)", use_container_width=True, type="primary"):
            # 현재 상태를 딕셔너리로 저장
            scrap_item = {
                "상품명": product_name,
                "생산수량": produce_qty,
                "채널": channel,
                "판매가": int(target_price),
                "제조원가": int(total_cog),
                "수수료": int(fee),
                "부가세": int(vat),
                "순이익": int(profit),
                "마진율": f"{margin:.1f}%",
                "저장일시": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.scraps.append(scrap_item)
            st.toast(f"'{product_name}' 저장 완료! 사이드바를 확인하세요.", icon="✅")
            st.rerun() # 화면 새로고침하여 사이드바 업데이트

if __name__ == "__main__":
    main()