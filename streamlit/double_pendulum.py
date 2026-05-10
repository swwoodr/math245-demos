import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Double Pendulum", layout="wide")
st.title("Double Pendulum")
st.markdown("A nonlinear ODE system — and a classic example of **deterministic chaos**.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    m1 = st.slider("Mass  m₁ (kg)", 0.1, 5.0, 1.0, 0.1)
    m2 = st.slider("Mass  m₂ (kg)", 0.1, 5.0, 1.0, 0.1)
    L1 = st.slider("Length  L₁ (m)", 0.2, 2.0, 1.0, 0.1)
    L2 = st.slider("Length  L₂ (m)", 0.2, 2.0, 1.0, 0.1)
    st.divider()
    st.header("Initial Conditions")
    th1_deg = st.slider("θ₁ initial (°)", -180, 180,  90, 5)
    th2_deg = st.slider("θ₂ initial (°)", -180, 180, 102, 5)
    st.caption("Both bobs start from rest.")
    st.divider()
    T = st.slider("Time span (s)", 5.0, 30.0, 20.0, 1.0)
    TRAIL = st.slider("Trail length (frames)", 10, 150, 60, 10)

# ── ODE ───────────────────────────────────────────────────────────────────────
G = 9.81

@st.cache_data
def solve_dp(m1, m2, L1, L2, th1_deg, th2_deg, T):
    th1_0 = np.radians(th1_deg)
    th2_0 = np.radians(th2_deg)

    def dp_ode(t, y):
        th1, w1, th2, w2 = y
        delta = th1 - th2
        D = 2 * m1 + m2 - m2 * np.cos(2 * delta)

        dw1 = (
            -G * (2 * m1 + m2) * np.sin(th1)
            - m2 * G * np.sin(th1 - 2 * th2)
            - 2 * np.sin(delta) * m2 * (w2**2 * L2 + w1**2 * L1 * np.cos(delta))
        ) / (L1 * D)

        dw2 = (
            2 * np.sin(delta) * (
                w1**2 * L1 * (m1 + m2)
                + G * (m1 + m2) * np.cos(th1)
                + w2**2 * L2 * m2 * np.cos(delta)
            )
        ) / (L2 * D)

        return [w1, dw1, w2, dw2]

    sol = solve_ivp(
        dp_ode, [0, T], [th1_0, 0.0, th2_0, 0.0],
        method="RK45", rtol=1e-8, atol=1e-10, dense_output=True,
    )
    t = np.linspace(0, T, 600)
    Y = sol.sol(t)
    return t, Y[0], Y[2]   # t, th1, th2

t_all, th1_all, th2_all = solve_dp(m1, m2, L1, L2, th1_deg, th2_deg, T)

x1 =  L1 * np.sin(th1_all)
y1 = -L1 * np.cos(th1_all)
x2 = x1 + L2 * np.sin(th2_all)
y2 = y1 - L2 * np.cos(th2_all)

# ── Animation frames ───────────────────────────────────────────────────────────
N_FRAMES  = 200
frame_idx = np.round(np.linspace(0, len(t_all) - 1, N_FRAMES)).astype(int)

frames = []
for fi in frame_idx:
    ti = t_all[fi]
    trail_start = max(0, fi - TRAIL)
    frames.append(go.Frame(
        name=f"{ti:.1f}",
        data=[
            go.Scatter(x=[0, x1[fi], x2[fi]],
                       y=[0, y1[fi], y2[fi]]),          # rods
            go.Scatter(x=[0, x1[fi], x2[fi]],
                       y=[0, y1[fi], y2[fi]]),          # bobs
            go.Scatter(x=x2[trail_start : fi + 1],
                       y=y2[trail_start : fi + 1]),     # trail
        ],
    ))

# ── Initial figure ─────────────────────────────────────────────────────────────
R = L1 + L2

fig = go.Figure(
    data=[
        go.Scatter(
            x=[0, x1[0], x2[0]], y=[0, y1[0], y2[0]],
            mode="lines",
            line=dict(color="#333333", width=3),
            showlegend=False,
        ),
        go.Scatter(
            x=[0, x1[0], x2[0]], y=[0, y1[0], y2[0]],
            mode="markers",
            marker=dict(
                color=["#222222", "royalblue", "crimson"],
                size=[10, 16, 16],
                line=dict(color="white", width=1),
            ),
            showlegend=False,
        ),
        go.Scatter(
            x=[x2[0]], y=[y2[0]],
            mode="lines",
            line=dict(color="rgba(200, 50, 50, 0.45)", width=1.5),
            showlegend=False,
        ),
    ],
    frames=frames,
)

# Pivot marker
fig.add_shape(type="circle", xref="x", yref="y",
              x0=-0.05, y0=-0.05, x1=0.05, y1=0.05,
              fillcolor="#222", line_color="#222")

fig.update_layout(
    height=520,
    margin=dict(l=20, r=20, t=65, b=90),
    plot_bgcolor="#f5f7fa",
    paper_bgcolor="white",
    xaxis=dict(range=[-(R + 0.2), R + 0.2],
               scaleanchor="y", scaleratio=1,
               showgrid=True, gridcolor="#e0e0e0",
               zeroline=True, zerolinecolor="#cccccc",
               showticklabels=False),
    yaxis=dict(range=[-(R + 0.2), 0.35],
               showgrid=True, gridcolor="#e0e0e0",
               zeroline=True, zerolinecolor="#cccccc",
               showticklabels=False),
    updatemenus=[dict(
        type="buttons", showactive=False,
        y=1.13, x=0.5, xanchor="center",
        buttons=[
            dict(label="▶  Play", method="animate",
                 args=[None, dict(frame=dict(duration=40, redraw=True),
                                  fromcurrent=True, mode="immediate")]),
            dict(label="⏸  Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False),
                                     mode="immediate")]),
        ],
    )],
    sliders=[dict(
        currentvalue=dict(prefix="t = ", suffix=" s", font=dict(size=12)),
        pad=dict(t=10, b=10),
        len=0.92, x=0.04,
        steps=[dict(
            method="animate",
            args=[[f.name], dict(mode="immediate",
                                  frame=dict(duration=0, redraw=True))],
            label=f.name if i % 25 == 0 else "",
        ) for i, f in enumerate(frames)],
    )],
)

st.plotly_chart(fig, use_container_width=True)

# ── Angle plot ─────────────────────────────────────────────────────────────────
fig2 = make_subplots(rows=1, cols=2,
                     subplot_titles=("Angle vs Time", "Phase Portrait (θ₁ vs θ₂)"))

fig2.add_trace(go.Scatter(x=t_all, y=np.degrees(th1_all), name="θ₁",
                           line=dict(color="royalblue", width=1.8)), row=1, col=1)
fig2.add_trace(go.Scatter(x=t_all, y=np.degrees(th2_all), name="θ₂",
                           line=dict(color="crimson", width=1.8)), row=1, col=1)
fig2.add_hline(y=0, line=dict(color="gray", width=1, dash="dash"), row=1, col=1)

fig2.add_trace(go.Scatter(
    x=np.degrees(th1_all), y=np.degrees(th2_all),
    mode="lines",
    line=dict(color="purple", width=1, ),
    name="Phase curve",
    showlegend=False,
), row=1, col=2)

fig2.update_xaxes(title_text="t (s)",    row=1, col=1)
fig2.update_yaxes(title_text="Angle (°)", row=1, col=1)
fig2.update_xaxes(title_text="θ₁ (°)",   row=1, col=2)
fig2.update_yaxes(title_text="θ₂ (°)",   row=1, col=2)

fig2.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=40, b=40),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend=dict(x=0.01, y=0.99),
)
st.plotly_chart(fig2, use_container_width=True)

# ── Chaos demo ────────────────────────────────────────────────────────────────
with st.expander("🔬 Sensitivity to Initial Conditions (Chaos)"):
    st.markdown(
        "The trajectory below adds a **1° perturbation** to θ₂. "
        "Watch how quickly the two solutions diverge — this exponential separation "
        "is the defining signature of **chaos**."
    )

    @st.cache_data
    def solve_dp_perturbed(m1, m2, L1, L2, th1_deg, th2_deg, T):
        return solve_dp(m1, m2, L1, L2, th1_deg, th2_deg + 1, T)

    _, th1_p, th2_p = solve_dp_perturbed(m1, m2, L1, L2, th1_deg, th2_deg, T)
    x2_p = L1 * np.sin(th1_p) + L2 * np.sin(th2_p)
    y2_p = -L1 * np.cos(th1_p) - L2 * np.cos(th2_p)
    dist = np.sqrt((x2 - x2_p) ** 2 + (y2 - y2_p) ** 2)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=t_all, y=dist,
                               line=dict(color="crimson", width=2),
                               fill="tozeroy", fillcolor="rgba(200,50,50,0.12)",
                               name="|Δr|"))
    fig3.update_layout(
        height=250,
        title="Distance between tip-2 trajectories (1° perturbation in θ₂)",
        xaxis_title="t (s)", yaxis_title="Distance (m)",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)
