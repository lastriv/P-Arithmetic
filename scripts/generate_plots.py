"""Computational experiment & SVG plot generator for P-Arithmetic.

Runs exact sweeps on toy universes (N_max = 100 and N_max = 1000) to locate:
1. Exact associativity-breaking thresholds: (a (+) b) (+) c != a (+) (b (+) c).
2. Quantum saturation thresholds: n (+) 1 == n.
3. Bounded Hubble's Law and Mass-Energy saturation curves.

Zero external dependencies: writes crisp SVG figures directly to plots/.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from p_arithmetic import (
    associativity_defect,
    bounded_hubble,
    bounded_hubble_tanh,
    bounded_mass_energy,
    bounded_mass_energy_tanh,
    p_add,
    saturation_threshold,
)

PLOTS_DIR = ROOT_DIR / "plots"

WIDTH = 760
HEIGHT = 460
PAD_L = 76
PAD_R = 30
PAD_T = 52
PAD_B = 58
PLOT_W = WIDTH - PAD_L - PAD_R
PLOT_H = HEIGHT - PAD_T - PAD_B


def _map_x(x: float, x_min: float, x_max: float) -> float:
    return PAD_L + ((x - x_min) / (x_max - x_min)) * PLOT_W


def _map_y(y: float, y_min: float, y_max: float) -> float:
    return PAD_T + PLOT_H - ((y - y_min) / (y_max - y_min)) * PLOT_H


def _polyline(points: list[tuple[float, float]], color: str, width: float = 2.5, dash: str = "") -> str:
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} points="{pts}" />'


def _svg_shell(
    title: str,
    x_label: str,
    y_label: str,
    x_ticks: list[tuple[float, str]],
    y_ticks: list[tuple[float, str]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    body: list[str],
    legend: list[tuple[str, str, str]],
    legend_pos: str = "top-left",
) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        f'<text x="{WIDTH / 2:.1f}" y="28" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="15.5" font-weight="600" fill="#111827">{xml_escape(title)}</text>',
    ]

    for xv, lbl in x_ticks:
        px = _map_x(xv, x_min, x_max)
        lines.append(f'<line x1="{px:.2f}" y1="{PAD_T}" x2="{px:.2f}" y2="{PAD_T + PLOT_H}" stroke="#e5e7eb" stroke-width="1" />')
        lines.append(f'<text x="{px:.2f}" y="{PAD_T + PLOT_H + 18}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" fill="#4b5563">{xml_escape(lbl)}</text>')

    for yv, lbl in y_ticks:
        py = _map_y(yv, y_min, y_max)
        lines.append(f'<line x1="{PAD_L}" y1="{py:.2f}" x2="{PAD_L + PLOT_W}" y2="{py:.2f}" stroke="#e5e7eb" stroke-width="1" />')
        lines.append(f'<text x="{PAD_L - 8}" y="{py + 4:.2f}" text-anchor="end" font-family="system-ui, sans-serif" font-size="11" fill="#4b5563">{xml_escape(lbl)}</text>')

    lines.append(f'<rect x="{PAD_L}" y="{PAD_T}" width="{PLOT_W}" height="{PLOT_H}" fill="none" stroke="#374151" stroke-width="1.2" />')
    lines.append(f'<text x="{PAD_L + PLOT_W / 2:.1f}" y="{HEIGHT - 14}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#1f2937">{xml_escape(x_label)}</text>')
    lines.append(
        f'<text x="18" y="{PAD_T + PLOT_H / 2:.1f}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#1f2937" transform="rotate(-90 18 {PAD_T + PLOT_H / 2:.1f})">{xml_escape(y_label)}</text>'
    )

    lines.extend(body)

    if legend:
        lw = 265
        lh = 20 * len(legend) + 12
        lx = PAD_L + 16 if legend_pos == "top-left" else PAD_L + PLOT_W - lw - 16
        ly = PAD_T + 14
        lines.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="4" fill="#ffffff" fill-opacity="0.92" stroke="#d1d5db" stroke-width="1" />')
        for idx, (label, color, dash) in enumerate(legend):
            cy = ly + 18 + idx * 20
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            lines.append(f'<line x1="{lx + 10}" y1="{cy}" x2="{lx + 34}" y2="{cy}" stroke="{color}" stroke-width="2.5"{dash_attr} />')
            lines.append(f'<text x="{lx + 42}" y="{cy + 4}" font-family="system-ui, sans-serif" font-size="11" fill="#111827">{xml_escape(label)}</text>')

    lines.append("</svg>")
    return "\n".join(lines)


def find_first_associativity_break(n_max: int) -> tuple[int, int, int, int] | None:
    """Find the minimal max(a, b, c) where (a (+) b) (+) c != a (+) (b (+) c)."""
    for s in range(1, n_max + 1):
        for a in range(1, s + 1):
            for b in range(a, s + 1):
                c = s
                d1 = associativity_defect(a, b, c, n_max)
                if d1 > 0:
                    return (a, b, c, d1)
                d2 = associativity_defect(a, c, b, n_max)
                if d2 > 0:
                    return (a, c, b, d2)
                d3 = associativity_defect(c, a, b, n_max)
                if d3 > 0:
                    return (c, a, b, d3)
    return None


def plot_associativity_threshold() -> tuple[tuple[int, int, int, int] | None, float]:
    """Incrementally sweep scale S in [1, 100] in O(N^3) and plot non-associative fraction."""
    n_max = 100
    n_sq = n_max * n_max
    first_break = find_first_associativity_break(n_max)

    # Precompute addition table for [0..n_max]^2 for fast O(N^3) incremental shell sweep.
    add_tbl = [
        [((a + b) * n_sq) // (n_sq + a * b) for b in range(n_max + 1)]
        for a in range(n_max + 1)
    ]

    broken_cum = 0
    frac_pts: list[tuple[float, float]] = []
    max_frac = 0.0

    for s in range(1, n_max + 1):
        # Count newly added triples (a, b, c) in [1, s]^3 with max(a, b, c) == s:
        # 1) c == s, a in [1, s-1], b in [1, s-1]  (symmetric with a == s, c in [1, s-1], b in [1, s-1])
        row_s = add_tbl[s]
        for a in range(1, s):
            row_a = add_tbl[a]
            for b in range(1, s):
                # (a, b, s) and (s, b, a) have identical associativity defect by commutativity
                if add_tbl[row_a[b]][s] != row_a[add_tbl[b][s]]:
                    broken_cum += 2
        # 2) b == s, a in [1, s-1], c in [1, s-1]
        for a in range(1, s):
            row_a = add_tbl[a]
            as_val = row_a[s]
            row_as = add_tbl[as_val]
            for c in range(1, s):
                if row_as[c] != row_a[row_s[c]]:
                    broken_cum += 1
        # 3) Exactly two coordinates equal s: (s, s, k), (k, s, s), (s, k, s) for k in [1, s-1]
        ss = row_s[s]
        row_ss = add_tbl[ss]
        for k in range(1, s):
            # (s, s, k) and (k, s, s) share identical defect; (s, k, s) is always associative by commutativity
            if row_ss[k] != row_s[row_s[k]]:
                broken_cum += 2
        # 4) (s, s, s) is always associative by commutativity.

        total = s * s * s
        frac = (broken_cum / total) * 100.0
        max_frac = max(max_frac, frac)
        frac_pts.append((_map_x(s, 0, n_max), _map_y(frac, 0, 100)))

    body: list[str] = []
    if first_break is not None:
        bx = _map_x(max(first_break[:3]), 0, n_max)
        body.append(f'<line x1="{bx:.2f}" y1="{PAD_T}" x2="{bx:.2f}" y2="{PAD_T + PLOT_H}" stroke="#dc2626" stroke-width="1.6" stroke-dasharray="6,4" />')
        label = xml_escape(f"Threshold S={max(first_break[:3])} {first_break[:3]}")
        body.append(
            f'<text x="{bx + 6:.2f}" y="{PAD_T + 26}" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#dc2626">{label}</text>'
        )

    body.append(_polyline(frac_pts, "#7c3aed", 2.5))

    svg = _svg_shell(
        title="Exact Associativity-Breaking Threshold & Non-Associative Fraction (N_max = 100)",
        x_label="Scale bound S (triples a, b, c in [1, S])",
        y_label="Non-associative triples (%)",
        x_ticks=[(0, "0"), (20, "20"), (40, "40"), (60, "60"), (80, "80"), (100, "100")],
        y_ticks=[(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")],
        x_min=0,
        x_max=n_max,
        y_min=0,
        y_max=100,
        body=body,
        legend=[
            ("Non-associative triples (%)", "#7c3aed", ""),
            ("First associativity break", "#dc2626", "6,4"),
        ],
        legend_pos="top-right",
    )
    (PLOTS_DIR / "associativity_threshold.svg").write_text(svg, encoding="utf-8")
    return first_break, max_frac


def plot_p_addition_saturation() -> None:
    n_max = 1000
    xs = list(range(0, n_max + 1, 10))
    y_max = 1400
    classical_pts = [(_map_x(a, 0, n_max), _map_y(a + 500, 0, y_max)) for a in xs if a + 500 <= y_max]
    p_pts = [(_map_x(a, 0, n_max), _map_y(p_add(a, 500, n_max), 0, y_max)) for a in xs]
    diag_pts = [(_map_x(a, 0, n_max), _map_y(p_add(a, a, n_max), 0, y_max)) for a in xs]
    horizon_y = _map_y(n_max, 0, y_max)

    body = [
        f'<line x1="{PAD_L}" y1="{horizon_y:.2f}" x2="{PAD_L + PLOT_W}" y2="{horizon_y:.2f}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="6,4" />',
        _polyline(classical_pts, "#9ca3af", 2.0, "4,4"),
        _polyline(p_pts, "#2563eb", 2.5),
        _polyline(diag_pts, "#059669", 2.5),
    ]
    svg = _svg_shell(
        title="P-Addition Saturation vs. Classical Addition (N_max = 1000)",
        x_label="Operand a",
        y_label="Result",
        x_ticks=[(0, "0"), (250, "250"), (500, "500"), (750, "750"), (1000, "1000")],
        y_ticks=[(0, "0"), (500, "500"), (1000, "1000 (N_max)"), (1400, "1400")],
        x_min=0,
        x_max=n_max,
        y_min=0,
        y_max=y_max,
        body=body,
        legend=[
            ("Classical: a + 500", "#9ca3af", "4,4"),
            ("P-Add: a (+) 500", "#2563eb", ""),
            ("P-Add: a (+) a", "#059669", ""),
            ("Horizon N_max = 1000", "#dc2626", "6,4"),
        ],
    )
    (PLOTS_DIR / "p_addition_saturation.svg").write_text(svg, encoding="utf-8")


def plot_associativity_defect() -> None:
    n_max = 1000
    a, c = 310, 830
    xs = list(range(0, n_max + 1, 5))
    defects = [associativity_defect(a, b, c, n_max) for b in xs]
    y_max = max(defects) + 1 if max(defects) > 0 else 2
    pts = [(_map_x(b, 0, n_max), _map_y(d, 0, y_max)) for b, d in zip(xs, defects)]

    body = [_polyline(pts, "#7c3aed", 2.0)]
    y_ticks = [(i, str(i)) for i in range(0, y_max + 1)]
    svg = _svg_shell(
        title=f"Associativity Defect |({a} (+) b) (+) {c} - {a} (+) (b (+) {c})| (N_max = 1000)",
        x_label="Middle operand b",
        y_label="Defect (units)",
        x_ticks=[(0, "0"), (250, "250"), (500, "500"), (750, "750"), (1000, "1000")],
        y_ticks=y_ticks,
        x_min=0,
        x_max=n_max,
        y_min=0,
        y_max=y_max,
        body=body,
        legend=[("Associativity defect", "#7c3aed", "")],
    )
    (PLOTS_DIR / "associativity_defect.svg").write_text(svg, encoding="utf-8")


def plot_bounded_hubble() -> None:
    c = 1000
    h = 10
    d_max = 300
    ds = list(range(0, d_max + 1, 2))
    y_max = 1400

    classical_pts = [(_map_x(d, 0, d_max), _map_y(h * d, 0, y_max)) for d in ds if h * d <= y_max]
    discrete_pts = [(_map_x(d, 0, d_max), _map_y(bounded_hubble(h, d, c), 0, y_max)) for d in ds]
    tanh_pts = [(_map_x(d, 0, d_max), _map_y(bounded_hubble_tanh(h, d, c), 0, y_max)) for d in ds]
    c_y = _map_y(c, 0, y_max)

    body = [
        f'<line x1="{PAD_L}" y1="{c_y:.2f}" x2="{PAD_L + PLOT_W}" y2="{c_y:.2f}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="6,4" />',
        _polyline(classical_pts, "#9ca3af", 2.0, "4,4"),
        _polyline(tanh_pts, "#f59e0b", 2.0, "5,3"),
        _polyline(discrete_pts, "#2563eb", 2.5),
    ]
    svg = _svg_shell(
        title="Bounded Hubble's Law: v(d) = H (x) d vs. Classical v = H * d (c = 1000, H = 10)",
        x_label="Distance d",
        y_label="Recession velocity v(d)",
        x_ticks=[(0, "0"), (100, "100"), (200, "200"), (300, "300")],
        y_ticks=[(0, "0"), (500, "500"), (1000, "1000 (c)"), (1400, "1400")],
        x_min=0,
        x_max=d_max,
        y_min=0,
        y_max=y_max,
        body=body,
        legend=[
            ("Classical: v = H * d", "#9ca3af", "4,4"),
            ("Discrete: H (x) d", "#2563eb", ""),
            ("Continuum: floor(c * tanh(Hd/c))", "#f59e0b", "5,3"),
            ("Speed of light horizon c = 1000", "#dc2626", "6,4"),
        ],
    )
    (PLOTS_DIR / "bounded_hubble.svg").write_text(svg, encoding="utf-8")


def plot_bounded_mass_energy() -> None:
    e_max = 1000
    rest = 25
    k_max = 120
    ks = list(range(0, k_max + 1, 1))
    y_max = 1400

    classical_pts = [(_map_x(k, 0, k_max), _map_y(k * rest, 0, y_max)) for k in ks if k * rest <= y_max]
    discrete_pts = [(_map_x(k, 0, k_max), _map_y(bounded_mass_energy(k, rest, e_max), 0, y_max)) for k in ks]
    tanh_pts = [(_map_x(k, 0, k_max), _map_y(bounded_mass_energy_tanh(k, rest, e_max), 0, y_max)) for k in ks]
    e_y = _map_y(e_max, 0, y_max)

    body = [
        f'<line x1="{PAD_L}" y1="{e_y:.2f}" x2="{PAD_L + PLOT_W}" y2="{e_y:.2f}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="6,4" />',
        _polyline(classical_pts, "#9ca3af", 2.0, "4,4"),
        _polyline(tanh_pts, "#f59e0b", 2.0, "5,3"),
        _polyline(discrete_pts, "#059669", 2.5),
    ]
    svg = _svg_shell(
        title="Bounded Mass-Energy: (mc^2) (x) k vs. Classical k * mc^2 (E_max = 1000, mc^2 = 25)",
        x_label="Particle count k",
        y_label="Total energy E_total",
        x_ticks=[(0, "0"), (40, "40"), (80, "80"), (120, "120")],
        y_ticks=[(0, "0"), (500, "500"), (1000, "1000 (E_max)"), (1400, "1400")],
        x_min=0,
        x_max=k_max,
        y_min=0,
        y_max=y_max,
        body=body,
        legend=[
            ("Classical: k * mc^2", "#9ca3af", "4,4"),
            ("Discrete: (mc^2) (x) k", "#059669", ""),
            ("Continuum: floor(E_max * tanh(...))", "#f59e0b", "5,3"),
            ("Energy horizon E_max = 1000", "#dc2626", "6,4"),
        ],
    )
    (PLOTS_DIR / "bounded_mass_energy.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    first_100, max_frac_100 = plot_associativity_threshold()
    first_1000 = find_first_associativity_break(1000)

    plot_p_addition_saturation()
    plot_associativity_defect()
    plot_bounded_hubble()
    plot_bounded_mass_energy()

    print("=== Computational Experiment Results ===")
    print(f"N_max = 100 : saturation_threshold = {saturation_threshold(100)}, first_asym_break = {first_100}, max_non_assoc_pct = {max_frac_100:.2f}%")
    print(f"N_max = 1000: saturation_threshold = {saturation_threshold(1000)}, first_asym_break = {first_1000}")
    print(f"Generated 5 SVG plots in {PLOTS_DIR}")


if __name__ == "__main__":
    main()
