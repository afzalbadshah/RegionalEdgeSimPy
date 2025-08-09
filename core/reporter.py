"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- This module prints metrics to the console and writes them to a CSV file.
- Students can add/remove/change metrics by modifying TASK_FIELDS below.
"""

import csv


class Reporter:
    """
    Simple CSV + console table reporter.
    Each row of output comes from a dict mapping field keys → values.
    """

    def __init__(self, fields, csv_file):
        """
        fields   : list of (key, label, format_string)
                   key   = dictionary key in data dict
                   label = column name for console/CSV
                   fmt   = how to format the value (e.g., '{:.2f}')
        csv_file : output file path
        """
        self.fields = fields
        self.csv_file = csv_file
        self.widths = None
        self._init_csv()

    def _init_csv(self):
        """
        Initialize CSV file with header row.
        """
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            header = [label for _, label, _ in self.fields]
            writer.writerow(header)

    def report(self, data):
        """
        Write one row to console and CSV from `data` dict.
        """
        # Apply formatting for console display
        formatted = []
        for key, label, fmt in self.fields:
            val = data.get(key, "")
            try:
                formatted.append(fmt.format(val))
            except (ValueError, TypeError):
                formatted.append(str(val))

        # If first call, print header and separator
        if self.widths is None:
            labels = [label for _, label, _ in self.fields]
            self.widths = [max(len(label), len(val)) for label, val in zip(labels, formatted)]
            header_line = " | ".join(label.ljust(w) for label, w in zip(labels, self.widths))
            separator = "-+-".join("-" * w for w in self.widths)
            print(header_line)
            print(separator)

        # Print row to console
        line = " | ".join(val.ljust(w) for val, w in zip(formatted, self.widths))
        print(line)

        # Append raw values (unformatted) to CSV
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            row = [data.get(key, "") for key, _, _ in self.fields]
            writer.writerow(row)


# ---------------------------------------------------------------------
# Default task reporting configuration
# ---------------------------------------------------------------------
# Students: To change what metrics are recorded:
# 1) Add a new tuple to TASK_FIELDS: ('your_key', 'Column Name', '{:.2f}')
#    - your_key: must match the key in the metrics dict passed to report().
#    - 'Column Name': what will appear in console/CSV header.
#    - '{:.2f}': Python format string for display precision.
# 2) Remove or comment out any tuple to hide that metric.
# 3) Ensure your scheduler or simulator includes those keys in its metrics dict.
# ---------------------------------------------------------------------

TASK_FIELDS = [
    ("round_no",    "Round",        "{}"),
    ("devices",     "Devices",      "{}"),
    ("workload",    "Workload",     "{:.2f}"),
    # Mobility‐specific metrics
    ("avg_pos",     "Avg_Pos",      "{:.2f}"),
    ("avg_signal",  "Signal(dB)",   "{:.2f}"),
    # Resource usage
    ("cpu_util",    "CPU (%)",      "{:.2f}"),
    ("memory_util", "Memory (%)",   "{:.2f}"),
    ("storage_util","Storage (%)",  "{:.2f}"),
    # Execution context
    ("layer",       "Paradigm",     "{}"),
    ("avg_tx",      "Avg_Tx(ms)",   "{:.2f}"),
    ("avg_prop",    "Avg_Prop(ms)", "{:.2f}"),
    ("tx_cost",     "Tx_Cost",      "{:.2f}"),
    ("proc_cost",   "Proc_Cost",    "{:.2f}"),
    ("energy",      "Energy",       "{:.4f}"),
    ("congestion",  "Conges(%)",    "{:.2f}"),
    ("flag",        "Flag",         "{}"),
    ("failed",      "Failed",       "{}"),
]

# Reporter instance used by the simulator
task_reporter = Reporter(TASK_FIELDS, "results/task_metrics_log.csv")
