import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import re

def sanitize_filename(name):
    sanitized = re.sub(r'[^a-zA-Z0-9]', '-', name)
    sanitized = re.sub(r'-+', '-', sanitized).strip('-')
    return sanitized

def generate_priority_plots(csv_file='results/task_metrics_log.csv', output_dir='visualization/figures_smartcities'):
    # Load CSV
    data = pd.read_csv(csv_file)
    data['Executed on'] = data['Executed on'].str.upper()

    # Define constants
    layers = ['EDGE', 'REGIONAL', 'CLOUD']
    priorities = [1, 2, 3]
    metrics = [
        ('CPU (%)', 'CPU Utilization (%)'),
        ('Storage (%)', 'Storage Utilization (%)'),
        ('Memory (%)', 'Memory Utilization (%)'),
        ('Avg_Prop(ms)', 'Prop Delay (ms)'),
        ('Tx_Cost', 'Transmission Cost'),
        ('Proc_Cost', 'Processing Cost'),
        ('Energy', 'Energy Consumption'),
        ('Conges(%)', 'Congestion (%)')
    ]

    # Output directory
    os.makedirs(output_dir, exist_ok=True)

    for metric, ylabel in metrics:
        for priority in priorities:
            subset = data[data['Flag'] == priority]
            workloads = sorted(subset['Workload'].unique())
            n = len(workloads)

            result = np.full((n, len(layers)), np.nan)
            for i, wl in enumerate(workloads):
                for j, layer in enumerate(layers):
                    val = subset[(subset['Workload'] == wl) & (subset['Executed on'] == layer)][metric]
                    if not val.empty:
                        result[i, j] = val.values[0]

            # Create figure
            fig, ax = plt.subplots(figsize=(4, 4))
            bar_width = 0.25
            x = np.arange(n)
            for i in range(len(layers)):
                ax.bar(x + i * bar_width, result[:, i], width=bar_width, label=layers[i])

            # Styling
            ax.set_ylabel(ylabel)
            ax.set_title(f'(Priority {priority})', fontweight='normal')
            ax.grid(True, axis='y')
            ax.spines[['top', 'right']].set_visible(False)
            ax.tick_params(labelsize=8)

            # X-labels
            labels = [''] * n
            if n >= 3:
                mid = n // 2
                labels[0] = str(workloads[0])
                labels[mid] = str(workloads[mid])
                labels[-1] = str(workloads[-1])
            elif n == 2:
                labels[0], labels[1] = str(workloads[0]), str(workloads[1])
            elif n == 1:
                labels[0] = str(workloads[0])

            ax.set_xticks(x + bar_width)
            ax.set_xticklabels(labels)
            ax.set_xlabel("Workload (KB)")
            ax.legend(fontsize=7, loc='upper right')

            # Save figure
            filename = f"{sanitize_filename(metric)}-P{priority}.png"
            filepath = os.path.join(output_dir, filename)
            plt.tight_layout()
            plt.savefig(filepath, dpi=300)
            plt.close()

def main():
    print("Generating Smart City priority plots...")
    generate_priority_plots()
    print("All figures saved to 'figures_square' directory.")

if __name__ == '__main__':
    main()
