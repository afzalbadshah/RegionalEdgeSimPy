import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def generate_plots(csv_path, output_dir='visualization'):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)

    sns.set_context("paper", font_scale=1.5)
    sns.set_style("white")

    layer_order = ['Edge', 'Regional', 'Cloud']

    # Mapping: column -> (y-axis label, output filename)
    plot_info = {
        "CPU (%)": ("CPU Utilization (%)", "cpu_bar.png"),
        "Storage (%)": ("Storage Utilization (%)", "storage_bar.png"),
        "Avg_Tx(ms)": ("Average Transmission Delay (ms)", "transmission_delay_bar.png"),
        "Avg_Prop(ms)": ("Average Propagation Delay (ms)", "propagation_delay_bar.png"),
        "Tx_Cost": ("Transmission Cost", "transmission_cost_bar.png"),
        "Proc_Cost": ("Processing Cost", "processing_cost_bar.png"),
        "Energy": ("Energy Consumption", "energy_bar.png"),
        "Conges(%)": ("Congestion (%)", "congestion_bar.png")
    }

    def plot_bar(data, y_col, y_label, filename):
        grouped = data.groupby(['Workload', 'Executed on'])[y_col].mean().reset_index()
        plt.figure(figsize=(14, 6))
        ax = sns.barplot(data=grouped, x="Workload", y=y_col, hue="Executed on",
                         hue_order=layer_order, dodge=True)
        ax.set_xlabel("Vehicular Workload (KB)")
        ax.set_ylabel(y_label)
        ax.legend(title=None, loc='upper left')
        plt.xticks(rotation=45)
        sns.despine()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename), dpi=300)
        plt.close()

    # Generate all bar charts
    for col, (y_label, filename) in plot_info.items():
        plot_bar(df, col, y_label, filename)

    print(f"✅ All bar charts saved to '{output_dir}'.")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Generate bar charts for vehicular workload metrics.")
        parser.add_argument("--csv", required=False, default="results/task_metrics_log.csv",
                            help="Path to CSV file (default: results/task_metrics_log.csv)")
        parser.add_argument("--out", default="visualization", help="Folder to save plots (default: visualization)")
        args = parser.parse_args()
        generate_plots(args.csv, args.out)
    except SystemExit as e:
        if e.code == 2:
            print("❌ Error: Please provide the required --csv argument.\nExample:\n  python plotter.py --csv results/task_metrics_log.csv")
        raise
