#!/usr/bin/env python3
"""
Dashboard Generator for Insight Collector

Generates standalone HTML report with:
- Tool usage heatmap
- Instinct confidence trends
- Pattern detection summary
- Evolution history timeline
- Session statistics
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Template for the HTML dashboard
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insight Collector Dashboard</title>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --accent: #e94560;
            --text: #eaeaea;
            --success: #4ecca3;
        }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .dashboard {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ color: var(--accent); margin-bottom: 10px; }}
        .header p {{ color: #888; }}
        .card {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .card h2 {{
            color: var(--accent);
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: var(--success);
            margin: 10px 0;
        }}
        .stat-label {{ color: #888; font-size: 0.9em; }}
        .heatmap {{
            display: grid;
            grid-template-columns: repeat(24, 1fr);
            gap: 4px;
            margin-top: 10px;
        }}
        .heatmap-cell {{
            aspect-ratio: 1;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
        }}
        .heatmap-label {{
            display: grid;
            grid-template-columns: repeat(24, 1fr);
            gap: 4px;
            margin-top: 5px;
            font-size: 10px;
            color: #666;
        }}
        .heatmap-label span {{ text-align: center; }}
        .tool-bar {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        .tool-name {{
            width: 120px;
            font-weight: bold;
            color: var(--text);
        }}
        .bar-container {{
            flex: 1;
            background: #0a0a1a;
            border-radius: 4px;
            height: 24px;
            position: relative;
            margin: 0 10px;
        }}
        .bar {{
            background: linear-gradient(90deg, var(--accent), var(--success));
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        .tool-count {{
            width: 60px;
            text-align: right;
            color: #888;
        }}
        .confidence-bar {{
            display: inline-flex;
            gap: 2px;
        }}
        .confidence-bar span {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}
        .filled {{ background: var(--success); }}
        .empty {{ background: #333; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            color: var(--accent);
            font-weight: bold;
            background: rgba(233, 69, 96, 0.1);
        }}
        tr:hover {{ background: rgba(255, 255, 255, 0.05); }}
        .timeline {{
            position: relative;
            padding-left: 30px;
            margin-top: 20px;
        }}
        .timeline-item {{
            position: relative;
            padding-bottom: 20px;
            border-left: 2px solid var(--accent);
            padding-left: 20px;
        }}
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -8px;
            top: 0;
            width: 14px;
            height: 14px;
            background: var(--accent);
            border-radius: 50%;
        }}
        .timeline-date {{
            color: #888;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .timeline-content {{
            color: var(--text);
        }}
        .tag {{
            display: inline-block;
            background: var(--accent);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 2px;
        }}
        .pattern-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .pattern-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--success);
        }}
        .pattern-domain {{
            color: var(--accent);
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .pattern-count {{
            font-size: 2em;
            font-weight: bold;
            color: var(--success);
        }}
        .empty-state {{
            text-align: center;
            color: #666;
            padding: 40px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🔍 Insight Collector Dashboard</h1>
            <p>Generated: {generated_at}</p>
        </div>

        <!-- Stats Overview -->
        <div class="grid">
            <div class="stat-card">
                <h3>📊 Observations</h3>
                <div class="stat-number">{total_observations}</div>
                <p class="stat-label">Total recorded</p>
            </div>
            <div class="stat-card">
                <h3>💡 Instincts</h3>
                <div class="stat-number">{total_instincts}</div>
                <p class="stat-label">Patterns learned</p>
            </div>
            <div class="stat-card">
                <h3>⚡ Evolutions</h3>
                <div class="stat-number">{total_evolutions}</div>
                <p class="stat-label">Components created</p>
            </div>
            <div class="stat-card">
                <h3>📈 Avg Confidence</h3>
                <div class="stat-number">{avg_confidence}</div>
                <p class="stat-label">Across instincts</p>
            </div>
        </div>

        <!-- Tool Usage Heatmap -->
        <div class="card">
            <h2>🔥 Tool Usage Heatmap (by hour)</h2>
            {heatmap_html}
        </div>

        <!-- Top Tools -->
        <div class="card">
            <h2>🛠️ Top Tools</h2>
            {top_tools_html}
        </div>

        <!-- Instincts Table -->
        <div class="card">
            <h2>📋 Instinct Registry</h2>
            {instincts_table_html}
        </div>

        <!-- Evolution Timeline -->
        <div class="card">
            <h2>🚀 Evolution Timeline</h2>
            {evolution_timeline_html}
        </div>

        <!-- Pattern Summary -->
        <div class="card">
            <h2>🧩 Pattern Summary</h2>
            {pattern_summary_html}
        </div>
    </div>
</body>
</html>'''


def get_caw_dir() -> Path:
    """Get .caw directory path."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    return Path(project_dir) / '.caw'


def load_observations() -> List[Dict]:
    """Load observations from JSONL file."""
    caw_dir = get_caw_dir()
    obs_file = caw_dir / 'observations' / 'observations.jsonl'

    if not obs_file.exists():
        return []

    observations = []
    try:
        with open(obs_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    observations.append(json.loads(line))
    except Exception as e:
        print(f"Warning: Could not load observations: {e}")

    return observations


def load_instincts_index() -> Dict:
    """Load instincts index."""
    caw_dir = get_caw_dir()
    index_file = caw_dir / 'instincts' / 'index.json'

    if not index_file.exists():
        return {'instincts': [], 'last_updated': None}

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load instincts index: {e}")
        return {'instincts': [], 'last_updated': None}


def load_evolutions() -> List[Dict]:
    """Load evolution history."""
    caw_dir = get_caw_dir()
    evolved_dir = caw_dir / 'evolved'

    evolutions = []
    if not evolved_dir.exists():
        return evolutions

    for subdir in ['commands', 'skills', 'agents']:
        evo_dir = evolved_dir / subdir
        if evo_dir.exists():
            for file in evo_dir.glob('*.md'):
                evolutions.append({
                    'type': subdir.rstrip('s'),
                    'name': file.stem,
                    'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })

    return sorted(evolutions, key=lambda x: x['created'], reverse=True)


def get_heatmap_color(count: int) -> str:
    """Get heatmap cell color based on usage count."""
    if count == 0:
        return '#1a1a2e'
    elif count <= 5:
        return '#16213e'
    elif count <= 15:
        return '#0f3460'
    elif count <= 30:
        return '#e94560'
    else:
        return '#4ecca3'


def generate_heatmap(observations: List[Dict]) -> str:
    """Generate tool usage heatmap HTML."""
    if not observations:
        return '<p class="empty-state">No observation data available</p>'

    # Count tool usage by hour (0-23)
    hour_counts = defaultdict(int)
    for obs in observations:
        try:
            dt = datetime.fromisoformat(obs['timestamp'].replace('Z', '+00:00'))
            hour = dt.hour
            hour_counts[hour] += 1
        except Exception:
            continue

    # Generate heatmap cells
    cells = []
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        color = get_heatmap_color(count)
        cells.append(
            f'<div class="heatmap-cell" style="background: {color};" '
            f'title="Hour {hour}: {count} uses">{count if count > 0 else ""}</div>'
        )

    # Generate hour labels
    labels = []
    for hour in range(24):
        label = f'{hour}h' if hour % 3 == 0 else ''
        labels.append(f'<span>{label}</span>')

    heatmap_html = f'''
    <div class="heatmap">
        {''.join(cells)}
    </div>
    <div class="heatmap-label">
        {''.join(labels)}
    </div>
    '''

    return heatmap_html


def generate_top_tools(observations: List[Dict]) -> str:
    """Generate top tools bar chart HTML."""
    if not observations:
        return '<p class="empty-state">No observation data available</p>'

    # Count tool usage
    tool_counts = Counter(obs['tool_name'] for obs in observations)
    top_tools = tool_counts.most_common(10)

    if not top_tools:
        return '<p class="empty-state">No tool usage data</p>'

    total_uses = sum(tool_counts.values())

    bars = []
    for tool, count in top_tools:
        percentage = (count / total_uses) * 100
        bars.append(f'''
        <div class="tool-bar">
            <div class="tool-name">{tool}</div>
            <div class="bar-container">
                <div class="bar" style="width: {percentage}%;"></div>
            </div>
            <div class="tool-count">{count} ({percentage:.1f}%)</div>
        </div>
        ''')

    return ''.join(bars)


def generate_confidence_bar(confidence: float) -> str:
    """Generate confidence bar HTML (10 dots)."""
    filled = int(confidence * 10)
    dots = []
    for i in range(10):
        css_class = 'filled' if i < filled else 'empty'
        dots.append(f'<span class="{css_class}"></span>')
    return f'<div class="confidence-bar">{"".join(dots)}</div>'


def generate_instincts_table(instincts: List[Dict]) -> str:
    """Generate instincts table HTML."""
    if not instincts:
        return '<p class="empty-state">No instincts generated yet</p>'

    rows = []
    for inst in sorted(instincts, key=lambda x: x.get('confidence', 0), reverse=True):
        inst_id = inst.get('id', 'unknown')
        trigger = inst.get('trigger', 'N/A')
        confidence = inst.get('confidence', 0.0)
        evidence = inst.get('evidence_count', 0)
        domain = inst.get('domain', 'general')

        confidence_bar = generate_confidence_bar(confidence)

        rows.append(f'''
        <tr>
            <td><code>{inst_id}</code></td>
            <td>{trigger}</td>
            <td>{confidence_bar}</td>
            <td style="text-align: center;">{confidence:.0%}</td>
            <td style="text-align: center;">{evidence}</td>
            <td><span class="tag">{domain}</span></td>
        </tr>
        ''')

    table_html = f'''
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Trigger</th>
                <th>Confidence</th>
                <th>%</th>
                <th>Evidence</th>
                <th>Domain</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    '''

    return table_html


def generate_evolution_timeline(evolutions: List[Dict]) -> str:
    """Generate evolution timeline HTML."""
    if not evolutions:
        return '<p class="empty-state">No evolutions yet</p>'

    items = []
    for evo in evolutions[:20]:  # Show latest 20
        evo_type = evo['type'].title()
        name = evo['name']
        try:
            dt = datetime.fromisoformat(evo['created'])
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            date_str = evo['created']

        items.append(f'''
        <div class="timeline-item">
            <div class="timeline-date">{date_str}</div>
            <div class="timeline-content">
                <strong>{evo_type}:</strong> {name}
            </div>
        </div>
        ''')

    return f'<div class="timeline">{"".join(items)}</div>'


def generate_pattern_summary(instincts: List[Dict]) -> str:
    """Generate pattern summary by domain."""
    if not instincts:
        return '<p class="empty-state">No patterns detected yet</p>'

    # Group by domain
    domain_counts = Counter(inst.get('domain', 'general') for inst in instincts)

    items = []
    for domain, count in domain_counts.most_common():
        items.append(f'''
        <div class="pattern-item">
            <div class="pattern-domain">{domain.title()}</div>
            <div class="pattern-count">{count}</div>
        </div>
        ''')

    return f'<div class="pattern-grid">{"".join(items)}</div>'


def generate_dashboard(output_path: Optional[str] = None) -> str:
    """Generate complete dashboard HTML."""
    caw_dir = get_caw_dir()

    # Ensure output directory exists
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = caw_dir / 'dashboard.html'

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    observations = load_observations()
    instincts_data = load_instincts_index()
    instincts = instincts_data.get('instincts', [])
    evolutions = load_evolutions()

    # Calculate stats
    total_observations = len(observations)
    total_instincts = len(instincts)
    total_evolutions = len(evolutions)
    avg_confidence = sum(inst.get('confidence', 0) for inst in instincts) / len(instincts) if instincts else 0

    # Generate sections
    heatmap_html = generate_heatmap(observations)
    top_tools_html = generate_top_tools(observations)
    instincts_table_html = generate_instincts_table(instincts)
    evolution_timeline_html = generate_evolution_timeline(evolutions)
    pattern_summary_html = generate_pattern_summary(instincts)

    # Fill template
    html_content = HTML_TEMPLATE.format(
        generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        total_observations=total_observations,
        total_instincts=total_instincts,
        total_evolutions=total_evolutions,
        avg_confidence=f'{avg_confidence:.0%}',
        heatmap_html=heatmap_html,
        top_tools_html=top_tools_html,
        instincts_table_html=instincts_table_html,
        evolution_timeline_html=evolution_timeline_html,
        pattern_summary_html=pattern_summary_html
    )

    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return str(output_file.absolute())


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Insight Collector Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 dashboard.py                    # Generate to .caw/dashboard.html
  python3 dashboard.py --open             # Generate and open in browser
  python3 dashboard.py -o report.html     # Custom output path
        '''
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: .caw/dashboard.html)'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open in browser after generation'
    )

    args = parser.parse_args()

    try:
        output_path = generate_dashboard(args.output)
        print(f"✅ Dashboard generated: {output_path}")

        if args.open:
            import webbrowser
            webbrowser.open(f'file://{output_path}')
            print(f"🌐 Opening in browser...")

    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
