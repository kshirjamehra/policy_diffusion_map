import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import numpy as np
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Global Policy Diffusion Map",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #303030;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- CLASS: SIMULATION ENGINE ---
class PolicySimulator:
    def __init__(self):
        # We start with a more comprehensive dataset of key global players
        self.data = pd.DataFrame({
            'country': [
                'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 
                'Netherlands', 'Sweden', 'Poland', 'Russia', 'China', 'Japan', 'South Korea', 
                'India', 'Singapore', 'Australia', 'New Zealand', 'Brazil', 'Mexico', 'Argentina', 
                'South Africa', 'Nigeria', 'Egypt', 'Saudi Arabia', 'UAE', 'Turkey', 'Israel', 
                'Indonesia', 'Vietnam', 'Thailand'
            ],
            'iso_alpha': [
                'USA', 'CAN', 'GBR', 'DEU', 'FRA', 'ITA', 'ESP', 
                'NLD', 'SWE', 'POL', 'RUS', 'CHN', 'JPN', 'KOR', 
                'IND', 'SGP', 'AUS', 'NZL', 'BRA', 'MEX', 'ARG', 
                'ZAF', 'NGA', 'EGY', 'SAU', 'ARE', 'TUR', 'ISR', 
                'IDN', 'VNM', 'THA'
            ],
            'region': [
                'North America', 'North America', 'Europe', 'Europe', 'Europe', 'Europe', 'Europe',
                'Europe', 'Europe', 'Europe', 'Europe', 'Asia', 'Asia', 'Asia',
                'Asia', 'Asia', 'Oceania', 'Oceania', 'South America', 'South America', 'South America',
                'Africa', 'Africa', 'Africa', 'Middle East', 'Middle East', 'Middle East', 'Middle East',
                'Asia', 'Asia', 'Asia'
            ],
            'resistance': np.random.uniform(0.1, 0.6, 31) # Random "resistance" to new policies
        })
        self.graph = self._build_network()

    def _build_network(self):
        """Constructs the influence graph."""
        G = nx.Graph()
        
        # Add nodes with metadata
        for _, row in self.data.iterrows():
            G.add_node(row['country'], region=row['region'], iso=row['iso_alpha'], resistance=row['resistance'])
        
        # Add Edges (Connections)
        countries = self.data['country'].tolist()
        
        # 1. Regional Blocs (High probability of connection)
        for i in range(len(countries)):
            for j in range(i + 1, len(countries)):
                c1, c2 = countries[i], countries[j]
                r1 = self.data[self.data['country'] == c1]['region'].values[0]
                r2 = self.data[self.data['country'] == c2]['region'].values[0]
                
                # If in same region, strong link
                if r1 == r2:
                    G.add_edge(c1, c2, weight=0.9)
                
                # Global strategic partners (simplified randomization for demo)
                elif np.random.random() < 0.15: 
                    G.add_edge(c1, c2, weight=0.3)
                    
        return G

    def run(self, patient_zero, policy_strength, years=10):
        """Runs the SIR (Susceptible-Infected-Recovered) simulation."""
        
        # Initial State
        status = {node: 'Susceptible' for node in self.graph.nodes()}
        status[patient_zero] = 'Adopted'
        
        history = []
        news_feed = []
        current_year = 2025
        
        # Add Year 0 state
        self._record_step(history, current_year, status)
        news_feed.append(f"{current_year}: Policy initiated in {patient_zero}")

        for year in range(1, years + 1):
            sim_year = current_year + year
            new_adopters = []
            
            # Logic: Iterate through all nodes
            for node in self.graph.nodes():
                if status[node] == 'Susceptible':
                    # Check neighbors
                    neighbors = list(self.graph.neighbors(node))
                    infected_neighbors = [n for n in neighbors if status[n] == 'Adopted']
                    
                    if len(infected_neighbors) > 0:
                        # Calculate Pressure
                        # More infected neighbors + High Policy Strength - Country Resistance
                        pressure = (len(infected_neighbors) * 0.1) + (policy_strength * 0.4)
                        resistance = self.graph.nodes[node]['resistance']
                        
                        chance = pressure - resistance
                        
                        # Roll dice
                        if np.random.random() < chance:
                            new_adopters.append(node)

            # Update Status
            for country in new_adopters:
                status[country] = 'Adopted'
                news_feed.append(f"{sim_year}: {country} adopts policy.")
            
            # Record Data
            self._record_step(history, sim_year, status)
            
            # Stop if world is saturated
            if all(s == 'Adopted' for s in status.values()):
                news_feed.append(f"{sim_year}: Global Saturation Reached.")
                break

        return pd.DataFrame(history), news_feed

    def _record_step(self, history, year, status):
        for node in self.graph.nodes():
            history.append({
                'Year': year,
                'Country': node,
                'Status': status[node],
                'ISO': self.graph.nodes[node]['iso'],
                'Color': 1 if status[node] == 'Adopted' else 0
            })

# --- UI LOGIC ---

def main():
    # Sidebar Controls
    st.sidebar.title("🛠️ Controls")
    
    sim = PolicySimulator()
    
    with st.sidebar.form("sim_form"):
        policy_name = st.text_input("Policy Name", value="New Regulation Protocol")
        origin_country = st.selectbox("Origin Country", sim.data['country'], index=0)
        
        st.markdown("---")
        st.write(" **Parameters**")
        strength = st.slider("Viral Strength", 0.1, 1.0, 0.5, 
                             help="Higher value = harder to resist.")
        duration = st.slider("Duration (Years)", 5, 25, 15)
        
        submitted = st.form_submit_button("Run Simulation ▶️")

    # Main Dashboard
    st.title("🌐 Global Policy Diffusion Map")
    st.markdown("### Interactive Simulation Model")
    
    if submitted:
        with st.spinner('Running network simulation...'):
            # Run the math
            df_res, news = sim.run(origin_country, strength, duration)
            time.sleep(1) # UX pause
        
        # --- TOP METRICS ---
        total_countries = len(sim.data)
        final_adopters = df_res[df_res['Year'] == df_res['Year'].max()]
        count_adopted = len(final_adopters[final_adopters['Status'] == 'Adopted'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Global Reach", f"{count_adopted}/{total_countries}", f"{int((count_adopted/total_countries)*100)}%")
        m2.metric("Start Year", "2025")
        m3.metric("End Year", df_res['Year'].max())
        
        st.markdown("---")

        # --- MAP VISUALIZATION ---
        col_map, col_news = st.columns([3, 1])
        
        with col_map:
            st.subheader(f"Diffusion: {policy_name}")
            fig = px.choropleth(
                df_res,
                locations="ISO",
                color="Status",
                animation_frame="Year",
                color_discrete_map={'Adopted': '#FF4B4B', 'Susceptible': '#2E3B4E'},
                hover_name="Country",
                projection="natural earth",
                title=""
            )
            fig.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin={"r":0,"t":0,"l":0,"b":0},
                height=500
            )
            st.plotly_chart(fig, width="stretch")

            # Area Chart for Adoption Curve
            st.subheader("📈 Adoption Velocity")
            adoption_counts = df_res[df_res['Status'] == 'Adopted'].groupby('Year').count()['Country'].reset_index()
            fig_line = px.area(adoption_counts, x='Year', y='Country', title="Cumulative Adoption Over Time", color_discrete_sequence=['#FF4B4B'])
            fig_line.update_layout(height=300)
            st.plotly_chart(fig_line, width="stretch")

        with col_news:
            st.subheader("📰 Live Ticker")
            st.markdown("*(Simulation Logs)*")
            
            news_container = st.container()
            with news_container:
                for item in news:
                    if "Saturation" in item:
                        st.success(item)
                    elif "initiated" in item:
                        st.info(item)
                    else:
                        st.markdown(f"• {item}")

        # --- EXPORT SECTION ---
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        csv = df_res.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📄 Download Simulation Report (CSV)",
            data=csv,
            file_name=f"diffusion_report_{policy_name.replace(' ', '_')}.csv",
            mime="text/csv",
        )

    else:
        # Empty State
        st.info("👈 Use the sidebar to configure the parameters and launch the simulation.")

if __name__ == "__main__":
    main()