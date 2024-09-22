import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###

@st.cache
def load_data():
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")

    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")

    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000

    return df


# Uncomment the next line when finished
df = load_data()

### P1.2 ###


st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year = st.slider("Select Year", min_value=min_year, max_value=max_year, value=2012)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = st.radio(
    "Select Sex",
    options=["M", "F"],
    format_func=lambda x: "Male" if x == "M" else "Female")

subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
all_countries = df["Country"].unique().tolist()
countries = st.multiselect(
    "Select Countries", 
    options=all_countries, 
    default=[
        "Austria", 
        "Germany", 
        "Iceland", 
        "Spain", 
        "Sweden", 
        "Thailand", 
        "Turkey"
    ]
)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
all_cancers = df["Cancer"].unique().tolist()
cancer = st.selectbox(
    "Select Cancer Type", 
    options=all_cancers, 
    index=all_cancers.index("Leukaemia") 
)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

heatmap = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age", sort=ages, title="Age"),
    y=alt.Y("Country", title="Country"),
    color=alt.Color(
        "Rate",
        scale=alt.Scale(type="log", domain=[0.01, 1000], clamp=True),
        title="Mortality rate per 100k"
    ),
    tooltip=["Country", "Age", "Rate"]
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
    width=600,
    height=300
)
pop_aggregated = subset.groupby("Country").agg({"Pop": "sum"}).reset_index()

bar_chart = alt.Chart(pop_aggregated).mark_bar().encode(
    y=alt.Y("Country", sort="-x", title="Country"),
    x=alt.X("Pop:Q", title="Sum of population size"),
    tooltip=[
        alt.Tooltip("Pop:Q", title="Sum of Population Size"),
        alt.Tooltip("Country", title="Country")
    ]
).properties(
    width=600,
    height=200
)

final_chart = alt.vconcat(heatmap, bar_chart)
st.altair_chart(final_chart, use_container_width=True)

### P2.5 ###

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
