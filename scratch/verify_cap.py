import os
import json
import tempfile
from phoenix.config import TrainingConfig
from phoenix.training.sweep import SweepSampler

def test_training_config():
    print("Testing TrainingConfig...")
    config = TrainingConfig(max_cnt_samples=100)
    assert config.max_cnt_samples == 100, f"Expected 100, got {config.max_cnt_samples}"
    
    # Test JSON serialization / deserialization
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name
    try:
        config.save_to_json(temp_path)
        loaded = TrainingConfig.load_from_json(temp_path)
        assert loaded.max_cnt_samples == 100, f"Expected 100, got {loaded.max_cnt_samples}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    print("TrainingConfig test passed successfully!")

def test_sweep_sampler_cap():
    print("Testing SweepSampler cap functionality...")
    
    # Generate some dummy metadata index records
    records = []
    # 10 Phoenix items (with 1 variation each)
    for i in range(10):
        records.append({
            "id": f"phoenix_{i}",
            "dataset": "phoenix",
            "lstmf_path": f"path/to/phoenix_{i}.lstmf"
        })
    # 50 CNT items (with 1 variation each)
    for i in range(50):
        records.append({
            "id": f"cnt_{i}",
            "dataset": "cnt",
            "lstmf_path": f"path/to/cnt_{i}.lstmf",
            "has_rare": False
        })
        
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        metadata_path = f.name
        output_list_path = f.name + "_out.list"
        
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(records, f)
            
        # Scenario 1: Without max_cnt_samples cap
        # At mixture_ratio = 0.2, CNT target size is:
        # 10 phoenix * (1.0 - 0.2) / 0.2 = 40 CNT samples.
        SweepSampler.sample_to_list(
            metadata_index_path=metadata_path,
            output_list_path=output_list_path,
            mixture_ratio=0.2,
            epoch=1,
            max_cnt_samples=None
        )
        with open(output_list_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        # Phoenix records (10) + CNT records (40) = 50 lines total
        assert len(lines) == 50, f"Expected 50 lines, got {len(lines)}"
        cnt_lines = [l for l in lines if "cnt_" in l]
        assert len(cnt_lines) == 40, f"Expected 40 CNT lines, got {len(cnt_lines)}"
        print("Scenario 1 (No cap): Passed! (Found 40 CNT lines)")

        # Scenario 2: With max_cnt_samples cap = 15
        SweepSampler.sample_to_list(
            metadata_index_path=metadata_path,
            output_list_path=output_list_path,
            mixture_ratio=0.2,
            epoch=1,
            max_cnt_samples=15
        )
        with open(output_list_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        # Phoenix records (10) + capped CNT records (15) = 25 lines total
        assert len(lines) == 25, f"Expected 25 lines, got {len(lines)}"
        cnt_lines = [l for l in lines if "cnt_" in l]
        assert len(cnt_lines) == 15, f"Expected 15 CNT lines, got {len(cnt_lines)}"
        print("Scenario 2 (With cap = 15): Passed! (Found 15 CNT lines)")

    finally:
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        if os.path.exists(output_list_path):
            os.remove(output_list_path)
            
    print("SweepSampler cap test passed successfully!")

if __name__ == "__main__":
    test_training_config()
    test_sweep_sampler_cap()
    print("All verification tests passed successfully!")
