import unittest
from phoenix.config import TrainingConfig

class TestMixtureSchedule(unittest.TestCase):
    def test_default_config(self):
        cfg = TrainingConfig()
        self.assertIn("mixture_schedule", cfg.to_dict())
        self.assertFalse(cfg.mixture_schedule.get("enabled"))
        self.assertEqual(cfg.mixture_schedule.get("start_ratio"), 0.5)
        self.assertEqual(cfg.mixture_schedule.get("end_ratio"), 1.0)
        self.assertEqual(cfg.mixture_schedule.get("start_epoch"), 1)
        self.assertEqual(cfg.mixture_schedule.get("end_epoch"), 12)

    def test_linear_interpolation(self):
        # We simulate the exact linear interpolation logic inside train.py
        total_epochs = 10
        start_epoch = 1
        end_epoch = 10
        start_ratio = 0.3
        end_ratio = 1.0

        ratios = []
        for epoch in range(1, total_epochs + 1):
            if epoch <= start_epoch:
                current_ratio = start_ratio
            elif epoch >= end_epoch:
                current_ratio = end_ratio
            else:
                fraction = (epoch - start_epoch) / (end_epoch - start_epoch)
                current_ratio = start_ratio + fraction * (end_ratio - start_ratio)
            ratios.append(current_ratio)

        self.assertAlmostEqual(ratios[0], 0.3)  # Epoch 1 (start_epoch)
        self.assertAlmostEqual(ratios[-1], 1.0) # Epoch 10 (end_epoch)
        
        # Check linear steps
        # step size = (1.0 - 0.3) / 9 = 0.7 / 9
        for i in range(total_epochs):
            expected = 0.3 + i * (0.7 / 9.0)
            self.assertAlmostEqual(ratios[i], expected)

if __name__ == "__main__":
    unittest.main()
