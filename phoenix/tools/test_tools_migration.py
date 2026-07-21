import phoenix.tools.download_scans as download_scans
import phoenix.tools.integrate_cnt as integrate_cnt
import phoenix.tools.package_cnt_test_data as package_cnt_test_data
import phoenix.tools.process_all_cnt as process_all_cnt
import phoenix.tools.process_all_scans as process_all_scans
import phoenix.tools.scrape_all_cnt as scrape_all_cnt
import phoenix.tools.apply_space_corrections as apply_space_corrections
import phoenix.tools.find_missing_spaces as find_missing_spaces
import phoenix.tools.analyze_dataset_character_frequencies as analyze_dataset_character_frequencies
import phoenix.tools.analyze_ocr_discrepancies as analyze_ocr_discrepancies
import phoenix.tools.test_training_routes as test_training_routes
import phoenix.tools.evaluate_lang_classification as evaluate_lang_classification
import phoenix.tools.prepare_training_data as prepare_training_data
import phoenix.tools.prepare_v2_training_data as prepare_v2_training_data

def test_tools_imports():
    assert hasattr(download_scans, "parse_url_line")
    assert hasattr(integrate_cnt, "main")
    assert hasattr(package_cnt_test_data, "main")
    assert hasattr(process_all_cnt, "main")
    assert hasattr(process_all_scans, "main")
    assert hasattr(scrape_all_cnt, "main")
    assert hasattr(apply_space_corrections, "load_exclusions")
    assert hasattr(find_missing_spaces, "find_missing_spaces")
    assert hasattr(analyze_dataset_character_frequencies, "main")
    assert hasattr(analyze_ocr_discrepancies, "analyze_discrepancies")
    assert hasattr(test_training_routes, "run_tests")
    assert hasattr(evaluate_lang_classification, "is_cherokee_char")
    assert hasattr(prepare_training_data, "main")
    assert hasattr(prepare_v2_training_data, "main")
