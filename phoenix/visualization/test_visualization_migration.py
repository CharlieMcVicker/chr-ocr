import phoenix.visualization.generate_binarization_graphs as generate_binarization_graphs
import phoenix.visualization.generate_cnt_viewer as generate_cnt_viewer
import phoenix.visualization.generate_column_confidence_histogram as generate_column_confidence_histogram
import phoenix.visualization.generate_confidence_heatmaps as generate_confidence_heatmaps
import phoenix.visualization.generate_confusion_matrix as generate_confusion_matrix
import phoenix.visualization.generate_metric_plots as generate_metric_plots
import phoenix.visualization.generate_performance_graphs as generate_performance_graphs
import phoenix.visualization.metrics_dashboard as metrics_dashboard
import phoenix.visualization.visualize_confusion as visualize_confusion
import phoenix.visualization.diagnose_columns as diagnose_columns
import phoenix.visualization.plot_layout as plot_layout
import phoenix.visualization.preview_bounding_boxes as preview_bounding_boxes

def test_visualization_imports():
    assert hasattr(generate_binarization_graphs, "main")
    assert hasattr(generate_cnt_viewer, "main")
    assert hasattr(generate_column_confidence_histogram, "main")
    assert hasattr(generate_confidence_heatmaps, "main")
    assert hasattr(generate_confusion_matrix, "main")
    assert hasattr(generate_metric_plots, "main")
    assert hasattr(generate_performance_graphs, "main")
    assert hasattr(visualize_confusion, "main")
    assert hasattr(diagnose_columns, "main")
    assert hasattr(plot_layout, "main")
    assert hasattr(preview_bounding_boxes, "main")
