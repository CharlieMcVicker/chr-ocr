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
    
    # Experiment / Run Identification
    slug: str = "default"

    # Paths / Directories
    train_manifest: str = "training_data/manifest_w_lang.json"
    model_dir: str = "training_data/dataset/model"
    _output_dir: Optional[str] = None
    _train_output_dir: Optional[str] = None
    _checkpoint_dir: Optional[str] = None
    _cnt_cache_dir: Optional[str] = None

    @property
    def output_dir(self) -> str:
        return self._output_dir if self._output_dir else f"data_temp/{self.slug}/dataset_epoch"

    @output_dir.setter
    def output_dir(self, val: str):
        self._output_dir = val

    @property
    def train_output_dir(self) -> str:
        return self._train_output_dir if self._train_output_dir else f"data_temp/{self.slug}/dataset_staged_output"

    @train_output_dir.setter
    def train_output_dir(self, val: str):
        self._train_output_dir = val

    @property
    def checkpoint_dir(self) -> str:
        return self._checkpoint_dir if self._checkpoint_dir else f"checkpoints/{self.slug}"

    @checkpoint_dir.setter
    def checkpoint_dir(self, val: str):
        self._checkpoint_dir = val

    @property
    def cnt_cache_dir(self) -> str:
        return self._cnt_cache_dir if self._cnt_cache_dir else f"data_temp/{self.slug}/cnt_cache"

    @cnt_cache_dir.setter
    def cnt_cache_dir(self, val: str):
        self._cnt_cache_dir = val
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
    pretrain_cnt_cap: Optional[int] = None
    use_cached_cnt: bool = False
    cnt_cache_dir: str = "data_temp/cnt_cache"
    master_pool_prefix: Optional[str] = None
    master_pool_variations: Optional[int] = None
    skip_final_eval: bool = False
    skip_cnt_eval: bool = False
    
    # Learning rate options
    learning_rate: float = 0.0005
    lr_schedule: str = "constant"  # constant, step, exp, cosine_warmup
    lr_decay_rate: float = 0.5
    lr_decay_epochs: int = 4
    lr_warmup_epochs: int = 2
    lr_t_max: Optional[int] = None
    lr_eta_min: float = 1e-6
    
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
        d = asdict(self)
        d["output_dir"] = self.output_dir
        d["train_output_dir"] = self.train_output_dir
        d["checkpoint_dir"] = self.checkpoint_dir
        d["cnt_cache_dir"] = self.cnt_cache_dir
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'TrainingConfig':
        # Filter out keys that aren't fields of TrainingConfig
        valid_keys = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        # Handle explicit override path keys from JSON data
        if "output_dir" in data:
            filtered_data["_output_dir"] = data["output_dir"]
        if "train_output_dir" in data:
            filtered_data["_train_output_dir"] = data["train_output_dir"]
        if "checkpoint_dir" in data:
            filtered_data["_checkpoint_dir"] = data["checkpoint_dir"]
        if "cnt_cache_dir" in data:
            filtered_data["_cnt_cache_dir"] = data["cnt_cache_dir"]

        # Merge dict fields (like cnt_noise) with default values
        if "cnt_noise" in filtered_data and isinstance(filtered_data["cnt_noise"], dict):
            default_noise = cls.__dataclass_fields__["cnt_noise"].default_factory()
            merged_noise = default_noise.copy()
            for k, v in filtered_data["cnt_noise"].items():
                if isinstance(v, dict) and k in merged_noise and isinstance(merged_noise[k], dict):
                    merged_noise[k] = {**merged_noise[k], **v}
                else:
                    merged_noise[k] = v
            filtered_data["cnt_noise"] = merged_noise
            
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
    eval_iterations: List[int]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "config": self.config.to_dict(),
            "eval_iterations": self.eval_iterations
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExperimentConfig':
        config_obj = TrainingConfig.from_dict(data["config"])
        eval_iterations = data.get("eval_iterations")
        if eval_iterations is None:
            eval_epochs = data.get("eval_epochs", [])
            iter_per_epoch = getattr(config_obj, "iterations_per_epoch", 200)
            eval_iterations = [epoch * iter_per_epoch for epoch in eval_epochs]
        return cls(
            id=data["id"],
            config=config_obj,
            eval_iterations=eval_iterations
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
class PreTrainingPhaseConfig:
    config: TrainingConfig
    output_dir: str
    checkpoint_path: str

    def to_dict(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "output_dir": self.output_dir,
            "checkpoint_path": self.checkpoint_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PreTrainingPhaseConfig':
        return cls(
            output_dir=data["output_dir"],
            checkpoint_path=data["checkpoint_path"],
            config=TrainingConfig.from_dict(data["config"])
        )


@dataclass
class SweepConfig:
    experiments: List[ExperimentConfig] = field(default_factory=list)
    base_config: Optional[dict] = None
    pre_training_phase: Optional[PreTrainingPhaseConfig] = None

    def to_dict(self) -> dict:
        data = {
            "experiments": [e.to_dict() for e in self.experiments]
        }
        if self.base_config:
            data["base"] = self.base_config
        if self.pre_training_phase:
            data["pre_training_phase"] = self.pre_training_phase.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'SweepConfig':
        base_dict = data.get("base")
        experiments_data = data.get("experiments", [])
        pre_training_phase_data = data.get("pre_training_phase")
        
        pre_training_phase = None
        if pre_training_phase_data:
            pre_training_phase = PreTrainingPhaseConfig.from_dict(pre_training_phase_data)
            
        base_config_dict = base_dict.get("config", {}) if base_dict else None
        base_eval_iterations = base_dict.get("eval_iterations") if base_dict else None
        base_eval_epochs = base_dict.get("eval_epochs") if base_dict else None
        
        experiments = []
        for exp_data in experiments_data:
            exp_data_copy = dict(exp_data)
            if base_config_dict and "config" in exp_data_copy:
                exp_data_copy["config"] = deep_merge(base_config_dict, exp_data_copy["config"])
            if "eval_iterations" not in exp_data_copy:
                if base_eval_iterations is not None:
                    exp_data_copy["eval_iterations"] = base_eval_iterations
                elif base_eval_epochs is not None and "eval_epochs" not in exp_data_copy:
                    exp_data_copy["eval_epochs"] = base_eval_epochs
            experiments.append(ExperimentConfig.from_dict(exp_data_copy))
            
        return cls(
            experiments=experiments,
            base_config=base_dict,
            pre_training_phase=pre_training_phase
        )

    def save_to_json(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> 'SweepConfig':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
