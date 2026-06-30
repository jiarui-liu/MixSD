#!/bin/bash

OUTPUT_DIR="/path/to/mixsd_data/mixsd/output"
SCRIPT_DIR="/path/to/MixSD/mixsd/math_operation_dataset"
RESULTS_CSV="$SCRIPT_DIR/eval_results.csv"

# Clear previous results
rm -f "$RESULTS_CSV"
echo "Results will be saved to: $RESULTS_CSV"

# Find all jsonl files and run evaluation on each
find "$OUTPUT_DIR" -type f -name "*.jsonl" | while read -r file; do
    echo "Evaluating: $file"
    python "$SCRIPT_DIR/eval_output.py" "$file" "$RESULTS_CSV"
done

echo ""
echo "========================================"
echo "All evaluations complete!"
echo "Results saved to: $RESULTS_CSV"
echo "========================================"
