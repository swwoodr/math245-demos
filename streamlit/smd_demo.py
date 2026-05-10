import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go

st.set_page_config(page_title="Spring-Mass-Damper", layout="wide")
st.title("Spring-Mass-Damper")
st.latex(r"m\,y'' + c\,y' + k\,y = 0")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    m = st.slider("Mass  m (kg)",            0.5,  5.0,  1.0, 0.1)
    c = st.slider("Damping  c",              0.0,  5.0,  0.4, 0.1)
    k = st.slider("Spring constant  k (N/m)", 1.0, 30.0, 12.0, 0.5)
    st.divider()
    st.header("Initial Conditions")
    y0_ic = st.slider("Displacement  y₀ (m)", -2.0, 2.0,  1.0, 0.1)
    v0_ic = st.slider("Velocity  v₀ (m/s)",   -5.0, 5.0,  0.0, 0.5)
    st.divider()
    T = st.slider("Time span (s)", 5.0, 30.0, 20.0, 1.0)

# ── Solve ODE ─────────────────────────────────────────────────────────────────
@st.cache_data
def solve_smd(m, c, k, y0_ic, v0_ic, T):
    sol = solve_ivp(
        lambda t, Y: [Y[1], -(c / m) * Y[1] - (k / m) * Y[0]],
        [0, T], [y0_ic, v0_ic],
        method="RK45", rtol=1e-8, atol=1e-10, dense_output=True,
    )
    t = np.linspace(0, T, 600)
    y = sol.sol(t)[0]
    return t, y

t_all, y_all = solve_smd(m, c, k, y0_ic, v0_ic, T)

# ── Display geometry ───────────────────────────────────────────────────────────
EQ_TOP   = 2.0        # equilibrium top-of-mass in display coords (y increases ↓)
SCALE    = 0.5        # physical displacement → display units
G_X0     = 2.0        # x where the graph starts
G_SCALE  = 3.8 / T   # seconds → display x-units

def disp(y_phys):
    return EQ_TOP + SCALE * y_phys

def make_spring(y_top, y_bot, xc=0.0, amp=0.15, n_coils=8):
    """Return (xs, ys) of a zigzag spring from y_top to y_bot."""
    if y_bot < y_top + 0.05:
        y_bot = y_top + 0.05
    pad   = 0.08 * (y_bot - y_top)
    y2, y3 = y_top + pad, y_bot - pad
    n_zigs = 2 * n_coils + 1
    yc = np.linspace(y2, y3, n_zigs + 1)
    xc_arr = np.where(np.arange(len(yc)) % 2 == 1, xc + amp, xc - amp).astype(float)
    xc_arr[[0, -1]] = xc
    xs = np.r_[xc, xc, xc_arr, xc, xc]
    ys = np.r_[y_top, y2, yc, y3, y_bot]
    return xs, ys

def make_mass(top, w=0.8, h=0.45):
    """Return (xs, ys) of a closed rectangle for the mass block."""
    l, r, bot = -w / 2, w / 2, top + h
    return [l, r, r, l, l], [top, top, bot, bot, top]

# ── Build animation frames ─────────────────────────────────────────────────────
N_FRAMES = 200
frame_idx = np.round(np.linspace(0, len(t_all) - 1, N_FRAMES)).astype(int)

frames = []
for fi in frame_idx:
    ti   = t_all[fi]
    mt   = disp(y_all[fi])
    sp_x, sp_y = make_spring(0.0, mt)
    mx,   my   = make_mass(mt)
    gx = G_X0 + G_SCALE * t_all[: fi + 1]
    gy = disp(y_all[: fi + 1])
    frames.append(go.Frame(
        name=f"{ti:.1f}",
        data=[
            go.Scatter(x=sp_x, y=sp_y),
            go.Scatter(x=mx,   y=my),
            go.Scatter(x=gx,   y=gy),
            go.Scatter(x=[gx[-1]], y=[gy[-1]]),
        ],
    ))

# ── Initial traces ─────────────────────────────────────────────────────────────
mt0 = disp(y_all[0])
sp_x0, sp_y0 = make_spring(0.0, mt0)
mx0,   my0   = make_mass(mt0)

fig = go.Figure(
    data=[
        go.Scatter(x=sp_x0, y=sp_y0, mode="lines",
                   line=dict(color="royalblue", width=2.5), showlegend=False),
        go.Scatter(x=mx0, y=my0, mode="lines",
                   fill="toself", fillcolor="#d94040",
                   line=dict(color="#900000", width=2), showlegend=False),
        go.Scatter(x=[G_X0], y=[disp(y_all[0])], mode="lines",
                   line=dict(color="royalblue", width=2), showlegend=False),
        go.Scatter(x=[G_X0], y=[disp(y_all[0])], mode="markers",
                   marker=dict(color="red", size=9), showlegend=False),
    ],
    frames=frames,
)

# Static shapes: ceiling bar + hatch marks + equilibrium dashed line
fig.add_shape(type="line", x0=-1.15, x1=1.15, y0=0, y1=0,
              line=dict(color="black", width=5))
for hx in np.linspace(-1.05, 1.05, 9):
    fig.add_shape(type="line", x0=hx, x1=hx - 0.12, y0=0, y1=-0.18,
                  line=dict(color="black", width=1))
x_graph_end = G_X0 + G_SCALE * T
fig.add_shape(type="line", x0=G_X0, x1=x_graph_end, y0=EQ_TOP, y1=EQ_TOP,
              line=dict(color="gray", width=1, dash="dash"))

# Axis tick annotations on the graph
t_ticks = np.linspace(0, T, 6)
for tt in t_ticks:
    xi = G_X0 + G_SCALE * tt
    fig.add_shape(type="line", x0=xi, x1=xi, y0=EQ_TOP - 0.06, y1=EQ_TOP + 0.06,
                  line=dict(color="gray", width=1))
    fig.add_annotation(x=xi, y=EQ_TOP + 0.22, text=f"{tt:.0f}",
                       showarrow=False, font=dict(size=10, color="gray"))
fig.add_annotation(x=G_X0 + G_SCALE * T / 2, y=EQ_TOP + 0.5,
                   text="t (s)", showarrow=False, font=dict(size=12, color="gray"))

# Y-axis range: ceiling near top, bottom below max displacement
amp_disp  = np.max(np.abs(y_all)) * SCALE
y_hi_data = EQ_TOP + amp_disp + 0.7   # bottom of figure (mass at max + block height)
y_lo_data = -0.55                       # top of figure (above ceiling hatch marks)

fig.update_layout(
    height=490,
    margin=dict(l=10, r=10, t=65, b=90),
    plot_bgcolor="#f5f7fa",
    paper_bgcolor="white",
    xaxis=dict(range=[-1.4, x_graph_end + 0.15],
               showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(range=[y_hi_data, y_lo_data],   # reversed: y_hi at bottom
               showgrid=False, zeroline=False, showticklabels=False),
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

# ── System analysis ────────────────────────────────────────────────────────────
omega_n = np.sqrt(k / m)
zeta    = c / (2 * np.sqrt(m * k))

if zeta < 1 - 1e-9:
    sys_type = "Underdamped"
elif zeta > 1 + 1e-9:
    sys_type = "Overdamped"
else:
    sys_type = "Critically Damped"

col1, col2, col3 = st.columns(3)
col1.metric("Natural Frequency ωₙ", f"{omega_n:.3f} rad/s")
col2.metric("Damping Ratio ζ",       f"{zeta:.3f}")
col3.metric("System Behavior",        sys_type)

st.markdown("**Characteristic equation** &nbsp; $r^2 + \\frac{c}{m}r + \\frac{k}{m} = 0$")
if zeta < 1 - 1e-9:
    omega_d = omega_n * np.sqrt(1 - zeta**2)
    st.latex(rf"r = -{zeta * omega_n:.3f} \pm {omega_d:.3f}\,i")
elif zeta > 1 + 1e-9:
    r1 = -zeta * omega_n + omega_n * np.sqrt(zeta**2 - 1)
    r2 = -zeta * omega_n - omega_n * np.sqrt(zeta**2 - 1)
    st.latex(rf"r_1 = {r1:.3f}, \qquad r_2 = {r2:.3f}")
else:
    st.latex(rf"r = -{zeta * omega_n:.3f} \text{{ (repeated root)}}")
