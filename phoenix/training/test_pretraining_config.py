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

if __name__ == "__main__":
    unittest.main()
