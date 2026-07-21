import phoenix.text.align_verses as align_verses
import phoenix.text.segment_verses as segment_verses
import phoenix.text.update_unicharsets as update_unicharsets

def test_text_imports():
    assert hasattr(align_verses, "align_book_transcriptions")
    assert hasattr(segment_verses, "process_book_verses")
    assert hasattr(update_unicharsets, "update_unicharset")
