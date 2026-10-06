"""
MediScan AI - Data Analyzer
Demonstrates: NumPy arrays, Pandas DataFrames, data alignment, aggregation,
              statistical analysis, summarization
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MedicalDataAnalyzer:
    """
    Analyzes medical test results using Pandas and NumPy.
    Demonstrates: OOP, encapsulation, Pandas, NumPy
    """

    def __init__(self, test_results: List[Dict]):
        """
        Initialize analyzer with test results.

        Args:
            test_results: List of test result dictionaries
        """
        self.raw_results = test_results
        self.df = self._build_dataframe(test_results)

    def _build_dataframe(self, results: List[Dict]) -> pd.DataFrame:
        """
        Convert test results to Pandas DataFrame.
        Demonstrates: Pandas DataFrame creation, data cleaning
        """
        if not results:
            return pd.DataFrame(columns=['test_name', 'value', 'unit',
                                         'reference_range', 'numeric_value', 'status'])

        # Create DataFrame from list of dictionaries
        df = pd.DataFrame(results)

        # Ensure required columns exist
        required_cols = ['test_name', 'value', 'unit', 'reference_range', 'numeric_value']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''

        # Clean data - demonstrates Pandas data alignment
        df['test_name'] = df['test_name'].astype(str).str.strip().str.title()
        df['unit'] = df['unit'].fillna('').astype(str).str.strip()
        df['value'] = df['value'].fillna('').astype(str).str.strip()
        df['reference_range'] = df['reference_range'].fillna('').astype(str)
        df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')

        # Add status column
        df['status'] = df.apply(self._compute_status, axis=1)

        return df

    def _compute_status(self, row: pd.Series) -> str:
        """
        Compute value status based on reference range.
        Demonstrates: Pandas apply, branching, regex
        """
        import re

        ref = str(row.get('reference_range', ''))
        numeric = row.get('numeric_value')

        if not ref or ref in ('', 'nan', 'None', 'Not provided in document'):
            return 'unknown'
        if numeric is None or (isinstance(numeric, float) and np.isnan(numeric)):
            return 'unknown'

        # Parse range "low - high"
        range_match = re.search(r'([\d.]+)\s*[-–]\s*([\d.]+)', ref)
        if range_match:
            try:
                low = float(range_match.group(1))
                high = float(range_match.group(2))
                if low <= numeric <= high:
                    return 'normal'
                return 'review'
            except ValueError:
                pass

        # Parse "< value"
        lt_match = re.search(r'<\s*([\d.]+)', ref)
        if lt_match:
            try:
                limit = float(lt_match.group(1))
                return 'normal' if numeric < limit else 'review'
            except ValueError:
                pass

        # Parse "> value"
        gt_match = re.search(r'>\s*([\d.]+)', ref)
        if gt_match:
            try:
                limit = float(gt_match.group(1))
                return 'normal' if numeric > limit else 'review'
            except ValueError:
                pass

        return 'unknown'

    def get_numeric_summary(self) -> Dict:
        """
        Get NumPy-based statistical summary of numeric test values.
        Demonstrates: NumPy arrays, numerical calculations
        """
        if self.df.empty:
            return {}

        numeric_col = self.df['numeric_value'].dropna()

        if numeric_col.empty:
            return {}

        # NumPy array operations - demonstrates numpy
        values_array = np.array(numeric_col.tolist())

        summary = {
            'count': int(len(values_array)),
            'mean': float(np.mean(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'median': float(np.median(values_array)),
        }

        return summary

    def get_status_breakdown(self) -> Dict:
        """
        Count tests by status.
        Demonstrates: Pandas groupby, aggregation
        """
        if self.df.empty:
            return {'normal': 0, 'review': 0, 'unknown': 0}

        # Pandas value_counts - demonstrates aggregation
        counts = self.df['status'].value_counts().to_dict()

        return {
            'normal': counts.get('normal', 0),
            'review': counts.get('review', 0),
            'unknown': counts.get('unknown', 0),
        }

    def get_tests_for_chart(self, max_tests: int = 15) -> Tuple[List[str], List[float]]:
        """
        Get test names and values suitable for chart generation.
        Demonstrates: Pandas filtering, sorting, list operations
        """
        if self.df.empty:
            return [], []

        # Filter to rows with numeric values
        chart_df = self.df[self.df['numeric_value'].notna()].copy()

        if chart_df.empty:
            return [], []

        # Limit number of tests shown
        chart_df = chart_df.head(max_tests)

        # Create display labels with units
        labels = []
        for _, row in chart_df.iterrows():
            name = row['test_name']
            unit = row['unit']
            label = f"{name}\n({unit})" if unit else name
            labels.append(label)

        values = chart_df['numeric_value'].tolist()

        return labels, values

    def filter_by_status(self, status: str) -> pd.DataFrame:
        """
        Filter tests by status.
        Demonstrates: Pandas filtering/boolean indexing
        """
        if self.df.empty:
            return pd.DataFrame()
        return self.df[self.df['status'] == status]

    def to_records(self) -> List[Dict]:
        """
        Convert DataFrame back to list of dicts.
        Demonstrates: Pandas to_dict, list operations
        """
        if self.df.empty:
            return []
        return self.df.to_dict('records')


def compare_reports(report_a_results: List[Dict],
                    report_b_results: List[Dict],
                    report_a_label: str = 'Report A',
                    report_b_label: str = 'Report B') -> Dict:
    """
    Compare test results from two reports.
    Demonstrates: Pandas merge/join, data alignment, NumPy calculations

    Args:
        report_a_results: Test results from first report
        report_b_results: Test results from second report
        report_a_label: Label for first report
        report_b_label: Label for second report

    Returns:
        Dictionary with comparison data
    """
    if not report_a_results or not report_b_results:
        return {'comparison': [], 'chart_data': None, 'summary': {}}

    # Build DataFrames
    df_a = pd.DataFrame(report_a_results)[['test_name', 'numeric_value', 'unit']].copy()
    df_b = pd.DataFrame(report_b_results)[['test_name', 'numeric_value', 'unit']].copy()

    # Normalize test names for merging
    df_a['test_name_lower'] = df_a['test_name'].str.lower().str.strip()
    df_b['test_name_lower'] = df_b['test_name'].str.lower().str.strip()

    # Rename value columns
    df_a = df_a.rename(columns={'numeric_value': 'value_a'})
    df_b = df_b.rename(columns={'numeric_value': 'value_b'})

    # Inner join on test name - demonstrates Pandas merge
    merged = pd.merge(df_a, df_b, on='test_name_lower', suffixes=('_a', '_b'))

    if merged.empty:
        return {'comparison': [], 'chart_data': None,
                'summary': {'matched_tests': 0}}

    # Calculate change using NumPy
    merged['change'] = merged['value_b'] - merged['value_a']
    merged['change_pct'] = np.where(
        merged['value_a'] != 0,
        ((merged['value_b'] - merged['value_a']) / merged['value_a']) * 100,
        np.nan
    )

    # Build comparison list
    comparison = []
    for _, row in merged.iterrows():
        val_a = row['value_a']
        val_b = row['value_b']
        change = row['change']
        change_pct = row['change_pct']

        if pd.isna(val_a) or pd.isna(val_b):
            continue

        entry = {
            'test_name': row['test_name_x'],
            'unit': row.get('unit_a', ''),
            'value_a': round(val_a, 3),
            'value_b': round(val_b, 3),
            'change': round(change, 3) if not pd.isna(change) else None,
            'change_pct': round(change_pct, 1) if not pd.isna(change_pct) else None,
            'direction': 'up' if change > 0 else ('down' if change < 0 else 'same'),
        }
        comparison.append(entry)

    # Build chart data for comparison
    if comparison:
        test_names = [c['test_name'] for c in comparison]
        values_a = [c['value_a'] for c in comparison]
        values_b = [c['value_b'] for c in comparison]
        chart_data = {
            'labels': test_names,
            'values_a': values_a,
            'values_b': values_b,
            'label_a': report_a_label,
            'label_b': report_b_label,
        }
    else:
        chart_data = None

    summary = {
        'matched_tests': len(comparison),
        'increased': sum(1 for c in comparison if c['direction'] == 'up'),
        'decreased': sum(1 for c in comparison if c['direction'] == 'down'),
        'unchanged': sum(1 for c in comparison if c['direction'] == 'same'),
        'label_a': report_a_label,
        'label_b': report_b_label,
    }

    return {
        'comparison': comparison,
        'chart_data': chart_data,
        'summary': summary,
    }
