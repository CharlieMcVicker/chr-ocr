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
    use_shared_pool: bool = False
    cnt_fraction: float = 0.1
    cnt_dir: str = "training_data/cnt"
    mixture_ratio: float = 0.8
    mixture_schedule: dict = field(default_factory=lambda: {
        "enabled": False,
        "start_ratio": 0.5,
        "end_ratio": 1.0,
        "start_epoch": 1,
        "end_epoch": 12,
    })
    max_cnt_samples: Optional[int] = None
    master_pool_prefix: Optional[str] = None
    skip_final_eval: bool = False
    
    # Learning rate options
    learning_rate: float = 0.0005
    lr_schedule: str = "constant"  # constant, step, exp
    lr_decay_rate: float = 0.5
    lr_decay_epochs: int = 4
    
    # Augmentation probabilities
    blur_prob: float = 0.1
    shadow_prob: float = 0.1
    distortion_prob: float = 0.4
    dropout_prob: float = 0.1
    bleedthrough_prob: float = 0.1
    distortion_limit: float = 0.05
    page_curl_prob: float = 0.0
    page_curl_direction: str = "random"
    page_curl_bending_factor: float = 0.15
    page_curl_compression_factor: float = 0.5
    page_curl_width_ratio: float = 0.3

    # CNT high-noise probabilities and intensity levels
    cnt_noise: dict = field(default_factory=lambda: {
        "blur": {"prob": 0.6, "limit_min": 3, "limit_max": 5},
        "shadow": {"prob": 0.5, "dimension": 6},
        "distortion": {
            "prob": 0.5,
            "limit": 0.15,
            "elastic_alpha": 1.0,
            "elastic_sigma": 15.0,
            "use_multi_scale": True
        },
        "dropout": {
            "prob": 0.5,
            "holes_min": 1,
            "holes_max": 4,
            "size_min": 4,
            "size_max": 10
        },
        "micro_dropout": {
            "prob": 0.4,
            "holes_min": 20,
            "holes_max": 60,
            "size_min": 1,
            "size_max": 2
        },
        "smudge": {"prob": 0.4, "intensity": 0.3}
    })

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

def deep_merge(base: dict, overrides: dict) -> dict:
    import copy
    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result


@dataclass
class SweepConfig:
    experiments: List[ExperimentConfig] = field(default_factory=list)
    base_config: Optional[dict] = None

    def to_dict(self) -> dict:
        data = {
            "experiments": [e.to_dict() for e in self.experiments]
        }
        if self.base_config:
            data["base"] = self.base_config
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'SweepConfig':
        base_dict = data.get("base")
        experiments_data = data.get("experiments", [])
        
        base_config_dict = base_dict.get("config", {}) if base_dict else None
        base_eval_epochs = base_dict.get("eval_epochs") if base_dict else None
        
        experiments = []
        for exp_data in experiments_data:
            exp_data_copy = dict(exp_data)
            if base_config_dict and "config" in exp_data_copy:
                exp_data_copy["config"] = deep_merge(base_config_dict, exp_data_copy["config"])
            if base_eval_epochs is not None and "eval_epochs" not in exp_data_copy:
                exp_data_copy["eval_epochs"] = base_eval_epochs
            experiments.append(ExperimentConfig.from_dict(exp_data_copy))
            
        return cls(
            experiments=experiments,
            base_config=base_dict
        )

    def save_to_json(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> 'SweepConfig':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
