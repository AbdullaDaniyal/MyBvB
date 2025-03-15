import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(layout='wide')

df = pd.read_csv('all_matchesS.csv', low_memory=False)
df['season'] = df['season'].replace({'2007/08': '2008', '2009/10': '2010', '2020/21': '2020'})
df['start_date'] = pd.to_datetime(df['start_date'])
df['start_date'] = df['start_date'].dt.strftime('%Y-%m-%d')
df = df.sort_values(['start_date', 'innings', 'ball'], ascending=True)
df['start_date'] = pd.to_datetime(df['start_date'])
df['start_date'] = df['start_date'].dt.strftime('%d-%m-%Y')
df = df[(df['innings'] == 1) | (df['innings'] == 2)]
df['wickets'] = df['player_dismissed'].fillna(0)
df['wickets'] = np.where(df['wickets'] != 0, 1, 0)
df['b_wkt'] = df['wicket_type'].apply(lambda x: 1 if x not in ['run out', 'retired hurt', 'retired out', 'obstructing the field'] and x is not np.nan else 0)
df['total_runs'] = df['runs_off_bat'] + df['extras']
df.rename(columns={'season': 'Year', 'venue': 'Venue'}, inplace=True)
df = df[['match_id', 'Year', 'start_date', 'Venue', 'innings', 'ball',
             'batting_team', 'bowling_team', 'striker', 'non_striker', 'bowler', 'wickets', 'total_runs',
             'runs_off_bat', 'extras', 'wides', 'noballs', 'byes', 'legbyes',
             'penalty', 'wicket_type', 'player_dismissed', 'other_wicket_type',
             'other_player_dismissed', 'b_wkt']]
df['b_runs'] = (df['runs_off_bat'] + df['wides'].fillna(0) + df['noballs'].fillna(0))
    
def phase(ball):
    if ball < 6:
        return 'Powerplay'
    elif ball < 15:
        return 'Middle Overs'
    else:
        return 'Death Overs'
    
df['Overs'] = df['ball'].apply(lambda x: phase(x))

df.replace({'RG Sharma': 'Rohit Sharma', 'V Kohli': 'Virat Kohli', 'SR Tendulkar':'Sachin Tendulkar', 'CV Varun': 'Varun Chakaravarthy', 'Z Khan': 'Zaheer Khan','JJ Bumrah':'Jasprit Bumrah', 'SA Yadav':'Suryakumar Yadav', 'AC Gilchrist':'Adam Gilchrist', 'Green Park':'Green Park, Kanpur', 'Saurashtra Cricket Association Stadium':'Saurashtra Cricket Association Stadium, Rajkot', 'SK Raina':'Suresh Raina', 'UT Yadav':'Umesh Yadav', 'Wankhede Stadium':'Wankhede Stadium, Mumbai', 'HH Pandya':'Hardik Pandya', 'KH Pandya':'Krunal Pandya', 'DL Chahar':'Deepak Chahar', 'RD Chahar':'Rahul Chahar', 'R Ravindra':'Rachin Ravindra', 'BCJ Cutting':'Ben Cutting', 'KA Pollard':'Kieron Pollard', 'SR Watson':'Shane Watson', 'A Kumble':'Anil Kumble', 'SK Warne':'Shane Warne', 'MA Starc':'Mitchell Starc', 'CH Gayle':'Chris Gayle', 'B Lee':'Brett Lee', 'GJ Maxwell':'Glenn Maxwell', 'YS Chahal':'Yuzvendra Chahal', 'MG Johnson':'Mitchell Johnson'}, inplace=True)

def BAV(runs, outs):
    return round(runs / outs, 1) if outs > 0 else '-'



st.markdown("""
    <style>
    /* Ensure select boxes don't get covered */
    div[data-testid="stColumn"] {
        overflow: visible !important;
    }

    /* Make selectbox more user-friendly */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
        font-size: 16px;
    }

    /* Ensure dropdown opens beside the select box */
    div[data-testid="stSelectbox"] div[role="listbox"] {
        position: absolute !important;
        left: 100% !important;  /* Push dropdown to the right */
        top: 100% !important; /* Open below selectbox */
        width: 250px !important;
        z-index: 9999 !important; /* Ensure it appears above other elements */
    }

    /* Ensure the select box remains visible */
    div[data-testid="stSelectbox"] {
        overflow: visible !important;
    }

    /* Customize button */
    div.stButton > button:first-child {
        color: white !important;
        border-radius: 7.5px;
        font-weight: bold;
        padding: 10px 24px;
        border: 0.4px solid #007BFF !important;
    }

    div.stButton > button:first-child:hover {
        border: 1px solid #28a745 !important;
        box-shadow: 0px 0px 10px #28a745 !important;
    }

    /* Make the table horizontally scrollable */
    .stTable {
        display: block;
        overflow-x: auto;
        max-width: 100%;
        white-space: nowrap;
    }
        
    /* Ensure proper table layout */
    .stTable thead th, .stTable tbody td {
        text-align: center; /* Center align text in both header and body */
        padding: 10px;
        vertical-align: middle;
    }

    /* Sticky header and no-overflow */
    .stTable thead {
        position: sticky;
        top: 0;
        background-color: #333;
        z-index: 1;
    }

    /* Adjust column widths and prevent wrapping */
    .stTable td {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        text-align: center !important; /* Force center alignment for content */
    }
    </style>
""", unsafe_allow_html=True)


btl = sorted(list(df['striker'].unique()))
pcl = sorted(list(df['bowler'].unique()))
srtb = ['Innings', 'Runs', 'Balls', 'Outs', 'Dots', '4s', '6s', 'Strike Rate']
srth = ['Descending', 'Ascending']
grpb = ['Venue', 'Inning', 'Overs', 'Batting Team', 'Bowling Team', 'Batter', 'Bowler']
    

st.subheader("Features")

# Initialize the active feature if it doesn't exist
if "active_feature" not in st.session_state:
    st.session_state.active_feature = None

# If no feature has been selected, show the three buttons
if st.session_state.active_feature is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Batter vs Bowler MatchUp"):
            st.session_state.active_feature = "matchup"
            st.experimental_rerun()
    with col2:
        if st.button("Visualization"):
            st.session_state.active_feature = "visualization"
            st.experimental_rerun()
    with col3:
        if st.button("Innings Progression"):
            st.session_state.active_feature = "worm_chart"
            st.experimental_rerun()

# --- Feature: Batter vs Bowler MatchUp ---
if st.session_state.active_feature == "matchup":
    st.subheader("Batter vs Bowler Match-Ups in IPL")
    
    
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        Batter = st.selectbox("**Select Batter:**", [''] + btl, index=0)
    with col_b:
        Bowler = st.selectbox("**Select Bowler:**", [''] + pcl, index=0)
    with col_c:
        Groupby = st.selectbox("**Group By:**", ['Year'] + grpb, index=0)
    
    advanced_search = st.checkbox("Click here for advanced options")
    if advanced_search:
        col_d, col_e = st.columns(2)
        with col_d:
            sortby = st.selectbox("**Sort Value:**", [None] + srtb, index=0)
        with col_e:
            how = st.selectbox("**Sort By:**", [None] + srth, index=0)
    
    # Submit button logic
    if advanced_search:
        if st.button("Submit"):
            if Batter == '' or Bowler == '':
                st.warning("⚠️ Please select both Batter and Bowler before Submitting! 😊")
            elif sortby is not None and how is None:
                st.warning("⚠️ If you selected a Sort Value, then please select Sort By! 😊")
            elif sortby is None and how is not None:
                st.warning("⚠️ If you selected Sort By, then please select a Sort Value! 😊")
            else:
                with st.container():
                    st.write('---')
                    st.subheader(f"{Batter} vs {Bowler} in IPL")
                    # (Your BvB function and table display code goes here)
                    # For brevity, we'll assume BvB() returns the styled table.
                    def BvB(df, Batter, Bowler, Groupby, sortby=None, how=None):
                        df1 = df.copy()
                        df1 = df1[(df1['striker'] == Batter) & (df1['bowler'] == Bowler)]
                        df1.rename(columns={'striker': 'Batter', 'bowler': 'Bowler',
                                             'innings': 'Inning',
                                             'batting_team': 'Batting Team',
                                             'bowling_team': 'Bowling Team'}, inplace=True)
                        if df1.empty:
                            styled = pd.DataFrame({
                                Groupby: ['-'],
                                'Innings': ['-'],
                                'Runs': ['-'],
                                'Balls': ['-'],
                                'Outs': ['-'],
                                'Dots': ['-'],
                                '4s': ['-'],
                                '6s': ['-'],
                                'Strike Rate': ['-'],
                                'Avg': ['-']
                            }).style.set_caption('Not Faced Each Other').apply(
                                lambda x: ['background-color: red'] * len(x), axis=1)
                            return styled
                        df1['dots'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
                        df1['four'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
                        df1['six'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)
                        rdf = df1.groupby(Groupby)['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'Runs'})
                        bdf = (df1.groupby(Groupby)['ball'].count() - df1.groupby(Groupby)['wides'].count()).reset_index().rename(columns={0: 'Balls'})
                        wdf = df1.groupby(Groupby)['b_wkt'].sum().reset_index().rename(columns={'b_wkt': 'Outs'})
                        idf = df1.groupby(Groupby)['match_id'].nunique().reset_index().rename(columns={'match_id': 'Innings'})
                        ddf = (df1.groupby(Groupby)['dots'].sum() - df1.groupby(Groupby)['wides'].count()).reset_index().rename(columns={0: 'Dots'})
                        fdf = df1.groupby(Groupby)['four'].sum().reset_index().rename(columns={'four': '4s'})
                        sdf = df1.groupby(Groupby)['six'].sum().reset_index().rename(columns={'six': '6s'})
                        merged = idf.merge(rdf, on=Groupby)\
                                    .merge(bdf, on=Groupby)\
                                    .merge(wdf, on=Groupby)\
                                    .merge(ddf, on=Groupby)\
                                    .merge(fdf, on=Groupby)\
                                    .merge(sdf, on=Groupby)
                        merged['Strike Rate'] = merged.apply(lambda x: round(x['Runs'] / x['Balls'] * 100, 1)
                                                             if x['Balls'] > 0 else '-', axis=1)
                        merged['Avg'] = merged.apply(lambda x: BAV(x['Runs'], x['Outs']), axis=1)
                        if sortby and how:
                            if how == 'Ascending':
                                merged = merged.sort_values(by=[sortby, 'Innings'], ascending=[True, False]).reset_index(drop=True)
                            elif how == 'Descending':
                                merged = merged.sort_values(by=[sortby, 'Innings'], ascending=[False, True]).reset_index(drop=True)
                            else:
                                raise ValueError("Invalid value for 'how'.")
                        totals = {
                            Groupby: 'Total',
                            'Innings': merged['Innings'].sum(),
                            'Runs': merged['Runs'].sum(),
                            'Balls': merged['Balls'].sum(),
                            'Outs': merged['Outs'].sum(),
                            'Dots': merged['Dots'].sum(),
                            '4s': merged['4s'].sum(),
                            '6s': merged['6s'].sum(),
                            'Strike Rate': round(merged['Runs'].sum() / merged['Balls'].sum() * 100, 1)
                                           if merged['Balls'].sum() > 0 else '-',
                            'Avg': BAV(merged['Runs'].sum(), merged['Outs'].sum())
                        }
                        merged = pd.concat([merged, pd.DataFrame([totals])], ignore_index=True)
                        styled = merged.style.set_caption('Download This Data Below:').format(
                            {'Strike Rate': '{:.1f}', 'Avg': lambda x: f'{x:.1f}' if isinstance(x, (int, float)) else '-'}
                        ).apply(lambda x: ['background-color: blue'] * len(x) if x.name == merged.index[-1] else [''] * len(x), axis=1)
                        return styled
                    st.table(BvB(df, Batter, Bowler, Groupby, sortby, how).hide(axis="index"))
                    final_df = BvB(df, Batter, Bowler, Groupby, sortby, how).data
                    csv = final_df.to_csv(index=False)
                                    
                    if "csv_downloaded" not in st.session_state:
                        st.session_state.csv_downloaded = False

                    # Display download button only if data exists
                    if not st.session_state.csv_downloaded and not final_df.empty:
                        download_button = st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{Batter}_vs_{Bowler}_IPL.csv",
                            mime="text/csv",
                            on_click=lambda: st.session_state.update({"csv_downloaded": True})
                        )



    else:
        if st.button("Submit"):
            if Batter == '' or Bowler == '':
                st.warning("⚠️ Please select both Batter and Bowler before Submitting! 😊")
            else:
                with st.container():
                    st.write('---')
                    st.subheader(f"{Batter} vs {Bowler} in IPL")
                    def BvB(df, Batter, Bowler, Groupby):
                        df1 = df.copy()
                        df1 = df1[(df1['striker'] == Batter) & (df1['bowler'] == Bowler)]
                        df1.rename(columns={'striker': 'Batter', 'bowler': 'Bowler',
                                            'innings': 'Inning',
                                            'batting_team': 'Batting Team',
                                            'bowling_team': 'Bowling Team'}, inplace=True)
                        if df1.empty:
                            empty = pd.DataFrame({
                                Groupby: ['-'],
                                'Innings': ['-'],
                                'Runs': ['-'],
                                'Balls': ['-'],
                                'Outs': ['-'],
                                'Dots': ['-'],
                                '4s': ['-'],
                                '6s': ['-'],
                                'Strike Rate': ['-'],
                                'Avg': ['-']
                            })
                            empty = empty.style.set_caption('Not Faced Each Other').apply(lambda x: ['background-color: red'] * len(x), axis=1)
                            return empty
                        df1['dots'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
                        df1['four'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
                        df1['six'] = df1['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)
                        rdf = df1.groupby(Groupby)['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'Runs'})
                        bdf = (df1.groupby(Groupby)['ball'].count() - df1.groupby(Groupby)['wides'].count()).reset_index().rename(columns={0: 'Balls'})
                        wdf = df1.groupby(Groupby)['b_wkt'].sum().reset_index().rename(columns={'b_wkt': 'Outs'})
                        idf = df1.groupby(Groupby)['match_id'].nunique().reset_index().rename(columns={'match_id': 'Innings'})
                        ddf = (df1.groupby(Groupby)['dots'].sum() - df1.groupby(Groupby)['wides'].count()).reset_index().rename(columns={0: 'Dots'})
                        fdf = df1.groupby(Groupby)['four'].sum().reset_index().rename(columns={'four': '4s'})
                        sdf = df1.groupby(Groupby)['six'].sum().reset_index().rename(columns={'six': '6s'})
                        merged = idf.merge(rdf, on=Groupby)\
                                    .merge(bdf, on=Groupby)\
                                    .merge(wdf, on=Groupby)\
                                    .merge(ddf, on=Groupby)\
                                    .merge(fdf, on=Groupby)\
                                    .merge(sdf, on=Groupby)
                        merged['Strike Rate'] = merged.apply(lambda x: round(x['Runs'] / x['Balls'] * 100, 1)
                                                             if x['Balls'] > 0 else '-', axis=1)
                        merged['Avg'] = merged.apply(lambda x: BAV(x['Runs'], x['Outs']), axis=1)
                        totals = {
                            Groupby: 'Total',
                            'Innings': merged['Innings'].sum(),
                            'Runs': merged['Runs'].sum(),
                            'Balls': merged['Balls'].sum(),
                            'Outs': merged['Outs'].sum(),
                            'Dots': merged['Dots'].sum(),
                            '4s': merged['4s'].sum(),
                            '6s': merged['6s'].sum(),
                            'Strike Rate': round(merged['Runs'].sum() / merged['Balls'].sum() * 100, 1)
                                           if merged['Balls'].sum() > 0 else '-',
                            'Avg': BAV(merged['Runs'].sum(), merged['Outs'].sum())
                        }
                        merged = pd.concat([merged, pd.DataFrame([totals])], ignore_index=True)
                        styled = merged.style.set_caption('Download This Data Below:').format(
                            {'Strike Rate': '{:.1f}', 'Avg': lambda x: f'{x:.1f}' if isinstance(x, (int, float)) else '-'}
                        ).apply(lambda x: ['background-color: blue'] * len(x) if x.name == merged.index[-1] else [''] * len(x), axis=1)
                        return styled
                    

                    st.table(BvB(df, Batter, Bowler, Groupby).hide(axis="index"))

                    if "final_df" not in st.session_state:
                        st.session_state["final_df"] = BvB(df, Batter, Bowler, Groupby).data
                        st.session_state["csv_data"] = st.session_state["final_df"].to_csv(index=False)

                    # Render download button without causing a rerun
                    csv_data = st.session_state.get("csv_data", None)
                    if csv_data:
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"{Batter}_vs_{Bowler}_IPL.csv",
                            mime="text/csv",
                            key="download_button"
                        )












elif st.session_state.active_feature == "visualization":
    st.subheader("Visualization")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Player Runs vs Teams", key="btn_player_runs_vs_teams"):
            st.session_state.active_viz = "player_runs_vs_teams"
    with col2:
        if st.button("Player Runs vs Bowlers", key="btn_player_runs_vs_bwl"):
            st.session_state.active_viz = "player_runs_vs_bowler"
    with col3:
        if st.button("Players Most Dismissal Type", key="PDT"):
            st.session_state.active_viz = "player_dismissal_type"

    if st.session_state.get("active_viz") == "player_runs_vs_teams":
        with st.container():
            st.write('---')
            st.subheader("Player Runs vs Teams")
            
            batter = st.selectbox("**Select Batter:**", [''] + btl, index=0, key="select_batter_prvt")
            
            if st.button("Generate Stats", key="generate_chart_main"):
                with st.container():
                    st.write('---')
                    # st.subheader(batter + ' Runs vs Each Opponent')

                    def BOD(df, batter):
                        df = df.copy()
                        df = df[df['striker'] == batter]
                        if df.empty:
                            st.warning("No data available for this batter!")
                            return None, None
                        
                        team = df['batting_team'].iloc[-1]
                        
                        df = df.groupby('bowling_team', as_index=False)['runs_off_bat'].sum()
                        df = df.sort_values(by='runs_off_bat', ascending=True).rename(
                            columns={'bowling_team': 'Opponent', 'runs_off_bat': 'Runs'}
                        )
                        total_runs = df['Runs'].sum()
                        
                        chart = (
                                alt.Chart(df)
                                .mark_bar()
                                .encode(
                                    x=alt.X('Runs:Q', title='Runs'),
                                    y=alt.Y('Opponent:N', sort='-x', title='Opponent'),
                                    tooltip=['Opponent', 'Runs']
                                )
                                .properties(
                                    # Keep the title shorter
                                    title=f"{batter} [{team}] : {total_runs} Runs",height=480
                                    # Remove the fixed height if you want it to shrink to fit
                                    # height=500
                                )
                                .configure_axis(labelFontSize=12, titleFontSize=12)
                                .configure_title(fontSize=15)
                            )

                        return chart, df

                    chart, df = BOD(df, batter)
                    
                    if chart is not None:
                        st.session_state["chart"] = chart
                        st.session_state["df"] = df

            if "chart" in st.session_state:
                st.altair_chart(st.session_state["chart"], use_container_width=True)

            if "df" in st.session_state:
                csv = st.session_state["df"].to_csv(index=False)
                st.download_button("Download Data", data=csv, file_name=f"{batter}_runs_vs_opponents.csv", mime="text/csv")




    elif st.session_state.get("active_viz") == "player_runs_vs_bowler":
        with st.container():
            st.write('---')
            st.subheader("Player Runs vs Bowlers")
            
            batter = st.selectbox("**Select Batter:**", [''] + btl, index=0, key="select_batter_prvt")

            if st.button("Generate Stats", key="generate_chart_main"):
                with st.container():
                    st.write('---')
                    # st.subheader(batter + ' Runs vs Each Bowler')

                    def BBD(df, batter):
                        df = df.copy()
                        df = df[df['striker'] == batter]

                        if df.empty:
                            st.warning("No data available for this batter!")
                            return None, None

                        team = df['batting_team'].iloc[-1]

                        df = (df.groupby('bowler')['runs_off_bat'].sum()
                            .reset_index()
                            .rename(columns={'bowler': 'Bowler', 'runs_off_bat': 'Runs'})
                            .sort_values(by='Runs', ascending=True))

                        total_runs = df['Runs'].sum()

                        chart = (
                            alt.Chart(df.tail(20))
                            .mark_bar()
                            .encode(
                                x=alt.X('Runs:Q', title='Runs'),
                                y=alt.Y('Bowler:N', sort='-x', title='Bowler'),
                                tooltip=['Bowler', 'Runs']
                            )
                            .properties(
                                title=f"{batter} [{team}] : {total_runs} Runs vs Bowlers", height=550
                            )
                            .configure_axis(labelFontSize=11, titleFontSize=12)
                            .configure_title(fontSize=13)
                        )

                        return chart, df

                    chart, df = BBD(df, batter)
                    
                    if chart is not None:
                        st.session_state["chart_bowlers"] = chart
                        st.session_state["df_bowlers"] = df

            if "chart_bowlers" in st.session_state:
                st.altair_chart(st.session_state["chart_bowlers"], use_container_width=True)

            if "df_bowlers" in st.session_state:
                csv = st.session_state["df_bowlers"].to_csv(index=False)
                st.download_button("Download Data", data=csv, file_name=f"{batter}_runs_vs_bowlers.csv", mime="text/csv")




    elif st.session_state.get("active_viz") == "player_dismissal_type":
        with st.container():
            st.write('---')
            st.subheader("Player Most Dismissal Type")
            
            batter = st.selectbox("**Select Batter:**", [''] + btl, index=0, key="select_batter_prvt")
            
            if st.button("Generate Stats", key="generate_chart_main"):
                with st.container():
                    st.write('---')

                    def DWT(df, batter):

                        df = df.copy()
                        df = df[df['player_dismissed']==batter]
                        df = df[(df['wicket_type']!='retired hurt') & (df['wicket_type']!='retired out')]
                        runs = df['wickets'].sum()
                        
                        team = df['batting_team'].iloc[-1]

                        df = pd.DataFrame(df.groupby('wicket_type')['wickets'].sum()).reset_index().sort_values(by='wickets', ascending=True).rename(columns={'wicket_type':'Dismissal Type','wickets':'Wickets'})

                        def capitalize_first_last(w):
                            words = w.split()
                            if len(words) == 1:
                                return words[0].capitalize()
                            words[0] = words[0].capitalize()
                            words[-1] = words[-1].capitalize()
                            return ' '.join(words)
                        
                        df['Dismissal Type'] = df['Dismissal Type'].apply(capitalize_first_last)
                        
                        chart = (
                            alt.Chart(df)
                            .mark_bar()
                            .encode(
                                x=alt.X('Wickets:Q', title='Wickets'),
                                y=alt.Y('Dismissal Type:N', sort='-x', title='Dismissal Type'),
                                tooltip=['Dismissal Type', 'Wickets']
                            )
                            .properties(
                                title=batter+ ' ['+team+'] : ' +str(runs)+ ' Dismissals Classifcation in IPL ', height=550
                            )
                            .configure_axis(labelFontSize=11, titleFontSize=12)
                            .configure_title(fontSize=13)
                        )

                        return chart, df

                    chart, df = DWT(df, batter)
                    
                    if chart is not None:
                        st.session_state["chart_bowlers"] = chart
                        st.session_state["df_bowlers"] = df

            if "chart_bowlers" in st.session_state:
                st.altair_chart(st.session_state["chart_bowlers"], use_container_width=True)

            if "df_bowlers" in st.session_state:
                csv = st.session_state["df_bowlers"].to_csv(index=False)
                st.download_button("Download Data", data=csv, file_name=f"{batter}_most_dismissal_type.csv", mime="text/csv")














# --- Feature: Innings Progression (Worm Chart) ---
elif st.session_state.active_feature == "worm_chart":
    st.subheader("Innings Progression (Worm Chart)")
    st.write("Coming Soon....")
    # (Insert your worm chart code here)
