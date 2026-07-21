import phoenix.layout.extract_lines as extract_lines
import phoenix.layout.extract_low_confidence_rare_crops as extract_low_confidence_rare_crops
import phoenix.layout.classify_layout as classify_layout
import phoenix.layout.find_line_class_params as find_line_class_params

def test_layout_imports():
    assert hasattr(extract_lines, "main")
    assert hasattr(extract_low_confidence_rare_crops, "main")
    assert hasattr(classify_layout, "main")
    assert hasattr(find_line_class_params, "main")
