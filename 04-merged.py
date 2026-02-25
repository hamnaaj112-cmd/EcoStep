"""
╔══════════════════════════════════════════════════════════════════════════╗
║                 EcoStep — Carbon Footprint Dashboard                     ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Emission Sources:                                                        ║
║ · DESNZ 2025 (UK Dept. for Energy Security & Net Zero)                   ║
║   → Petrol: 2.06916 kg CO2e/L                                            ║
║   → Diesel: 2.57082 kg CO2e/L                                            ║
║   → UK Grid: 0.43 kg CO2e/kWh                                            ║
║                                                                          ║
║ · Hannah Ritchie, Pablo Rosado, and Max Roser (2022) -                   ║
║   “Environmental Impacts of Food Production” Published online            ║
║   at OurWorldinData.org.                                                 ║
║   Source: https://ourworldindata.org/environmental-impacts-of-food       ║
║   → Dietary Greenhouse gas averages per food-system category             ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EcoStep · Carbon Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════════════
def initialize_session_state():
    defaults = {
        "fuel_type": "Petrol",
        "fuel_litres": 3.0,
        "ac_hours": 2.0,
        "tv_hours": 2.0,
        "laptop_hours": 4.0,
        "light_hours": 3.0,
        "diet_choice": "Mixed (Poultry / Fish)",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ══════════════════════════════════════════════════════════════════
#  CALCULATION 
# ══════════════════════════════════════════════════════════════════

# ── Transport  ────────────────────────────────
PETROL_FACTOR = 2.06916   # kg CO2e per litre
DIESEL_FACTOR = 2.57082   # kg CO2e per litre

# ── Electricity  ──────────────────────────────
GRID_FACTOR   = 0.43      # kg CO2e per kWh 

APPLIANCE_KW  = {          # Power draw in kWh per hour of use
    "AC (1.5 Ton)": 1.50,
    "TV (LED)":     0.10,
    "Laptop":       0.05,
    "Lights (LED)": 0.01,
}

# ── Diet  ───────────────────────────
DIET_FACTORS  = {
    "High Meat (Beef / Lamb)":          8.0,
    "Mixed (Poultry / Fish)":            4.0,
    "Vegetarian / Vegan (Plant-based)":  1.5,
}

# ── Context Conversion Factors ────────────────────────────────────
TREE_DAILY_ABS   = 0.057   # kg CO2e absorbed by one mature tree per day
PHONE_CHARGE_KG  = 0.008   # kg CO2e per smartphone full charge
KM_CAR_FACTOR    = 0.170   # kg CO2e per km average petrol car

# ── Carbon Grade Thresholds ───────────────────────────────────────
GRADE_LOW  = 12.0   # < 12 kg → Low
GRADE_HIGH = 50.0   # > 50 kg → High

def calc_transport(fuel_type: str, litres: float) -> float:
    if "Petrol" in fuel_type:
        return litres * PETROL_FACTOR
    elif "Diesel" in fuel_type:
        return litres * DIESEL_FACTOR
    return 0.0

def calc_electricity(hours: dict) -> tuple[float, float]:
    kwh = sum(hours[a] * APPLIANCE_KW[a] for a in APPLIANCE_KW)
    return kwh, kwh * GRID_FACTOR

def calc_diet(choice: str) -> float:
    return DIET_FACTORS.get(choice, 0.0)

def calc_totals(transport: float, electricity: float, diet: float) -> dict:
    total = transport + electricity + diet
    monthly = total * 30
    trees = total / TREE_DAILY_ABS if total > 0 else 0
    phones = total / PHONE_CHARGE_KG if total > 0 else 0
    km_eq = total / KM_CAR_FACTOR if total > 0 else 0

    if total < GRADE_LOW:
        grade, badge, badge_color = "Low", "Excellent", "#10b981"
    elif total <= GRADE_HIGH:
        grade, badge, badge_color = "Moderate", "Good", "#f59e0b"
    else:
        grade, badge, badge_color = "High", "Needs Work", "#ef4444"

    dominant = max(
        [("Transport", transport), ("Electricity", electricity), ("Diet", diet)],
        key=lambda x: x[1]
    )[0]

    return {
        "transport": transport,
        "electricity": electricity,
        "diet": diet,
        "total": total,
        "monthly": monthly,
        "trees": trees,
        "phones": phones,
        "km_eq": km_eq,
        "grade": grade,
        "badge": badge,
        "badge_color": badge_color,
        "dominant": dominant,
    }

def smart_tip(dominant: str) -> tuple[str, str]:
    tips = {
        "Transport": (
            "",
            "Your biggest footprint driver is **Transport**. Switching just "
            "2 days/week to public transit or cycling can cut your transport "
            "emissions by up to **40%**."
        ),
        "Electricity": (
            "",
            "Your biggest driver is **Energy Use**. Raising your AC thermostat "
            "by 2 °C and switching to LED bulbs could reduce your "
            "electricity emissions significantly."
        ),
        "Diet": (
            "",
            "Your biggest driver is **Diet**. One meat-free day per week saves "
            "roughly **0.5 tonnes CO₂e/year** — equivalent to planting 9 trees."
        ),
    }
    return tips.get(dominant)

# ══════════════════════════════════════════════════════════════════
#  HTML/CSS STYLING
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap');

/* ── Color System ── */
:root {
    --primary: #166534;
    --primary-dark: #14532d;
    --primary-light: #dcfce7;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg-light: #f0f4f0;
    --bg-white: #ffffff;
    --text-dark: #064e3b;
    --text-medium: #475569;
    --text-light: #64748b;
    --border: #e2e8f0;
}

/* ── Base Styling ── */
.stApp {
    background: #c3f7d6;
    font-family: 'Inter', sans-serif;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-dark);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', 'Inter', sans-serif !important;
    color: var(--text-dark) !important;
    font-weight: 600 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #064e3b 0%, #022c22 100%) !important;
    border-right: 1px solid #e5e7eb !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #88C28A !important;
}

/* ── Cards ── */
.insight-card {
    background: #FCFFFF;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;

    height: 175px;           
    display: flex;          
    flex-direction: column; 
    justify-content: center;
    text-align: center;  
}

.insight-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

/* ── Header ── */
.header-card {
    background: linear-gradient(180deg, #064e3b 0%, #022c22 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(22, 101, 52, 0.2);
}

.header-card h1 {
    color: white !important;
    margin: 0;
    font-size: 2.5rem;
}

.header-card p {
    color: rgba(255, 255, 255, 0.9);
    margin: 0.5rem 0 0 0;
}

/* ── Result ── */  
.result-card {
    background-color: #fcffff;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 15px;
}
            
.badge {
    display: inline-block;
}

.badge.badge-low {
    padding: 0.5rem 1rem;
    margin-top: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    border-radius: 777px;
    background-color: #d1fae5;
    color: #065f46;
}

.badge.badge-moderate {
    padding: 0.5rem 1rem;
    margin-top: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    border-radius: 777px;
    background-color: #fef3c7;
    color: #78350f;
}

.badge.badge-high {
    padding: 0.5rem 1rem;
    margin-top: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    border-radius: 777px;
    background-color: #fee2e2;
    color: #991b1b;
}

/* ── Result Metrics ── */         
[data-testid="stMetric"] {
    background-color: #fcffff;
    border: 2px solid #08a37c;
    border-radius: 12px !important;
    padding: 1.25rem !important;
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 48px !important;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
}
            
[data-testid="stNotification"] {
    background: #088564 !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #088564 !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
}

[data-testid="stExpander"] summary {
    color: white !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    padding: 1rem !important;
}
            

/* ── Buttons ── */
.stDownloadButton > button, .stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 2px 4px rgba(22, 101, 52, 0.2) !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover, .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] [role="slider"] {
    background: #C3F7D6 !important;
}

/* ── Selectboxes ── */
[data-testid="stSelectbox"] > div > div {
    background: #08c291 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ── Alert Boxes ── */
.stSuccess {
    background: #38A130 !important;
    border-left: 4px solid var(--success) !important;
    color: #065f46 !important;
}

.stWarning {
    background: #D9CD41 !important;
    border-left: 4px solid var(--warning) !important;
    color: #92400e !important;
}

.stError {
    background: #D94141 !important;
    border-left: 4px solid var(--danger) !important;
    color: #991b1b !important;
}

.stInfo {
    background: #588C5A !important;
    border-left: 4px solid var(--primary) !important;
    color: #588C5A !important;
}
            
/* ── Tip Card ── */
.st-do {
    background-color: #08C291 !important;
    color: white !important
}

/* ── Divider ── */
hr {
    border: none;
    border-top: 1px solid var(--border) !important;
    margin-bottom: 0.25rem 0 !important;
}

/* ── Caption ── */
.stCaption {
    color: black !important;
    font-size: 0.875rem !important;
}
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  main func
# ══════════════════════════════════════════════════════════════════
def main():
    # ── HEADER ────────────────────────────────────────────────────
    st.markdown("""
    <div class='header-card' style='text-align: center;'>
        <h1>EcoStep Carbon Calculator</h1>
        <p>Track your daily carbon footprint and discover ways to reduce it</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ───────────────────────────────────────────────────
    with st.sidebar:
        st.sidebar.markdown("""
        <div style='text-align: center;'>
        <h1 style='font-size: 3rem; margin-bottom: 0;'>EcoStep</h1>
        <p style='font-size: 1.2rem; font-weight: 600; color: #6b7280;'>Carbon Footprint Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        st.sidebar.markdown("""
        <div style='text-align: center; background-color: rgba(22, 101, 52, 0.05); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(22, 101, 52, 0.1);'>
        <h3 style='margin-top: 0;'> About</h3>
        <p style='font-size: 0.95rem; color: #374151;text-align: justify;'>
        EcoStep bridges the gap between daily habits and global impact. 
        Our engine calculates your personal carbon footprint across transport, 
        energy, and diet, providing instant visualizations and actionable 
        insights to help you navigate your journey toward a lower-carbon lifestyle.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.sidebar.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
        <h3 style='margin-bottom: 1rem;'> Impact Levels</h3>
        <div style='display: flex; flex-direction: column; gap: 10px; align-items: center;'>
        <div style='width: 90%; background-color: #28AD50; border: 1px solid #10b981; color: #065f46; padding: 10px; border-radius: 8px; font-weight: 600;'>
            Great (Under 12 kg CO₂e)
        </div>
        <div style='width: 90%; background-color: #E3C51B; border: 1px solid #f59e0b; color: #92400e; padding: 10px; border-radius: 8px; font-weight: 600;'>
            Okay (12-50 kg CO₂e)
        </div>
        <div style='width: 90%; background-color: #ED755A; border: 1px solid #ef4444; color: #991b1b; padding: 10px; border-radius: 8px; font-weight: 600;'>
            Needs a Look (Over 50 kg CO₂e)
        </div>
        </div>
        <p style='font-size: 0.8rem; color: #6b7280; margin-top: 10px;'>
        (Daily CO₂e per target)
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.expander("Data Sources"):
            st.markdown("""
            **Transport & Energy:**
            - UK DESNZ 2025
            - Petrol: 2.07 kg CO₂e/L
            - Diesel: 2.57 kg CO₂e/L
            - Grid: 0.43 kg CO₂e/kWh
                          
            **Diet:**
            - Hannah Ritchie, Pablo Rosado, and Max Roser (2022) -
              “Environmental Impacts of Food Production” Published online
              at OurWorldinData.org.
            - Dietary Greenhouse gas averages per food-system category
            """)
                    
        with st.expander("Tech Team"):
            st.markdown("""
            **Team Members:**          
            - Hamna Abdul Jaleel
            - Saad Mustafa
            - Sana Rafik
            """)

    # ── INPUT SECTION ─────────────────────────────────────────────
    st.markdown("## Enter Your Daily Data")
    st.success("Fill in your consumption data below to calculate your carbon footprint")

    col_input, col_results = st.columns([1.2, 0.8], gap="large")

    with col_input:

        # TRANSPORT
        with st.expander("♦ Transportation", expanded=True):
            fuel_type = st.selectbox(
                "Fuel Type",
                ["Petrol", "Diesel", "None (EV / Walk / Cycle)"],
                key="fuel_type",
            )
            
            if "None" not in fuel_type:
                fuel_litres = st.slider(
                    "Litres consumed today",
                    min_value=0.0,
                    max_value=80.0,
                    step=0.5,
                    key="fuel_litres",
                )
            else:
                st.session_state["fuel_litres"] = 0.0
                fuel_litres = 0.0

            transport_co2 = calc_transport(fuel_type, fuel_litres)
            
            if transport_co2 > 0:
                st.caption(f"{fuel_litres:.1f} L = **{transport_co2:.2f} kg CO₂e**")
            else:
                st.success("Zero emissions!")

        # ELECTRICITY
        with st.expander("♦ Electricity Usage", expanded=True):
            hours_used = {}
            for appliance, (key, lo, hi) in {
                "AC (1.5 Ton)": ("ac_hours", 0.0, 18.0),
                "TV (LED)": ("tv_hours", 0.0, 16.0),
                "Laptop": ("laptop_hours", 0.0, 16.0),
                "Lights (LED)": ("light_hours", 0.0, 24.0),
            }.items():
                kw = APPLIANCE_KW[appliance]
                hours_used[appliance] = st.slider(
                    f"--→  {appliance} ({kw} kWh/hr)",
                    min_value=lo,
                    max_value=hi,
                    step=0.5,
                    key=key,
                )

            elec_kwh, electricity_co2 = calc_electricity(hours_used)
            st.caption(f"Total: **{elec_kwh:.2f} kWh = {electricity_co2:.2f} kg CO₂e**")

        # DIET
        with st.expander("♦ Diet", expanded=True):
            diet_choice = st.selectbox(
                "Your typical daily diet",
                list(DIET_FACTORS.keys()),
                key="diet_choice",
            )
            
            diet_co2 = calc_diet(diet_choice)
            st.caption(f"Daily estimate: **{diet_co2:.1f} kg CO₂e**")


    # ── RESULTS SECTION ───────────────────────────────────────────
    with col_results:
        st.markdown("### Your Results")
        
        results = calc_totals(transport_co2, electricity_co2, diet_co2)
        total = results["total"]
        monthly = results["monthly"]
        grade = results["grade"]
        badge = results["badge"]
        badge_color = results["badge_color"]
        trees = results["trees"]
        phones = results["phones"]
        km_eq = results["km_eq"]
        dominant = results["dominant"]

        # Main result card
        icon = "🟢" if grade == "Low" else "🟡" if grade == "Moderate" else "🔴"
        badge_class = "badge-low" if grade == "Low" else "badge-moderate" if grade == "Moderate" else "badge-high"
        
        st.markdown(f"""
        <div class="result-card" style="border-color: {badge_color};">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 2rem; font-weight: 700; color: {badge_color}; margin-bottom: 0.25rem;">{total:.1f}</div>
            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">kg CO₂e per day</div>
            <div class="badge {badge_class}">{badge}</div>
        </div>
        """, unsafe_allow_html=True)

        # Feedback
        if grade == "Low":
            st.success("🌱 Excellent! Keep it up.")
        elif grade == "Moderate":
            st.warning("⚠️ Good, room to improve.")
        else:
            st.error("🔥 High impact. Make changes.")

        # Metrics
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Daily", f"{total:.1f} kg CO₂e")
        with m2:
            st.metric("Monthly", f"{monthly:.0f} kg CO₂e")

    # ── VISUALIZATION ─────────────────────────────────────────────
    if total > 0:
        st.markdown("---")
        st.markdown("## ↗ Emission Insights")

        viz_col1, viz_col2 = st.columns(2)

        values = [transport_co2, electricity_co2, diet_co2]
        labels = ["Transport", "Electricity", "Diet"]
        colors = ['#24753E', '#f59e0b', '#10b981']

        # Shared settings for both graphs
        graph_size = (6, 5)

        with viz_col1:
            fig, ax = plt.subplots(figsize=graph_size, facecolor='#FCFFFF')
            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                wedgeprops=dict(edgecolor='#FCFFFF', linewidth=2)
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, frameon=False)
            ax.set_title('Emissions Distribution', fontweight='bold', pad=15)
            
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with viz_col2:
            fig, ax = plt.subplots(figsize=graph_size, facecolor='#FCFFFF')
            bars = ax.barh(labels, values, color=colors, height=0.6)
            
            ax.set_xlabel('kg CO₂e', fontweight='bold')
            ax.set_title('Emissions by Category', fontweight='bold', pad=15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            
            for bar, val in zip(bars, values):
                ax.text(val + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{val:.2f}', va='center', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    # ── INSIGHTS ──────────────────────────────────────────────────
    if total > 0:
        st.markdown("---")
        st.markdown("## -> Insights")

        i1, i2, i3 = st.columns(3)

        with i1:
            st.markdown(f"""
            <div class='insight-card'>
                <h6 style='text-align: left; margin: 0 auto;'>Trees Needed</h6>
                <p style='font-size: 2rem; font-weight: 700; color: #10b981; margin: 0.5rem 0;'>{int(trees)}</p>
                <p style='font-size: 0.85rem; color: var(--text-light); margin: 0;'>
                    Mature trees needed daily to offset your emissions
                </p>
            </div>
            """, unsafe_allow_html=True)

        with i2:
            st.markdown(f"""
            <div class='insight-card'>
                <h6 style='text-align: left; margin: 0 auto;'>Phone Charges</h6>
                <p style='font-size: 2rem; font-weight: 700; color: #f59e0b; margin: 0.5rem 0;'>{int(phones)}</p>
                <p style='font-size: 0.85rem; color: var(--text-light); margin: 0;'>
                    Equivalent smartphone charges
                </p>
            </div>
            """, unsafe_allow_html=True)

        with i3:
            st.markdown(f"""
            <div class='insight-card'>
                <h6 style='text-align: left; margin: 0 auto;'>Driving Distance</h6>
                <p style='font-size: 2rem; font-weight: 700; color: #24753E; margin: 0.5rem 0;'>{km_eq:.1f} km</p>
                <p style='font-size: 0.85rem; color: var(--text-light); margin: 0;'>
                    Equivalent driving in petrol car
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Smart Tip
        st.markdown("---")
        tip_icon, tip_text = smart_tip(dominant)
        
        with st.expander(f"{tip_icon} Personalized Tip", expanded=True):
            st.info(tip_text)

    # ── EXPORT ────────────────────────────────────────────────────
    if total > 0:
        st.markdown("---")
        st.markdown("## ↓ Export Report")

        e1, e2 = st.columns(2)

        with e1:
            today_str = datetime.now().strftime("%Y-%m-%d")
            report_data = {
                'Category': ['Transport', 'Electricity', 'Diet', 'Total'],
                'kg CO₂e': [transport_co2, electricity_co2, diet_co2, total]
            }
            df = pd.DataFrame(report_data)
            csv = df.to_csv(index=False).encode()
            
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"carbon_report_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with e2:
            # Markdown Export
            md_report = f"""# Carbon Footprint Report
Date: {today_str}

## Summary
- Daily Total: {total:.2f} kg CO₂e
- Monthly Estimate: {monthly:.0f} kg CO₂e
- Grade: {grade}

## Breakdown
- Transport: {transport_co2:.2f} kg ({(transport_co2/total*100 if total > 0 else 0):.1f}%)
- Electricity: {electricity_co2:.2f} kg ({(electricity_co2/total*100 if total > 0 else 0):.1f}%)
- Diet: {diet_co2:.2f} kg ({(diet_co2/total*100 if total > 0 else 0):.1f}%)

## Context
- {int(trees)} trees needed
- {int(phones)} phone charges equivalent
- {km_eq:.1f} km driving equivalent
"""
            st.download_button(
                label="Download Markdown",
                data=md_report.encode(),
                file_name=f"carbon_report_{today_str}.md",
                mime="text/markdown",
                use_container_width=True
            )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.875rem; padding: 1rem 0;">
        <strong>EcoStep Carbon Calculator</strong><br>
        Tech Team 
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  RUN APPLICATION
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()