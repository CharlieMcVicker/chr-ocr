import unittest
import os
import shutil
import tempfile
from phoenix.training.sweep import get_checkpoint_for_iteration

class TestSweepCheckpointSelection(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for dummy checkpoints
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the directory after test
        shutil.rmtree(self.test_dir)

    def test_get_checkpoint_exact_match(self):
        # target iteration = 2400
        # Create a checkpoint matching exact iteration
        cp_path = os.path.join(self.test_dir, "chr_16.115_2400_2400.checkpoint")
        with open(cp_path, "w") as f:
            f.write("dummy")
            
        selected = get_checkpoint_for_iteration(self.test_dir, 2400)
        self.assertEqual(selected, cp_path)

    def test_get_checkpoint_fallback_closest_iteration(self):
        # target iteration = 2400
        # Checkpoints with actual iterations: 1875 (max 2400), 1790 (max 2300), and 1000 (max 2400)
        cp1 = os.path.join(self.test_dir, "chr_16.115_1875_2400.checkpoint")
        cp2 = os.path.join(self.test_dir, "chr_15.621_1790_2300.checkpoint")
        cp3 = os.path.join(self.test_dir, "chr_20.000_1000_2400.checkpoint")
        
        for cp in [cp1, cp2, cp3]:
            with open(cp, "w") as f:
                f.write("dummy")
                
        # Target iter is 2400.
        # cp1 actual iter is 1875 -> diff = 525
        # cp2 actual iter is 1790 -> diff = 610
        # cp3 actual iter is 1000 -> diff = 1400
        # Closest is cp1 (1875), even though cp2's max_iterations is 2300 (which is closer to 2400).
        selected = get_checkpoint_for_iteration(self.test_dir, 2400)
        self.assertEqual(selected, cp1)


class TestPreTrainingPhase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.results_file = os.path.join(self.test_dir, "results.json")
        self.best_config_path = os.path.join(self.test_dir, "best_config.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_pre_training_phase_dry_run(self):
        from phoenix.config import SweepConfig
        from phoenix.training.sweep import run_meta_parameter_sweep
        
        # Create a SweepConfig dictionary
        config_data = {
            "pre_training_phase": {
                "output_dir": os.path.join(self.test_dir, "pretrain_out"),
                "checkpoint_path": os.path.join(self.test_dir, "pretrain_out/model.checkpoint"),
                "config": {
                    "total_epochs": 1,
                    "iterations_per_epoch": 10
                }
            },
            "experiments": [
                {
                    "id": "exp_1",
                    "config": {
                        "mixture_ratio": 0.8
                    },
                    "eval_iterations": [10]
                }
            ]
        }
        
        sweep_config = SweepConfig.from_dict(config_data)
        
        # Run sweep in dry-run mode
        run_meta_parameter_sweep(
            sweep_config=sweep_config,
            test_dir=self.test_dir,
            traineddata_path="dummy.traineddata",
            results_file=self.results_file,
            dry_run=True,
            best_config_path=self.best_config_path
        )
        
        # Verify that the continue_from for the experiment was overridden to the pretrain checkpoint path
        self.assertEqual(
            sweep_config.experiments[0].config.continue_from,
            sweep_config.pre_training_phase.checkpoint_path
        )


if __name__ == "__main__":
    unittest.main()
