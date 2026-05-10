import streamlit as st
import numpy as np
from scipy.integrate import quad
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Riemann Sum Demo", layout="wide")
st.title("Riemann Integration")
st.markdown("Approximate $\\displaystyle\\int_a^b f(x)\\,dx$ using rectangles.")

# ── Function library ───────────────────────────────────────────────────────────
FUNCS = {
    "sin(x)":    (np.sin,                   r"\sin(x)",                 0.0,      np.pi),
    "cos(x)":    (np.cos,                   r"\cos(x)",                 0.0,  np.pi/2),
    "x²":        (lambda x: x**2,           r"x^2",                     0.0,      3.0),
    "x³ − 2x":   (lambda x: x**3 - 2*x,    r"x^3 - 2x",               -1.5,      2.0),
    "eˣ":        (np.exp,                   r"e^x",                     0.0,      2.0),
    "√x":        (np.sqrt,                  r"\sqrt{x}",                0.0,      4.0),
    "x · sin(x)":(lambda x: x*np.sin(x),   r"x\sin(x)",                0.0,  2*np.pi),
    "1/(1+x²)":  (lambda x: 1/(1+x**2),    r"\dfrac{1}{1+x^2}",       -3.0,      3.0),
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Function")
    fname = st.selectbox("f (x) =", list(FUNCS.keys()))
    f, f_latex, a_def, b_def = FUNCS[fname]

    st.header("Interval  [a, b]")
    a = st.number_input("a", value=float(round(a_def, 4)), step=0.1, format="%.3f")
    b = st.number_input("b", value=float(round(b_def, 4)), step=0.1, format="%.3f")

    st.header("Rectangles")
    n = st.slider("n", 1, 150, 10)

    st.header("Method")
    method = st.radio("Sample point", ["Left endpoint", "Right endpoint", "Midpoint"])

if a >= b:
    st.error("⚠️  a must be less than b.")
    st.stop()

# ── Compute Riemann sum ────────────────────────────────────────────────────────
dx       = (b - a) / n
x_left   = a + np.arange(n) * dx
x_right  = x_left + dx
x_mid    = x_left + dx / 2

sample_map = {"Left endpoint": x_left, "Right endpoint": x_right, "Midpoint": x_mid}
x_sample = sample_map[method]

heights       = f(x_sample)
riemann_sum   = float(np.sum(heights) * dx)
true_val, _   = quad(f, a, b)
abs_error     = abs(riemann_sum - true_val)
rel_error_pct = 100 * abs_error / abs(true_val) if true_val != 0 else float("nan")

# ── Smooth curve ───────────────────────────────────────────────────────────────
x_curve = np.linspace(a, b, 600)
y_curve = f(x_curve)

# ── Main plot ──────────────────────────────────────────────────────────────────
fig = go.Figure()

# Shaded true area (fill between curve and y = 0)
fig.add_trace(go.Scatter(
    x=x_curve, y=y_curve,
    fill="tozeroy",
    fillcolor="rgba(100, 170, 255, 0.18)",
    line=dict(width=0),
    name="True area",
    showlegend=True,
    hoverinfo="skip",
))

# Rectangles — one bar trace, bars centered between left/right endpoints
x_centers = x_left + dx / 2
fig.add_trace(go.Bar(
    x=x_centers,
    y=heights,
    width=dx,
    base=0,
    marker=dict(
        color="rgba(255, 155, 40, 0.50)",
        line=dict(color="rgba(200, 95, 0, 0.85)", width=1.2),
    ),
    name=f"{method} sum",
))

# Curve on top
fig.add_trace(go.Scatter(
    x=x_curve, y=y_curve,
    mode="lines",
    line=dict(color="royalblue", width=2.5),
    name=f"f(x) = {fname}",
))

# Sample points where heights are taken
fig.add_trace(go.Scatter(
    x=x_sample, y=heights,
    mode="markers",
    marker=dict(color="orangered", size=7, symbol="circle",
                line=dict(color="white", width=1)),
    name="Sample points",
))

fig.update_layout(
    height=460,
    margin=dict(l=20, r=20, t=50, b=40),
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0,
    bargroupgap=0,
    xaxis=dict(title="x", showgrid=True, gridcolor="#eeeeee",
               zeroline=True, zerolinecolor="#bbbbbb", zerolinewidth=1.5),
    yaxis=dict(title="y", showgrid=True, gridcolor="#eeeeee",
               zeroline=True, zerolinecolor="#bbbbbb", zerolinewidth=1.5),
    legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#cccccc", borderwidth=1),
    title=dict(
        text=f"$f(x) = {f_latex}$ &nbsp; on &nbsp; $[{a:.3g},\\,{b:.3g}]$ "
             f"&nbsp; — &nbsp; {n} rectangle{'s' if n > 1 else ''}, {method.lower()}",
        font=dict(size=15),
    ),
)

st.plotly_chart(fig, use_container_width=True)

# ── Metrics ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Riemann Sum",    f"{riemann_sum:+.6f}")
c2.metric("True Integral",  f"{true_val:+.6f}")
c3.metric("Absolute Error", f"{abs_error:.2e}")
c4.metric("Relative Error", f"{rel_error_pct:.3f}%" if not np.isnan(rel_error_pct) else "—")

st.latex(
    rf"\int_{{{a:.3g}}}^{{{b:.3g}}} {f_latex}\,dx \;\approx\; {riemann_sum:.6f}"
    rf"\qquad \text{{(true value: }} {true_val:.6f}\text{{)}}"
)

# ── Convergence plot ───────────────────────────────────────────────────────────
with st.expander("📉  Error Convergence vs. n  (all three methods)"):
    st.markdown(
        "How quickly does each method improve as you add more rectangles? "
        "Left/Right converge at **O(1/n)**; Midpoint at **O(1/n²)** — "
        "visible as a steeper slope on the log-log plot."
    )

    n_vals = np.arange(1, 251)
    conv_errors = {m: [] for m in ["Left endpoint", "Right endpoint", "Midpoint"]}

    for ni in n_vals:
        dxi  = (b - a) / ni
        xl   = a + np.arange(ni) * dxi
        for meth, xs in [("Left endpoint", xl),
                          ("Right endpoint", xl + dxi),
                          ("Midpoint",       xl + dxi / 2)]:
            rs = float(np.sum(f(xs)) * dxi)
            conv_errors[meth].append(abs(rs - true_val))

    colors = {"Left endpoint": "royalblue",
               "Right endpoint": "crimson",
               "Midpoint": "seagreen"}
    dashes  = {"Left endpoint": "solid",
                "Right endpoint": "dot",
                "Midpoint": "solid"}

    fig2 = go.Figure()
    for meth, errs in conv_errors.items():
        fig2.add_trace(go.Scatter(
            x=n_vals, y=errs,
            mode="lines",
            name=meth,
            line=dict(color=colors[meth], width=2, dash=dashes[meth]),
        ))

    # Reference lines O(1/n) and O(1/n²)
    ref_x = np.array([1, 250], dtype=float)
    scale = conv_errors["Left endpoint"][0]
    fig2.add_trace(go.Scatter(
        x=ref_x, y=scale / ref_x,
        mode="lines", name="O(1/n)",
        line=dict(color="gray", width=1.2, dash="dash"),
    ))
    fig2.add_trace(go.Scatter(
        x=ref_x, y=scale / ref_x**2,
        mode="lines", name="O(1/n²)",
        line=dict(color="goldenrod", width=1.2, dash="dash"),
    ))

    fig2.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=30, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(title="n (rectangles)", type="log",
                   showgrid=True, gridcolor="#eeeeee"),
        yaxis=dict(title="Absolute Error", type="log",
                   showgrid=True, gridcolor="#eeeeee"),
        legend=dict(x=0.99, y=0.99, xanchor="right",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#cccccc", borderwidth=1),
    )
    st.plotly_chart(fig2, use_container_width=True)
