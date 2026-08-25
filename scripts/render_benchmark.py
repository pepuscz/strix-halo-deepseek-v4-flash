#!/usr/bin/env python3
"""Render the published throughput chart from benchmarks/results.json."""

from __future__ import annotations

import argparse
import html
import json
import math
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
    x0, x1 = 92.0, 850.0
    x_min = default["context_scaling"][0]["actual_input_tokens"]
    x_max = default["context_scaling"][-1]["actual_input_tokens"]

    def x(value: int) -> float:
        return x0 + (math.log(value) - math.log(x_min)) / (
            math.log(x_max) - math.log(x_min)
        ) * (x1 - x0)

    panels = [
        ("Input processing", "prefill_tokens_per_second", 110.0, 170.0, 280.0),
        ("Generation", "decode_tokens_per_second", 350.0, 170.0, 45.0),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 620" role="img" aria-labelledby="title description">',
        '  <title id="title">Cold-retrieval throughput from 2K to 492K prompts</title>',
        '  <desc id="description">Input-processing and generation throughput for the qualified Strix Halo llama.cpp Vulkan IQ3_XXS configuration using the same cold five-key retrieval workload at eleven measured prompt lengths from 2,040 through 491,520 tokens, with the available Lucebox ROCm ROCmFPX retrieval reference.</desc>',
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
        '  <rect class="background" width="940" height="620"/>',
        '  <text class="chart-title" x="470" y="30" text-anchor="middle">Cold-retrieval throughput from 2K to 492K prompts</text>',
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
                f'  <text class="panel-title" x="92" y="{top - 12:g}">{title} (tok/s)</text>',
                f'  <rect class="frame" x="{x0:g}" y="{top:g}" width="{x1 - x0:g}" height="{height:g}"/>',
            ]
        )
        for fraction in (0.0, 0.5, 1.0):
            value = maximum * (1.0 - fraction)
            yy = top + height * fraction
            lines.append(f'  <line class="grid" x1="{x0:g}" y1="{yy:.2f}" x2="{x1:g}" y2="{yy:.2f}"/>')
            lines.append(f'  <text class="tick" x="80" y="{yy + 4:.2f}" text-anchor="end">{value:g}</text>')

        def y(value: float) -> float:
            return bottom - value / maximum * height

        for kind, _name, points in series:
            coords = [(x(p["actual_input_tokens"]), y(p[key])) for p in points]
            if kind == "default":
                path = " ".join(
                    ("M" if index == 0 else "L") + f"{xx:.2f} {yy:.2f}"
                    for index, (xx, yy) in enumerate(coords)
                )
                lines.append(f'  <path class="default-line" d="{path}"/>')
            for index, ((xx, yy), point) in enumerate(zip(coords, points)):
                value = point[key]
                if kind == "default":
                    lines.append(f'  <circle class="default-mark" cx="{xx:.2f}" cy="{yy:.2f}" r="4.5"/>')
                    anchor = "start" if index < len(points) - 1 else "end"
                    dx = 7 if anchor == "start" else -7
                    label_y = yy - 8 if index % 2 == 0 else yy + 18
                    if label_y < top + 12:
                        label_y = yy + 18
                    lines.append(
                        f'  <text class="value" x="{xx + dx:.2f}" y="{label_y:.2f}" text-anchor="{anchor}">{value:.2f}</text>'
                    )
                else:
                    lines.append(f'  <rect class="reference-mark" x="{xx - 5:.2f}" y="{yy - 5:.2f}" width="10" height="10"/>')
                    lines.append(
                        f'  <text class="value" x="{xx + 9:.2f}" y="{yy + 4:.2f}" text-anchor="start">{value:.2f}</text>'
                    )

    axis_y = 530.0
    lines.append(f'  <line class="axis" x1="{x0:g}" y1="{axis_y:g}" x2="{x1:g}" y2="{axis_y:g}"/>')
    ticks = [point["actual_input_tokens"] for point in default["context_scaling"]]
    labels = [
        "2.04K", "3.84K", "7.68K", "15.4K", "30.7K", "59.9K",
        "122.9K", "163.8K", "213K", "245.8K", "491.5K",
    ]
    for index, (value, label) in enumerate(zip(ticks, labels)):
        xx = x(value)
        label_y = 551 if index % 2 == 0 else 568
        lines.append(f'  <line class="axis" x1="{xx:.2f}" y1="530" x2="{xx:.2f}" y2="537"/>')
        anchor = "start" if index == 0 else "end" if index == len(ticks) - 1 else "middle"
        lines.append(f'  <text class="tick" x="{xx:.2f}" y="{label_y}" text-anchor="{anchor}">{label}</text>')
    lines.extend(
        [
            '  <text class="axis-title" x="471" y="592" text-anchor="middle">Exact prompt length (tokens, logarithmic scale)</text>',
            '  <text class="note" x="471" y="611" text-anchor="middle">All points use cold five-key retrieval. Allocations: 128K through 122.9K; 256K through 245.8K; 512K at 491.5K.</text>',
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
