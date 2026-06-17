import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class TrainingConfig:
    # Epoch/Iteration parameters
    total_epochs: int = 12
    iterations_per_epoch: int = 200
    variations_per_image: int = 3
    error_rate: float = 0.05
    
    # Paths / Directories
    train_manifest: str = "training_data/manifest_w_lang.json"
    output_dir: str = "training_data/dataset_epoch"
    model_dir: str = "training_data/dataset/model"
    train_output_dir: str = "training_data/dataset_staged_output"
    continue_from: Optional[str] = None
    old_traineddata: Optional[str] = None
    max_workers: Optional[int] = None
    use_dynamic_cnt: bool = False
    cnt_fraction: float = 0.1
    cnt_dir: str = "training_data/cnt"
    
    # Learning rate options
    learning_rate: float = 0.0005
    lr_schedule: str = "constant"  # constant, step, exp
    lr_decay_rate: float = 0.5
    lr_decay_epochs: int = 4
    
    # Augmentation probabilities
    blur_prob: float = 0.4
    shadow_prob: float = 0.3
    distortion_prob: float = 0.4
    dropout_prob: float = 0.3
    bleedthrough_prob: float = 0.25

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'TrainingConfig':
        # Filter out keys that aren't fields of TrainingConfig
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def save_to_json(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> 'TrainingConfig':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

@dataclass
class ExperimentConfig:
    id: str
    config: TrainingConfig
    eval_epochs: List[int]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "config": self.config.to_dict(),
            "eval_epochs": self.eval_epochs
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExperimentConfig':
        return cls(
            id=data["id"],
            config=TrainingConfig.from_dict(data["config"]),
            eval_epochs=data["eval_epochs"]
        )

@dataclass
class SweepConfig:
    experiments: List[ExperimentConfig] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "experiments": [e.to_dict() for e in self.experiments]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SweepConfig':
        return cls(
            experiments=[ExperimentConfig.from_dict(e) for e in data.get("experiments", [])]
        )

    def save_to_json(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> 'SweepConfig':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
