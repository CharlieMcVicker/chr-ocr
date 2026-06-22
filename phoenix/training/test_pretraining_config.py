import unittest
from phoenix.config import TrainingConfig, PreTrainingPhaseConfig, SweepConfig

class TestPreTrainingPhaseConfig(unittest.TestCase):
    def test_pre_training_phase_serialization(self):
        # Create configs
        train_cfg = TrainingConfig(total_epochs=5, iterations_per_epoch=100)
        pretrain_phase = PreTrainingPhaseConfig(
            config=train_cfg,
            output_dir="test_pretrain_output",
            checkpoint_path="test_pretrain_checkpoint.checkpoint"
        )
        
        sweep_cfg = SweepConfig(
            experiments=[],
            pre_training_phase=pretrain_phase
        )
        
        # Serialize to dict
        serialized = sweep_cfg.to_dict()
        
        self.assertIn("pre_training_phase", serialized)
        self.assertEqual(serialized["pre_training_phase"]["output_dir"], "test_pretrain_output")
        self.assertEqual(serialized["pre_training_phase"]["checkpoint_path"], "test_pretrain_checkpoint.checkpoint")
        self.assertEqual(serialized["pre_training_phase"]["config"]["total_epochs"], 5)
        
        # Deserialize back
        deserialized = SweepConfig.from_dict(serialized)
        
        self.assertIsNotNone(deserialized.pre_training_phase)
        self.assertEqual(deserialized.pre_training_phase.output_dir, "test_pretrain_output")
        self.assertEqual(deserialized.pre_training_phase.checkpoint_path, "test_pretrain_checkpoint.checkpoint")
        self.assertEqual(deserialized.pre_training_phase.config.total_epochs, 5)
        self.assertEqual(deserialized.pre_training_phase.config.iterations_per_epoch, 100)

    def test_capping_and_caching_parameters(self):
        cfg = TrainingConfig(
            pretrain_cnt_cap=4500,
            use_cached_cnt=True,
            cnt_cache_dir="custom_cache_dir"
        )
        self.assertEqual(cfg.pretrain_cnt_cap, 4500)
        self.assertEqual(cfg.use_cached_cnt, True)
        self.assertEqual(cfg.cnt_cache_dir, "custom_cache_dir")
        
        serialized = cfg.to_dict()
        self.assertEqual(serialized["pretrain_cnt_cap"], 4500)
        self.assertEqual(serialized["use_cached_cnt"], True)
        self.assertEqual(serialized["cnt_cache_dir"], "custom_cache_dir")
        
        deserialized = TrainingConfig.from_dict(serialized)
        self.assertEqual(deserialized.pretrain_cnt_cap, 4500)
        self.assertEqual(deserialized.use_cached_cnt, True)
        self.assertEqual(deserialized.cnt_cache_dir, "custom_cache_dir")

    def test_mock_cached_cnt_loader(self):
        import tempfile
        import os
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "cnt_cache_manifest.json")
            mock_manifest = {
                "cnt_01_verse_line_00": [
                    {
                        "id": "cnt_01_verse_line_00",
                        "dataset": "cnt",
                        "variation_id": "cnt_01_verse_line_00_cached_0",
                        "tiff_path": "dummy.tiff",
                        "gt_path": "dummy.gt.txt",
                        "box_path": "dummy.box",
                        "lstmf_path": "dummy.lstmf",
                        "label": "Ꭰ",
                        "variation": 0
                    }
                ]
            }
            with open(manifest_path, "w") as f:
                json.dump(mock_manifest, f)
            
            self.assertTrue(os.path.exists(manifest_path))
            with open(manifest_path, "r") as f:
                loaded = json.load(f)
            self.assertIn("cnt_01_verse_line_00", loaded)

if __name__ == "__main__":
    unittest.main()
