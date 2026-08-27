#!/usr/bin/env python3
"""Render the published throughput chart from benchmarks/results.json."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks/results.json"
OUTPUT = ROOT / "docs/benchmark.svg"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def system_points(system: dict) -> list[dict]:
    return list(system["context_scaling"])


def render(data: dict) -> str:
    default = data["systems"][data["default_system"]]
    reference = data["systems"]["rocm-rocmfpx"]
    series = [
        ("default", default["name"], system_points(default)),
        ("reference", reference["name"], system_points(reference)),
    ]
    x0, main_x1 = 92.0, 745.0
    outlier_x0, outlier_x, outlier_x1 = 765.0, 807.5, 850.0
    main_max = 262144

    def x(value: int) -> float:
        if value <= main_max:
            return x0 + value / main_max * (main_x1 - x0)
        return outlier_x

    panels = [
        ("Input processing", "prefill_tokens_per_second", 145.0, 170.0, 280.0),
        ("Generation", "decode_tokens_per_second", 420.0, 170.0, 45.0),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 710" role="img" aria-labelledby="title description">',
        '  <title id="title">Cold-retrieval throughput by prompt length</title>',
        '  <desc id="description">Input-processing and generation throughput for Strix Halo llama.cpp Vulkan IQ3_XXS and the Lucebox ROCm ROCmFPX leading alternative using the same cold five-key retrieval workload. The main horizontal segment is linear from zero through 262,144 tokens; the 491,520-token measurement is isolated after an explicit axis break. The Lucebox result is shown at 122,879 tokens.</desc>',
        "  <style>",
        "    .background { fill: #ffffff; }",
        "    .frame { fill: none; stroke: #d0d7de; stroke-width: 1; }",
        "    .grid { stroke: #d8dee4; stroke-width: 1; stroke-dasharray: 3 5; }",
        "    .axis { stroke: #57606a; stroke-width: 1.25; }",
        "    .default-line { fill: none; stroke: #0969da; stroke-width: 3; }",
        "    .default-mark { fill: #0969da; }",
        "    .reference-mark { fill: #bf3989; }",
        '    text { fill: #24292f; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }',
        "    .chart-title { font-size: 22px; font-weight: 600; }",
        "    .legend { font-size: 12px; font-weight: 500; }",
        "    .panel-title { font-size: 16px; font-weight: 600; }",
        "    .tick { font-size: 11px; }",
        "    .value { font-size: 11px; font-weight: 600; }",
        "    .note { font-size: 11px; fill: #57606a; }",
        "    .axis-title { font-size: 13px; font-weight: 500; }",
        "    @media (prefers-color-scheme: dark) {",
        "      .background { fill: #0d1117; } .frame, .grid { stroke: #30363d; }",
        "      .axis { stroke: #8b949e; } .default-line { stroke: #58a6ff; }",
        "      .default-mark { fill: #58a6ff; } .reference-mark { fill: #db61a2; }",
        "      text { fill: #e6edf3; } .note { fill: #8b949e; }",
        "    }",
        "  </style>",
        '  <rect class="background" width="940" height="710"/>',
        '  <text class="chart-title" x="470" y="30" text-anchor="middle">Cold-retrieval throughput by prompt length</text>',
        '  <line class="default-line" x1="92" y1="55" x2="120" y2="55"/>',
        '  <circle class="default-mark" cx="106" cy="55" r="4"/>',
        f'  <text class="legend" x="130" y="59">{esc(default["name"])}</text>',
        '  <rect class="reference-mark" x="564" y="51" width="8" height="8"/>',
        f'  <text class="legend" x="581" y="59">{esc(reference["name"])}</text>',
    ]

    for title, key, top, height, maximum in panels:
        bottom = top + height
        lines.extend(
            [
                f'  <text class="panel-title" x="92" y="{top - 55:g}">{title} (tok/s)</text>',
                f'  <rect class="frame" x="{x0:g}" y="{top:g}" width="{main_x1 - x0:g}" height="{height:g}"/>',
                f'  <rect class="frame" x="{outlier_x0:g}" y="{top:g}" width="{outlier_x1 - outlier_x0:g}" height="{height:g}"/>',
            ]
        )
        if key == "prefill_tokens_per_second":
            lines.append(
                f'  <text class="note" x="{outlier_x:g}" y="{top - 10:g}" text-anchor="middle">512K allocation</text>'
            )
        for fraction in (0.0, 0.5, 1.0):
            value = maximum * (1.0 - fraction)
            yy = top + height * fraction
            lines.append(f'  <line class="grid" x1="{x0:g}" y1="{yy:.2f}" x2="{main_x1:g}" y2="{yy:.2f}"/>')
            lines.append(f'  <line class="grid" x1="{outlier_x0:g}" y1="{yy:.2f}" x2="{outlier_x1:g}" y2="{yy:.2f}"/>')
            lines.append(f'  <text class="tick" x="80" y="{yy + 4:.2f}" text-anchor="end">{value:g}</text>')

        def y(value: float) -> float:
            return bottom - value / maximum * height

        for kind, _name, points in series:
            coords = [(x(p["actual_input_tokens"]), y(p[key])) for p in points]
            if kind == "default":
                main_coords = [
                    coord
                    for coord, point in zip(coords, points)
                    if point["actual_input_tokens"] <= main_max
                ]
                path = " ".join(
                    ("M" if index == 0 else "L") + f"{xx:.2f} {yy:.2f}"
                    for index, (xx, yy) in enumerate(main_coords)
                )
                lines.append(f'  <path class="default-line" d="{path}"/>')
            for index, ((xx, yy), point) in enumerate(zip(coords, points)):
                value = point[key]
                if kind == "default":
                    lines.append(f'  <circle class="default-mark" cx="{xx:.2f}" cy="{yy:.2f}" r="4.5"/>')
                    if index < 5:
                        dx, dy, anchor = (
                            (0, -12, "start"),
                            (0, 24, "start"),
                            (16, -28, "start"),
                            (0, 42, "start"),
                            (6, -10, "start"),
                        )[index]
                        lines.append(
                            f'  <text class="value" x="{xx + dx:.2f}" y="{yy + dy:.2f}" text-anchor="{anchor}">{value:.2f}</text>'
                        )
                    else:
                        anchor = "start" if index < len(points) - 1 else "end"
                        dx = 7 if anchor == "start" else -7
                        label_y = yy - 8 if index % 2 == 0 else yy + 18
                        lines.append(
                            f'  <text class="value" x="{xx + dx:.2f}" y="{label_y:.2f}" text-anchor="{anchor}">{value:.2f}</text>'
                        )
                else:
                    lines.append(f'  <rect class="reference-mark" x="{xx - 5:.2f}" y="{yy - 5:.2f}" width="10" height="10"/>')
                    lines.append(
                        f'  <text class="value" x="{xx + 9:.2f}" y="{yy + 4:.2f}" text-anchor="start">{value:.2f}</text>'
                    )

    axis_y = 610.0
    lines.append(f'  <line class="axis" x1="{x0:g}" y1="{axis_y:g}" x2="{main_x1:g}" y2="{axis_y:g}"/>')
    lines.append(f'  <line class="axis" x1="{outlier_x0:g}" y1="{axis_y:g}" x2="{outlier_x1:g}" y2="{axis_y:g}"/>')
    ticks = [7680, 15359, 30720, 59933, 122879, 163840, 245760]
    labels = ["8K", "15K", "31K", "60K", "123K", "164K", "246K"]
    anchors = ["end", "start", "middle", "middle", "middle", "middle", "middle"]
    for value, label, anchor in zip(ticks, labels, anchors):
        xx = x(value)
        lines.append(f'  <line class="axis" x1="{xx:.2f}" y1="610" x2="{xx:.2f}" y2="617"/>')
        lines.append(f'  <text class="tick" x="{xx:.2f}" y="631" text-anchor="{anchor}">{label}</text>')
    lines.append(f'  <line class="axis" x1="{outlier_x:g}" y1="610" x2="{outlier_x:g}" y2="617"/>')
    lines.append(f'  <text class="tick" x="{outlier_x:g}" y="631" text-anchor="middle">492K</text>')
    lines.extend(
        [
            '  <text class="axis-title" x="471" y="660" text-anchor="middle">Prompt length (tokens)</text>',
            '  <text class="note" x="471" y="689" text-anchor="middle">Cold five-key retrieval. Main segment is linear through 256K; the 491.5K point is isolated after the axis break.</text>',
            "</svg>",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(json.loads(DATA.read_text(encoding="utf-8")))
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("benchmark chart is stale; run scripts/render_benchmark.py")
        return
    OUTPUT.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
