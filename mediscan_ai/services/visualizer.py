"""
MediScan AI - Visualizer
Demonstrates: Matplotlib, NumPy arrays, graphs, file I/O
Generates charts from medical test data.
"""
import os
import uuid
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Color palette for medical charts
COLORS = {
    'primary': '#4F8EF7',
    'normal': '#34D399',
    'review': '#F87171',
    'unknown': '#94A3B8',
    'accent': '#A78BFA',
    'background': '#0F172A',
    'card': '#1E293B',
    'text': '#F1F5F9',
    'grid': '#334155',
}

# Matplotlib style configuration
CHART_STYLE = {
    'figure.facecolor': '#1E293B',
    'axes.facecolor': '#0F172A',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#CBD5E1',
    'xtick.color': '#94A3B8',
    'ytick.color': '#94A3B8',
    'text.color': '#F1F5F9',
    'grid.color': '#334155',
    'grid.alpha': 0.5,
}


def _setup_style() -> None:
    """Apply custom dark theme to matplotlib"""
    plt.rcParams.update(CHART_STYLE)
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.size'] = 10


def save_chart(fig: plt.Figure, charts_folder: str) -> str:
    """
    Save a matplotlib figure to disk.
    Demonstrates: file I/O, os module, string operations

    Args:
        fig: Matplotlib figure
        charts_folder: Directory to save charts

    Returns:
        Filename of saved chart (relative to static/)
    """
    os.makedirs(charts_folder, exist_ok=True)
    filename = f"chart_{uuid.uuid4().hex[:12]}.png"
    full_path = os.path.join(charts_folder, filename)
    fig.savefig(full_path, bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"Chart saved: {full_path}")
    return f"generated_charts/{filename}"


def generate_test_bar_chart(
    labels: List[str],
    values: List[float],
    statuses: Optional[List[str]] = None,
    title: str = "Medical Test Results",
    charts_folder: str = "static/generated_charts",
) -> Optional[str]:
    """
    Generate a bar chart of medical test values.
    Demonstrates: Matplotlib, NumPy arrays, loops, lists, branching

    Args:
        labels: Test names
        values: Numeric test values
        statuses: Status of each test ('normal', 'review', 'unknown')
        title: Chart title
        charts_folder: Where to save chart

    Returns:
        Relative path to saved chart, or None on failure
    """
    if not labels or not values or len(labels) != len(values):
        logger.warning("Invalid data for bar chart")
        return None

    if len(values) < 1:
        return None

    try:
        _setup_style()

        # Use NumPy for index calculation
        x = np.arange(len(labels))
        n = len(labels)

        # Determine bar colors from status
        bar_colors = []
        for i in range(n):
            status = (statuses[i] if statuses and i < len(statuses) else 'unknown')
            bar_colors.append(COLORS.get(status, COLORS['unknown']))

        # Figure sizing - wider for many tests
        fig_width = max(10, n * 1.2)
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        fig.patch.set_facecolor(COLORS['card'])
        ax.set_facecolor(COLORS['background'])

        # Draw bars
        bars = ax.bar(x, values, color=bar_colors, edgecolor='#334155',
                      linewidth=0.8, width=0.65, zorder=2)

        # Add value labels on top of bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height + max(height * 0.02, 0.01),
                f'{val:.2g}',
                ha='center', va='bottom',
                color='#F1F5F9', fontsize=8, fontweight='bold'
            )


        # Labels and formatting
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=40, ha='right', fontsize=8)

        # Use a logarithmic scale when test values span a very large range.
        # The actual test values remain unchanged.
        positive_values = [v for v in values if v > 0]

        if positive_values:
            min_value = min(positive_values)
            max_value = max(positive_values)

            if max_value / min_value >= 100:
                ax.set_yscale('log')
                ax.set_ylabel("Value (log scale)", color='#CBD5E1')
            else:
                ax.set_ylabel("Value", color='#CBD5E1')
        else:
            ax.set_ylabel("Value", color='#CBD5E1')

        ax.set_title(title, color='#F1F5F9', fontsize=13, fontweight='bold', pad=15)
        ax.grid(axis='y', color=COLORS['grid'], alpha=0.5, which='both', zorder=1)
        ax.set_axisbelow(True)

        # Legend
        legend_items = [
            mpatches.Patch(color=COLORS['normal'], label='Within Range'),
            mpatches.Patch(color=COLORS['review'], label='Needs Review'),
            mpatches.Patch(color=COLORS['unknown'], label='Range Unknown'),
        ]
        ax.legend(handles=legend_items, loc='upper right',
                  facecolor=COLORS['card'], labelcolor='#CBD5E1',
                  edgecolor='#334155', fontsize=8)

        plt.tight_layout()
        return save_chart(fig, charts_folder)

    except Exception as e:
        logger.error(f"Bar chart generation error: {e}", exc_info=True)
        return None


def generate_comparison_chart(
    comparison_data: Dict,
    charts_folder: str = "static/generated_charts",
) -> Optional[str]:
    """
    Generate a grouped bar chart comparing two reports.
    Demonstrates: Matplotlib grouped bars, NumPy, loops

    Args:
        comparison_data: Output from data_analyzer.compare_reports()
        charts_folder: Where to save chart

    Returns:
        Path to saved chart or None
    """
    chart_data = comparison_data.get('chart_data')
    if not chart_data:
        return None

    labels = chart_data.get('labels', [])
    values_a = chart_data.get('values_a', [])
    values_b = chart_data.get('values_b', [])
    label_a = chart_data.get('label_a', 'Report A')
    label_b = chart_data.get('label_b', 'Report B')

    if not labels or not values_a or not values_b:
        return None

    try:
        _setup_style()

        x = np.arange(len(labels))
        width = 0.35  # Width of each bar group

        fig_width = max(10, len(labels) * 1.5)
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        fig.patch.set_facecolor(COLORS['card'])
        ax.set_facecolor(COLORS['background'])

        # Two groups of bars
        bars_a = ax.bar(x - width / 2, values_a, width,
                        label=label_a, color=COLORS['primary'],
                        edgecolor='#1E3A6E', alpha=0.9, zorder=2)
        bars_b = ax.bar(x + width / 2, values_b, width,
                        label=label_b, color=COLORS['accent'],
                        edgecolor='#4C1D95', alpha=0.9, zorder=2)

        # Value labels
        for bar in bars_a:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., h + h * 0.01,
                    f'{h:.2g}', ha='center', va='bottom', fontsize=7,
                    color='#F1F5F9')

        for bar in bars_b:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., h + h * 0.01,
                    f'{h:.2g}', ha='center', va='bottom', fontsize=7,
                    color='#F1F5F9')

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=40, ha='right', fontsize=8)
        ax.set_ylabel("Value", color='#CBD5E1')
        ax.set_title("Report Comparison", color='#F1F5F9',
                     fontsize=13, fontweight='bold', pad=15)
        ax.legend(facecolor=COLORS['card'], labelcolor='#CBD5E1',
                  edgecolor='#334155', fontsize=9)
        ax.grid(axis='y', color=COLORS['grid'], alpha=0.5, zorder=1)
        ax.set_axisbelow(True)

        plt.tight_layout()
        return save_chart(fig, charts_folder)

    except Exception as e:
        logger.error(f"Comparison chart error: {e}", exc_info=True)
        return None


def generate_status_donut_chart(
    status_counts: Dict,
    charts_folder: str = "static/generated_charts",
) -> Optional[str]:
    """
    Generate a donut chart showing test status distribution.
    Demonstrates: Matplotlib pie/donut, branching

    Args:
        status_counts: {'normal': N, 'review': N, 'unknown': N}
        charts_folder: Where to save chart

    Returns:
        Path to saved chart or None
    """
    normal = status_counts.get('normal', 0)
    review = status_counts.get('review', 0)
    unknown = status_counts.get('unknown', 0)

    total = normal + review + unknown
    if total == 0:
        return None

    try:
        _setup_style()

        sizes = []
        labels_list = []
        colors_list = []
        explode = []

        data = [
            (normal, 'Within Range', COLORS['normal']),
            (review, 'Needs Review', COLORS['review']),
            (unknown, 'Range Unknown', COLORS['unknown']),
        ]

        for count, lbl, col in data:
            if count > 0:
                sizes.append(count)
                labels_list.append(f"{lbl}\n({count})")
                colors_list.append(col)
                explode.append(0.04 if lbl == 'Needs Review' else 0)

        if not sizes:
            return None

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor(COLORS['card'])
        ax.set_facecolor(COLORS['card'])

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels_list,
            colors=colors_list,
            explode=explode[:len(sizes)],
            autopct='%1.0f%%',
            startangle=90,
            wedgeprops=dict(width=0.6, edgecolor=COLORS['card'], linewidth=2),
        )

        for text in texts:
            text.set_color('#CBD5E1')
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color('#F1F5F9')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        ax.set_title("Test Results Overview", color='#F1F5F9',
                     fontsize=12, fontweight='bold', pad=20)

        plt.tight_layout()
        return save_chart(fig, charts_folder)

    except Exception as e:
        logger.error(f"Donut chart error: {e}", exc_info=True)
        return None
