# app/metrics.py
from collections import defaultdict

# Store counters in memory
# Key: (name, labels_tuple) -> Value: count
_COUNTERS = defaultdict(int)

def inc_counter(name: str, labels: dict):
    # Sort labels to ensure consistent keys
    label_key = tuple(sorted(labels.items()))
    _COUNTERS[(name, label_key)] += 1

def generate_latest():
    """
    Returns metrics in Prometheus text format.
    """
    output = []
    
    # Group by metric name
    metrics_by_name = defaultdict(list)
    for (name, label_key), value in _COUNTERS.items():
        metrics_by_name[name].append((label_key, value))
        
    for name, entries in metrics_by_name.items():
        # TYPE header
        output.append(f"# TYPE {name} counter")
        for label_key, value in entries:
            # Format labels: key="value",key2="value2"
            label_str = ",".join(f'{k}="{v}"' for k, v in label_key)
            output.append(f'{name}{{{label_str}}} {value}')
            
    return "\n".join(output) + "\n"