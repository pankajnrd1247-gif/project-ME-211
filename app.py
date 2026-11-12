import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Multi-Axial Stress Failure Analysis
# The calculation functions below are kept the same as the original project.


def find_principal_stress(sigma_x, sigma_y, tau_xy):
    """Find principal stresses for plane stress."""
    average = (sigma_x + sigma_y) / 2
    radius = (((sigma_x - sigma_y) / 2) ** 2 + tau_xy ** 2) ** 0.5

    sigma_1 = average + radius
    sigma_2 = average - radius
    sigma_3 = 0

    return sigma_1, sigma_2, sigma_3


def calculate_failure(sigma_1, sigma_2, sigma_3, yield_strength, poisson):
    """Calculating equivalent stress and factor of safety for each theory."""

    # Rankine - Maximum Principal Stress Theory
    rankine = max(abs(sigma_1), abs(sigma_2), abs(sigma_3))

    # Tresca - Maximum Shear Stress Theory
    tresca = max(
        abs(sigma_1 - sigma_2),
        abs(sigma_2 - sigma_3),
        abs(sigma_3 - sigma_1)
    )

    # von Mises - Distortion Energy Theory
    von_mises = (
        0.5 * (
            (sigma_1 - sigma_2) ** 2
            + (sigma_2 - sigma_3) ** 2
            + (sigma_3 - sigma_1) ** 2
        )
    ) ** 0.5

    # Saint-Venant - Maximum Principal Strain Theory
    saint_venant = max(
        abs(sigma_1 - poisson * (sigma_2 + sigma_3)),
        abs(sigma_2 - poisson * (sigma_1 + sigma_3)),
        abs(sigma_3 - poisson * (sigma_1 + sigma_2))
    )

    # Haigh  - Maximum Strain Energy Theory
    haigh_value = (
        sigma_1**2 + sigma_2**2 + sigma_3**2
        - 2 * poisson * (
            sigma_1 * sigma_2 + sigma_2 * sigma_3 + sigma_3 * sigma_1
        )
    )
    haigh = max(0, haigh_value) ** 0.5

    names = ["Rankine", "Tresca", "von Mises", "Saint-Venant", "Haigh"]
    stresses = [rankine, tresca, von_mises, saint_venant, haigh]

    results = []
    for name, equivalent_stress in zip(names, stresses):
        if equivalent_stress == 0:
            fos = float("inf")
        else:
            fos = yield_strength / equivalent_stress

        status = "SAFE" if fos >= 1 else "FAILURE"
        results.append((name, equivalent_stress, fos, status))

    return results


def make_graph(results, yield_strength):
    """Browser version of the original equivalent-stress graph."""
    names = [row[0] for row in results]
    stresses = [row[1] for row in results]
    statuses = [row[3] for row in results]
    colors = ["steelblue" if status == "SAFE" else "orange" for status in statuses]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=stresses,
        marker_color=colors,
        text=[f"{value:.1f}" for value in stresses],
        textposition="outside",
        name="Equivalent stress"
    ))
    fig.add_hline(
        y=yield_strength,
        line_color="red",
        line_dash="dash",
        annotation_text=f"Yield strength = {yield_strength:.1f} MPa"
    )
    fig.update_layout(
        xaxis_title="Failure Theory",
        yaxis_title="Equivalent Stress (MPa)",
        height=430,
        plot_bgcolor="white",
        margin=dict(l=25, r=25, t=55, b=30),
        yaxis=dict(rangemode="tozero", gridcolor="lightgray")
    )
    return fig


st.set_page_config(
    page_title="Multi-Axial Stress Failure Analysis",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fb 0%, #edf2fa 100%);}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .hero {
        background: linear-gradient(110deg, #17324d, #176b87);
        padding: 25px; border-radius: 16px; color: white;
        margin-bottom: 20px;
    }
    .hero h1 {color: white; margin: 0;}
    .hero p {color: #eaf5fa; margin: 8px 0 0 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>MULTI-AXIAL STRESS FAILURE ANALYSIS</h1>
    <p>Enter your own stress and material values below (stress unit: MPa)</p>
</div>
""", unsafe_allow_html=True)

def clear_inputs():
    for key in ["sigma_x", "sigma_y", "tau_xy", "yield_strength", "poisson"]:
        st.session_state[key] = ""
    st.session_state.pop("calculation_results", None)


# Input section: same five inputs as the original Tkinter project.
st.subheader("Enter Input Values")

col1, col2 = st.columns(2)
with col1:
    sigma_x_text = st.text_input("Normal stress X (sigma_x)", key="sigma_x")
    sigma_y_text = st.text_input("Normal stress Y (sigma_y)", key="sigma_y")
    tau_xy_text = st.text_input("Shear stress (tau_xy)", key="tau_xy")
with col2:
    yield_text = st.text_input("Yield strength (Sy)", key="yield_strength")
    poisson_text = st.text_input("Poisson ratio", key="poisson")

button_col1, button_col2 = st.columns([1, 1])
with button_col1:
    calculate_clicked = st.button("Calculate", type="primary", use_container_width=True)
with button_col2:
    st.button("Clear All", use_container_width=True, on_click=clear_inputs)

if calculate_clicked:
    try:
        # Read all five values entered by the user, as in the original project.
        sigma_x = float(sigma_x_text)
        sigma_y = float(sigma_y_text)
        tau_xy = float(tau_xy_text)
        yield_strength = float(yield_text)
        poisson = float(poisson_text)

        if yield_strength <= 0:
            raise ValueError("Yield strength must be greater than zero.")

        if not 0 <= poisson <= 0.5:
            raise ValueError("Poisson ratio must be between 0 and 0.5.")

        # Calculate principal stresses
        sigma_1, sigma_2, sigma_3 = find_principal_stress(
            sigma_x, sigma_y, tau_xy
        )

        # Calculate all failure theories
        results = calculate_failure(
            sigma_1, sigma_2, sigma_3, yield_strength, poisson
        )

        st.session_state["calculation_results"] = {
            "principal": (sigma_1, sigma_2, sigma_3),
            "results": results,
            "yield_strength": yield_strength
        }

    except ValueError as error:
        st.error(
            "Please enter a valid number in every input box.\n\n" + str(error)
        )

if "calculation_results" in st.session_state:
    saved = st.session_state["calculation_results"]
    sigma_1, sigma_2, sigma_3 = saved["principal"]
    results = saved["results"]
    yield_strength = saved["yield_strength"]

    st.subheader("Principal Stresses")
    p1, p2, p3 = st.columns(3)
    p1.metric("Sigma 1", f"{sigma_1:.2f} MPa")
    p2.metric("Sigma 2", f"{sigma_2:.2f} MPa")
    p3.metric("Sigma 3", f"{sigma_3:.2f} MPa")

    st.subheader("Failure Theory Results")
    table_rows = []
    for name, stress, fos, status in results:
        fos_text = "Infinity" if fos == float("inf") else f"{fos:.3f}"
        table_rows.append({
            "Failure Theory": name,
            "Equivalent Stress (MPa)": f"{stress:.2f}",
            "Factor of Safety": fos_text,
            "Status": status
        })
    st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    # Find the theory with the lowest factor of safety
    governing = min(results, key=lambda row: row[2])
    name, stress, fos, status = governing
    fos_text = "Infinity" if fos == float("inf") else f"{fos:.3f}"

    final_text = (
        f"Governing theory: {name} | FOS: {fos_text} | Result: {status}"
    )
    if status == "SAFE":
        st.success(final_text)
    else:
        st.error(final_text)

    st.subheader("Equivalent Stress Graph")
    st.plotly_chart(make_graph(results, yield_strength), width="stretch")

    st.caption(
        "Blue bar = Safe | Orange bar = Failure | Red dashed line = Yield strength"
    )

st.caption("Multi-Axial Stress Failure Analysis")
