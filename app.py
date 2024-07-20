import streamlit as st
import pandas as pd
import time
import plotly.express as px

# 데이터 프레임 정의 (예시 데이터)
df = pd.read_csv("C:/Users/82108/Downloads/2020g.csv", encoding="cp949")
df1 = pd.read_csv("C:/Users/82108/Downloads/2023gin2.csv", encoding="cp949")
df2 = pd.read_csv("C:/Users/82108/Downloads/edu.csv", encoding='cp949')

# 직종 추천 함수
def recommend_jobs(user_info, df):
    # 사용자 정보에 따라 데이터 필터링
    filtered_df = df.copy()
    for key, value in user_info.items():
        if key == '연령':  # 나이대를 기준으로 필터링
            filtered_df = filtered_df[(filtered_df[key] == value)]
        else:
            filtered_df = filtered_df[filtered_df[key] == value]

    # 필터링된 데이터에서 직종 대분류별 개수 계산
    job_counts = filtered_df['대분류'].value_counts().head(5)
    total_count = job_counts.sum()
    
    # 각 대분류의 비율 계산
    job_ratios = (job_counts / total_count) * 100
    
    # 데이터프레임으로 정리
    recommendations = pd.DataFrame({
        '대분류': job_counts.index,
        '개수': job_counts.values,
        '비율': job_ratios.values
    }).reset_index(drop=True)
    
    return recommendations

# 홈 페이지 함수
def show_home_page():
    st.markdown("<h1 style='text-align: center; color: #336699;'>희망고리 🔗</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #000000;'>꿈을 향한 희망찬 연결고리🪽</h4>", unsafe_allow_html=True)
    st.markdown("---")  # Separator between each item

# 메인 함수
def main():
    st.sidebar.header('메뉴 선택')
    menu_choice = st.sidebar.radio('', ['홈화면', '고용 추천 서비스', '커뮤니티'])

    if menu_choice == '홈화면':
        show_home_page()
        # 홈 화면으로 돌아갈 때 세션 상태 초기화
        st.session_state.clear()

    elif menu_choice == '고용 추천 서비스':
        st.markdown("<h4 style='text-align: center; color: #000000;'>사이드바에 정보를 입력하고 산업 추천을 받아보세요.</h4>", unsafe_allow_html=True)
        st.markdown("---")  # Separator between each item
        st.markdown("\n") 

        with st.sidebar:
            st.markdown("## 사용자 정보 입력")
            disability_type = st.selectbox("장애 유형을 선택하세요", df['장애유형'].unique())
            severity = st.radio("장애 중증도를 선택하세요", df['중증여부'].unique())
            age = st.number_input("나이를 입력하세요", min_value=0, max_value=100, step=1)
            desired_location = st.selectbox("희망 근무지를 선택하세요", df['희망지역'].dropna().unique())

            if st.button("입력 완료"):
                if disability_type and severity and age and desired_location:
                    # 사용자 정보 모으기
                    age_group = f"{int(age/10)*10}대"
                    user_info = {
                        '장애유형': disability_type,
                        '중증여부': severity,
                        '연령': age_group,
                        '희망지역': desired_location
                    }

                    # 산업 추천 받기
                    job_recommendations = recommend_jobs(user_info, df)

                    with st.spinner("추천 산업을 계산 중입니다..."):
                        time.sleep(2)  # 예시로 2초 동안 대기

                    # 사용자 정보와 추천 산업을 세션 상태에 저장
                    st.session_state['user_info'] = user_info
                    st.session_state['job_recommendations'] = job_recommendations
                    st.session_state['recommendation_made'] = True
                else:
                    st.warning("모든 정보를 입력해주세요")

    if st.session_state.get('recommendation_made', False):
        st.markdown(f"<h3 style='text-align: center; color: #336699;'>상위 추천 산업 5개:</h3>", unsafe_allow_html=True)

        job_recommendations = st.session_state['job_recommendations']
        user_info = st.session_state['user_info']

        st.markdown(f"**{user_info['연령']} {user_info['희망지역']}지역에서 {user_info['중증여부']} {user_info['장애유형']}를 가진 구직자들은 다음과 같은 산업에서 근무하고 있습니다**.")

        fig = px.pie(
            job_recommendations,
            values='개수',
            names='대분류',
            title=f"장애인 고용 추천 산업",
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.5,
            opacity=0.8
        )

        fig.update_layout(
            title_x=0.5,
            title_font=dict(size=24, color="#336699"),
            font=dict(size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            width=700,
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='closest',
            transition={'duration': 1000}
        )

        fig.update_traces(
            marker=dict(colors=['#FFC0CB', '#FFDAB9', '#B0E0E6', '#98FB98', '#FFA07A']),
            textinfo='label+percent',
            textfont_size=16,
            textposition='inside',
            hole=.5,
        )

        st.plotly_chart(fig)
        st.markdown("---")  # Separator between each item
        st.markdown("\n") 

        st.markdown("<h5 style='text-align: center; color: #336699;'>추천 산업 중 하나를 선택해주세요:</h5>", unsafe_allow_html=True)
        selected_job = st.selectbox("추천 직종", job_recommendations['대분류'])

        filtered_df1_1 = df1[(df1['대분류'] == selected_job) & (df1['사업장 주소'].str.contains(user_info['희망지역'])) & (df1['우선표출'] == 'Y')]
        filtered_df1_2 = df1[(df1['대분류'] == selected_job) & (df1['사업장 주소'].str.contains(user_info['희망지역'])) & (df1['우선표출'] != 'Y')]

        st.markdown("---")  # Separator between each item
        st.markdown("\n") 
        if not filtered_df1_1.empty:
            st.markdown(f"<h3 style='text-align: center; color: #336699;'>{selected_job}에 대한 우수구인 정보:</h3>", unsafe_allow_html=True)
            st.write(filtered_df1_1[[
                "사업장명",
                "모집직종",
                "고용형태",
                "임금형태",
                "임금",
                "입사형태",
                "요구경력",
                "요구학력",
                "전공계열",
                "요구자격증",
                "사업장 주소",
                "기업형태",
                "담당기관",
                "등록일",
                "연락처",
                "대분류"
            ]])
            st.markdown("---")  # Separator between each item
            st.markdown("\n") 
        
        st.markdown(f"<h3 style='text-align: center; color: #336699;'>{selected_job}에 대한 구인 정보:</h3>", unsafe_allow_html=True)
        st.write(filtered_df1_2[[
            "사업장명",
            "모집직종",
            "고용형태",
            "임금형태",
            "임금",
            "입사형태",
            "요구경력",
            "요구학력",
            "전공계열",
            "요구자격증",
            "사업장 주소",
            "기업형태",
            "담당기관",
            "등록일",
            "연락처",
            "대분류"
        ]])
        
        # Filter df2 based on selected job
        filtered_df2 = df2[df2['관련산업'].apply(lambda x: selected_job in x)]
        st.markdown("---")  # Separator between each item
        st.markdown("\n") 
        # Display filtered educational information
        st.markdown(f"<h3 style='text-align: center; color: #336699;'>{selected_job} 관련 무료 교육 정보:</h3>", unsafe_allow_html=True)

        # Iterating through rows of filtered_df2
        # Thumbnail size (adjust as needed)
        thumbnail_width = 300
        thumbnail_height = 300

        # Display thumbnails for the current page
        items_per_page = 5
        total_pages = (len(filtered_df2) + items_per_page - 1) // items_per_page
        current_page = st.number_input("페이지 선택", min_value=1, max_value=total_pages, value=1)
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = filtered_df2[start_idx:end_idx]
        
        for index, row in paginated_df.iterrows():
            thumbnail_html = f"""
             <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <div style="margin-right: 20px;">
                    <strong>과정명:</strong> {row['과정명']}<br>
                    <strong>카테고리:</strong> {row['카테고리']}<br>
                    <strong>교육분야:</strong> {row['교육분야']}<br>
                    <strong>차시목록명:</strong> {row['차시목록명']}<br>
                    <strong>교육내용:</strong> {row['교육내용']}<br>
                </div>
                <a href="{row['상세URL']}" target="_blank">
                    <img src="{row['썸네일이미지주소']}" style="width: {thumbnail_width}px; height: {thumbnail_height}px; object-fit: cover;">
                </a>
            </div>
            """
            st.markdown(thumbnail_html, unsafe_allow_html=True)
        
    elif menu_choice == '커뮤니티':
        st.markdown("<h4 style='text-align: center; color: #336699;'>커뮤니티</h4>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #000000;'>실시간으로 채용 정보를 공유해보세요🍀</h4>", unsafe_allow_html=True)
        st.markdown("---")  # Separator between each item
        st.markdown("\n") 

        # 게시판 기능 구현
        st.markdown("## 게시판")
        
        if 'posts' not in st.session_state:
            st.session_state['posts'] = []

        with st.form(key='community_form'):
            post_content = st.text_area("내용을 입력하세요", height=150)
            submit_button = st.form_submit_button("게시")

            if submit_button and post_content:
                st.session_state['posts'].append(post_content)
                st.success("게시글이 성공적으로 게시되었습니다.")
        
        # 게시글 출력
        if st.session_state['posts']:
            for i, post in enumerate(reversed(st.session_state['posts'])):  # 최신 글이 위에 오도록
                st.markdown(f"**익명 {i+1}**: {post}")
                if st.button(f"삭제 {i+1}", key=f"delete_{i}"):
                    st.session_state['posts'].pop(-i-1)  # 최신 글 삭제
                    st.experimental_rerun()
        
    # 고용 추천 서비스 세션 변수 초기화
    if menu_choice == '커뮤니티' or (menu_choice == '홈화면' and 'recommendation_made' in st.session_state):
        if 'user_info' in st.session_state:
            del st.session_state['user_info']
        if 'job_recommendations' in st.session_state:
            del st.session_state['job_recommendations']
        if 'recommendation_made' in st.session_state:
            del st.session_state['recommendation_made']
        
if __name__ == '__main__':
    main()
