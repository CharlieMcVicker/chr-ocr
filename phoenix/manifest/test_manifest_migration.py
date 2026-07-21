import phoenix.manifest.add_predicted_lang_to_manifest as add_predicted_lang_to_manifest
import phoenix.manifest.enrich_manifest_with_ftm as enrich_manifest_with_ftm
import phoenix.manifest.filter_manifest as filter_manifest
import phoenix.manifest.build_frontend_index as build_frontend_index

def test_manifest_imports():
    assert hasattr(add_predicted_lang_to_manifest, "main")
    assert hasattr(enrich_manifest_with_ftm, "main")
    assert hasattr(filter_manifest, "main")
    assert hasattr(build_frontend_index, "main")
