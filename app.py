import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


st.title("Batter vs Bowler Match-Ups in IPL")

# Load the data from a CSV file
df = pd.read_csv('all_matchesS.csv', low_memory=False)
df.head(1)

# Update season names to ensure consistency
df['season'] = df['season'].replace({'2007/08': '2008', '2009/10': '2010', '2020/21': '2020'})
df.season.unique()

# Format the start date column to match desired format
df['start_date'] = pd.to_datetime(df['start_date'])
df['start_date'] = df['start_date'].dt.strftime('%Y-%m-%d')

# Sort data by start_date, innings, and ball
df = df.sort_values(['start_date', 'innings', 'ball'], ascending=True)
df.head(1)

# Format the date column again to use in further steps
df['start_date'] = pd.to_datetime(df['start_date'])
df['start_date'] = df['start_date'].dt.strftime('%d-%m-%Y')

df.head(2)

# Filter for valid innings
df = df[(df['innings'] == 1) | (df['innings'] == 2)]

# Check unique seasons
df.season.unique()

df.head(1)

# Create a binary column for wickets taken by the bowler
df['wickets'] = df['player_dismissed']
df['wickets'] = df['wickets'].fillna(0)
df['wickets'] = np.where(df['wickets'] != 0, 1, 0)

# Create another binary column for valid wickets
df['b_wkt'] = df['wicket_type'].apply(lambda x: 1 if x not in ['run out', 'retired hurt', 'retired out', 'obstructing the field'] and x is not np.nan else 0)
df.head(2)

# Calculate total runs
df['total_runs'] = df['runs_off_bat'] + df['extras']
df.head(2)

# Select relevant columns for analysis
df = df[['match_id', 'season', 'start_date', 'venue', 'innings', 'ball',
         'batting_team', 'bowling_team', 'striker', 'non_striker', 'bowler', 'wickets', 'total_runs',
         'runs_off_bat', 'extras', 'wides', 'noballs', 'byes', 'legbyes',
         'penalty', 'wicket_type', 'player_dismissed', 'other_wicket_type',
         'other_player_dismissed', 'b_wkt']]
df.head(2)

# Add extra columns for bowler's runs conceded (including wides and no-balls)
df['b_runs'] = (df['runs_off_bat'] + df['wides'].fillna(0) + df['noballs'].fillna(0))
df.head(2)

df.replace({'RG Sharma': 'Rohit Sharma', 'V Kohli': 'Virat Kohli', 'SR Tendulkar':'Sachin Tendulkar', 'CV Varun': 'Varun Chakaravarthy', 'Z Khan': 'Zaheer Khan','JJ Bumrah':'Jasprit Bumrah'}, inplace=True)

# Function to calculate batting average (BAV)
def BAV(runs, outs):
    if outs > 0:
        return round(runs / outs, 1)
    else:
        return '-'

# Define some useful lists for the dropdowns
btl = sorted(list(df['striker'].unique()))
pcl = sorted(list(df['bowler'].unique()))
srtb = list(['Innings', 'Runs', 'Balls', 'Outs', 'Dots', '4s', '6s', 'Strike Rate'])
srth = list(['Descending', 'Ascending'])

# Apply custom CSS to style the app
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

col1, col2 = st.columns([1, 1])

with col1:
    batter = st.selectbox("**Select Batter:**", [''] + btl, index=0)

with col2:
    bowler = st.selectbox("**Select Bowler:**", [''] + pcl, index=0)

advanced_search = st.checkbox("Click here for advanced search")

if advanced_search:
    col3, col4 = st.columns([1, 1])

    with col3:
        # st.markdown("Select Sort Value: <span style='color:green;'>(Optional)</span>", unsafe_allow_html=True)
        sortby = st.selectbox("**Select Sort Value:**", [None] + srtb, index=0)

    with col4:
        # st.markdown("Select How: <span style='color:green;'>(Optional)</span>", unsafe_allow_html=True)
        how = st.selectbox("**Select How:**", [None] + srth, index=0)


# Submit button logic
    if st.button("Submit"):
        if batter == '' or bowler == '':
            st.warning("⚠️ Please select both a Batter and a Bowler before Submitting! 😊")
        elif sortby != None and how == None:  # Check if sortby is selected but how is empty
            st.warning("⚠️ If you selected a Sort Value, then please select How! 😊")
        elif sortby == None and how != None:  # Check if sortby is selected but how is empty
            st.warning("⚠️ If you selected How, then please select a Sort Value! 😊")
        else:
            st.subheader(f"{batter} vs {bowler} in IPL")

            # Define the function to display Batter vs Bowler stats
            def BvB(df, batter, bowler, sortby=None, how=None):
                df = df.copy()

                # Filter the data for the specific batter and bowler
                df = df[(df['striker'] == batter) & (df['bowler'] == bowler)]

                # If there's no data for the specified batter and bowler, return a styled message
                if df.empty:
                    df1 = pd.DataFrame({
                        'Year': ['-'],
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
                        lambda x: ['background-color: red']*len(x) if x.name == df1.index[-1] else ['']*len(x), axis=1)

                    return df1

                # Calculate additional columns: dots, fours, sixes
                df['dots'] = df['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
                df['four'] = df['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
                df['six'] = df['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

                # Group by season and calculate aggregates
                rdf = pd.DataFrame(df.groupby('season')['runs_off_bat'].sum()).reset_index().rename(columns={'season': 'Year', 'runs_off_bat': 'Runs'})
                bdf = pd.DataFrame(df.groupby('season')['ball'].count() - df.groupby('season')['wides'].count()).reset_index().rename(columns={'season': 'Year', 0: 'Balls'})
                wdf = pd.DataFrame(df.groupby('season')['b_wkt'].sum()).reset_index().rename(columns={'season': 'Year', 'b_wkt': 'Outs'})
                idf = pd.DataFrame(df.groupby('season')['match_id'].apply(lambda x: len(np.unique(x)))).reset_index().rename(columns={'season': 'Year', 'match_id': 'Innings'})
                ddf = (pd.DataFrame(df.groupby('season')['dots'].sum() - df.groupby('season')['wides'].count())).reset_index().rename(columns={'season': 'Year', 0: 'Dots'})
                fdf = pd.DataFrame(df.groupby('season')['four'].sum()).reset_index().rename(columns={'season': 'Year', 'four': '4s'})
                sdf = pd.DataFrame(df.groupby('season')['six'].sum()).reset_index().rename(columns={'season': 'Year', 'six': '6s'})

                # Merge all the grouped dataframes
                df = pd.merge(idf, rdf, on='Year').merge(bdf).merge(wdf).merge(ddf).merge(fdf).merge(sdf)

                # Calculate strike rate
                df['Strike Rate'] = round(df['Runs'] / df['Balls'] * 100, 1)

                # Select relevant columns and calculate average
                df = df[['Year', 'Innings', 'Runs', 'Balls', 'Outs', 'Dots', '4s', '6s', 'Strike Rate']]
                df['Avg'] = df.apply(lambda x: BAV(x['Runs'], x['Outs']), axis=1)

                # Modify sorting if sortby and how are provided
                if sortby and how:
                    if how == 'Ascending':
                        df = df.sort_values(by=sortby, ascending=True).reset_index(drop=True)
                    elif how == 'Descending':
                        df = df.sort_values(by=sortby, ascending=False).reset_index(drop=True)
                    else:
                        raise ValueError("Invalid value for 'how'. Choose 'Ascending' or 'Descending'.")

                # Calculate totals for all seasons
                totals = {
                    'Year': 'Total',
                    'Innings': df['Innings'].sum(),
                    'Runs': df['Runs'].sum(),
                    'Balls': df['Balls'].sum(),
                    'Outs': df['Outs'].sum(),
                    'Dots': df['Dots'].sum(),
                    '4s': df['4s'].sum(),
                    '6s': df['6s'].sum(),
                    'Strike Rate': round(df['Runs'].sum() / df['Balls'].sum() * 100, 1) if df['Balls'].sum() > 0 else '-',
                    'Avg': BAV(df['Runs'].sum(), df['Outs'].sum())
                }

                # Append totals row to the dataframe
                totals_df = pd.DataFrame([totals])  # Create a DataFrame from the totals dictionary
                df = pd.concat([df, totals_df], ignore_index=True)  #

                # Return the final dataframe with results
                df = df.style.set_caption('Download This Data Below :').format(
            {'Strike Rate': '{:.1f}', 'Avg': lambda x: f'{x:.1f}' if isinstance(x, (int, float)) else '-'}
        ).apply(lambda x: ['background-color: blue']*len(x) if x.name == df.index[-1] else [''] * len(x), axis=1)

                return df

            st.table(BvB(df, batter, bowler, sortby, how).hide(axis="index"))

            final_df = BvB(df, batter, bowler, sortby, how).data
            csv = final_df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name=f"{batter}_vs_{bowler}_IPL.csv", mime="text/csv")

else:
    if st.button("Submit"):
        if batter == '' or bowler == '':
            st.warning("⚠️ Please select both a Batter and a Bowler before Submitting! 😊")
        else:
            st.subheader(f"{batter} vs {bowler} in IPL")

            def BvB(df, batter, bowler):
                df = df.copy()

                df = df[(df['striker'] == batter) & (df['bowler'] == bowler)]

                if df.empty:
                    df1 = pd.DataFrame({
                        'Year': ['-'],
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
                        lambda x: ['background-color: red']*len(x) if x.name == df1.index[-1] else ['']*len(x), axis=1)
                    
                    return df1

                df['dots'] = df['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
                df['four'] = df['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
                df['six'] = df['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

                rdf = pd.DataFrame(df.groupby('season')['runs_off_bat'].sum()).reset_index().rename(columns={'season': 'Year', 'runs_off_bat': 'Runs'})
                bdf = pd.DataFrame(df.groupby('season')['ball'].count() - df.groupby('season')['wides'].count()).reset_index().rename(columns={'season': 'Year', 0: 'Balls'})
                wdf = pd.DataFrame(df.groupby('season')['b_wkt'].sum()).reset_index().rename(columns={'season': 'Year', 'b_wkt': 'Outs'})
                idf = pd.DataFrame(df.groupby('season')['match_id'].apply(lambda x: len(np.unique(x)))).reset_index().rename(columns={'season': 'Year', 'match_id': 'Innings'})
                ddf = (pd.DataFrame(df.groupby('season')['dots'].sum()-df.groupby('season')['wides'].count())).reset_index().rename(columns={'season': 'Year', 0: 'Dots'})
                fdf = pd.DataFrame(df.groupby('season')['four'].sum()).reset_index().rename(columns={'season': 'Year', 'four': '4s'})
                sdf = pd.DataFrame(df.groupby('season')['six'].sum()).reset_index().rename(columns={'season': 'Year', 'six': '6s'})

                df = pd.merge(idf, rdf, on='Year').merge(bdf).merge(wdf).merge(ddf).merge(fdf).merge(sdf)

                df['Strike Rate'] = round(df['Runs'] / df['Balls'] * 100, 1)
                df = df[['Year', 'Innings', 'Runs', 'Balls', 'Outs', 'Dots', '4s', '6s', 'Strike Rate']]
                df['Avg'] = df.apply(lambda x: BAV(x['Runs'], x['Outs']), axis=1)

                totals = {
                    'Year': 'Total',
                    'Innings': df['Innings'].sum(),
                    'Runs': df['Runs'].sum(),
                    'Balls': df['Balls'].sum(),
                    'Outs': df['Outs'].sum(),
                    'Dots': df['Dots'].sum(),
                    '4s': df['4s'].sum(),
                    '6s': df['6s'].sum(),
                    'Strike Rate': round(df['Runs'].sum() / df['Balls'].sum() * 100, 1) if df['Balls'].sum() > 0 else '-',
                    'Avg': BAV(df['Runs'].sum(), df['Outs'].sum())
                }

                df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)


                df = df.style.set_caption('Download This Data Below:').format(
                    {'Strike Rate': '{:.1f}', 'Avg': lambda x: f'{x:.1f}' if isinstance(x, (int, float)) else '-'}
                ).apply(lambda x: ['background-color: blue']*len(x) if x.name == df.index[-1] else [''] * len(x), axis=1)

                return df

            st.table(BvB(df, batter, bowler).hide(axis="index"))

            final_df = BvB(df, batter, bowler).data
            csv = final_df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name= batter+"_vs_"+bowler+"_IPL.csv", mime="text/csv") 
