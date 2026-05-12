#!/usr/bin/env python3
"""Plot cache metrics from all_circuits_cache_metrics.csv (no pandas)"""

import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (18, 14)

def load_csv(csv_path):
    """Load CSV without pandas"""
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for key in row:
                try:
                    if '.' in row[key]:
                        row[key] = float(row[key])
                    else:
                        row[key] = int(row[key])
                except (ValueError, TypeError):
                    pass
            data.append(row)
    return data

def plot_metrics(data, output_dir):
    """Create comprehensive metrics plots"""
    output_dir.mkdir(parents=True, exist_ok=True)
    n = len(data)
    circuits = [d['circuit'] for d in data]

    fig = plt.figure(figsize=(18, 14))

    # 1. Circuit complexity overview
    ax1 = plt.subplot(3, 3, 1)
    qubits = [d['num_logical_qubits'] for d in data]
    gates = [d['total_routable_gates']/10 for d in data]
    layers = [d['total_layers'] for d in data]
    x = np.arange(n)
    w = 0.25
    ax1.bar(x - w, qubits, w, label='Qubits', alpha=0.8)
    ax1.bar(x, gates, w, label='Gates (÷10)', alpha=0.8)
    ax1.bar(x + w, layers, w, label='Layers', alpha=0.8)
    ax1.set_xlabel('Circuit')
    ax1.set_ylabel('Count')
    ax1.set_title('Circuit Complexity Overview', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([c[:12] for c in circuits], rotation=45, ha='right', fontsize=8)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # 2. T/CNOT ratio scatter
    ax2 = plt.subplot(3, 3, 2)
    t_ratio = [d['t_count_ratio'] for d in data]
    cnot_ratio = [d['cnot_ratio'] for d in data]
    gates_color = [d['total_routable_gates'] for d in data]
    scatter = ax2.scatter(cnot_ratio, t_ratio, s=100, alpha=0.6, c=gates_color, cmap='viridis')
    ax2.set_xlabel('CNOT Ratio')
    ax2.set_ylabel('T-count Ratio')
    ax2.set_title('Gate Composition', fontweight='bold')
    plt.colorbar(scatter, ax=ax2, label='Total Gates')
    ax2.grid(alpha=0.3)

    # 3. Layer reuse
    ax3 = plt.subplot(3, 3, 3)
    reuse = [d['layer_reuse_ratio'] for d in data]
    colors = plt.cm.RdYlGn(np.array(reuse) / max(reuse) if max(reuse) > 0 else np.array(reuse))
    ax3.barh(range(n), reuse, color=colors)
    ax3.set_yticks(range(n))
    ax3.set_yticklabels([c[:12] for c in circuits], fontsize=8)
    ax3.set_xlabel('Layer Reuse Ratio')
    ax3.set_title('Layer Reuse Potential', fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)

    # 4. Layer size analysis
    ax4 = plt.subplot(3, 3, 4)
    avg_size = [d['avg_layer_size'] for d in data]
    max_size = [d['max_layer_size'] for d in data]
    congestion = [d['layer_congestion_score'] for d in data]
    gate_count = [d['total_routable_gates'] for d in data]
    scatter = ax4.scatter(avg_size, max_size, s=np.array(gate_count)*0.5, alpha=0.6, c=congestion, cmap='coolwarm')
    ax4.set_xlabel('Avg Layer Size')
    ax4.set_ylabel('Max Layer Size')
    ax4.set_title('Layer Size Distribution', fontweight='bold')
    plt.colorbar(scatter, ax=ax4, label='Congestion')
    ax4.grid(alpha=0.3)

    # 5. Congestion score
    ax5 = plt.subplot(3, 3, 5)
    sorted_idx = sorted(range(n), key=lambda i: congestion[i])
    sorted_circuits = [circuits[i][:12] for i in sorted_idx]
    sorted_congestion = [congestion[i] for i in sorted_idx]
    colors = plt.cm.Spectral(np.array(sorted_congestion) / max(sorted_congestion) if max(sorted_congestion) > 0 else np.array(sorted_congestion))
    ax5.barh(range(n), sorted_congestion, color=colors)
    ax5.set_yticks(range(n))
    ax5.set_yticklabels(sorted_circuits, fontsize=8)
    ax5.set_xlabel('Congestion Score')
    ax5.set_title('Layer Congestion (lower=balanced)', fontweight='bold')
    ax5.grid(axis='x', alpha=0.3)

    # 6. Path length
    ax6 = plt.subplot(3, 3, 6)
    avg_path = [d['avg_estimated_path_length'] for d in data]
    max_path = [d['max_estimated_path_length'] for d in data]
    num_cnot = [d['num_cnot'] for d in data]
    scatter = ax6.scatter(avg_path, max_path, s=np.array(qubits)*10, alpha=0.6, c=num_cnot, cmap='plasma')
    ax6.set_xlabel('Avg Path Length')
    ax6.set_ylabel('Max Path Length')
    ax6.set_title('Routing Path Metrics', fontweight='bold')
    plt.colorbar(scatter, ax=ax6, label='CNOT Gates')
    ax6.grid(alpha=0.3)

    # 7. CNOT pairs
    ax7 = plt.subplot(3, 3, 7)
    unique_pairs = [d['num_unique_cnot_pairs'] for d in data]
    avg_rep = [d['avg_cnot_pair_repetition'] for d in data]
    scatter = ax7.scatter(unique_pairs, avg_rep, s=np.array(num_cnot)*0.3, alpha=0.6, c=qubits, cmap='coolwarm')
    ax7.set_xlabel('Unique CNOT Pairs')
    ax7.set_ylabel('Avg Pair Repetition')
    ax7.set_title('CNOT Connectivity', fontweight='bold')
    plt.colorbar(scatter, ax=ax7, label='Qubits')
    ax7.grid(alpha=0.3)

    # 8. T-gate distribution
    ax8 = plt.subplot(3, 3, 8)
    num_t = [d['num_t_tdg'] for d in data]
    avg_t_per_layer = [d['avg_t_per_layer'] for d in data]
    ax8.bar(range(n), num_t, alpha=0.7, color='steelblue')
    ax8_twin = ax8.twinx()
    ax8_twin.plot(range(n), avg_t_per_layer, 'ro-', linewidth=2, markersize=6)
    ax8.set_xlabel('Circuit')
    ax8.set_ylabel('Total T gates', color='steelblue')
    ax8_twin.set_ylabel('Avg T per layer', color='red')
    ax8.set_title('T-gate Distribution', fontweight='bold')
    ax8.set_xticks(range(n))
    ax8.set_xticklabels([c[:10] for c in circuits], rotation=45, ha='right', fontsize=8)
    ax8.grid(axis='y', alpha=0.3)

    # 9. Repeated sequences
    ax9 = plt.subplot(3, 3, 9)
    rep_len = [d['max_repeated_seq_len'] for d in data]
    max_rep = max(rep_len) if rep_len else 1
    colors = plt.cm.YlOrRd(np.array(rep_len) / max_rep if max_rep > 0 else np.array(rep_len))
    ax9.barh(range(n), rep_len, color=colors)
    ax9.set_yticks(range(n))
    ax9.set_yticklabels([c[:12] for c in circuits], fontsize=8)
    ax9.set_xlabel('Max Repeated Seq Length')
    ax9.set_title('Layer Pattern Repetition', fontweight='bold')
    ax9.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    # Save
    output_path = output_dir / 'cache_metrics_plots.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Plots saved: {output_path}")

    # Summary stats
    print(f"\n📊 Analysis of {n} circuits:")
    print(f"  • Avg qubits: {np.mean(qubits):.1f}")
    print(f"  • Avg gates: {np.mean([d['total_routable_gates'] for d in data]):.0f}")
    print(f"  • Avg layers: {np.mean([d['total_layers'] for d in data]):.0f}")
    if congestion:
        max_cong_idx = congestion.index(max(congestion))
        print(f"  • Most congested: {circuits[max_cong_idx]} ({max(congestion):.3f})")
    if reuse:
        max_reuse_idx = reuse.index(max(reuse))
        print(f"  • Most reusable: {circuits[max_reuse_idx]} ({max(reuse):.3f})")
    if max_path:
        print(f"  • Max path length: {max(max_path):.0f}")

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    csv_path = project_root / 'benchmarks' / 'results' / 'cache_metrics' / 'all_circuits_cache_metrics.csv'

    if not csv_path.exists():
        print(f"Error: CSV not found at {csv_path}")
        sys.exit(1)

    data = load_csv(csv_path)
    print(f"✓ Loaded {len(data)} circuits")

    output_dir = project_root / 'visualization' / 'cache_metrics'
    plot_metrics(data, output_dir)
    print("✅ Done!")
