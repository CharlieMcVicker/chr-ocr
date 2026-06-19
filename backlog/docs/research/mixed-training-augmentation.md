# Mixed Training and Augmentation Specification

This document outlines the theoretical foundation, mathematical formulations, and operational specifications for the Cherokee Phoenix OCR mixed training and augmentation pipeline. It establishes a robust framework to handle historical print variations, ink degradation, and character imbalance, ensuring high-fidelity text recognition.

---

## 1. Stable Seeded Sampling with Salt Strings

To ensure deterministic, reproducible, and verifiable training, validation, and testing splits across dynamic datasets, we implement a stable seeded sampling algorithm using cryptographic hashing salted with specific identifiers. 

Traditional pseudo-random number generator (PRNG) seeding (e.g., `random.seed(42)`) is highly sensitive to the order of dataset traversal and dataset modifications. If a single image is added or removed, the entire assignment shifts. Salted hashing ensures that each sample's assignment is independent of other samples.

### Mathematical Formulation

Let $x$ be a unique identifier for a dataset sample (e.g., a file path or database primary key), and let $S \in \mathbb{R}$ be a string representing the salt (e.g., `"phoenix_ocr_split_v1"`).

We compute the stable MD5 hash value of the combined string representation:

$$\mathcal{H}(x, S) = \text{MD5}(x \mathbin{\Vert} S)$$

Let $\mathcal{V}(x, S)$ be the integer value of the first 8 hex characters of $\mathcal{H}(x, S)$:

$$\mathcal{V}(x, S) = \text{int}(\mathcal{H}(x, S)[0:8], 16)$$

The normalized projection $P(x, S) \in [0, 99]$ is defined as:

$$P(x, S) = \mathcal{V}(x, S) \bmod 100$$

Given target proportions for training ($T_{\text{train}}$), validation ($T_{\text{val}}$), and testing ($T_{\text{test}}$) where $T_{\text{train}} + T_{\text{val}} + T_{\text{test}} = 100$, the sample $x$ is assigned to a split based on the following boundary conditions:

$$\text{Split}(x) = \begin{cases} 
\text{Train}, & \text{if } 0 \le P(x, S) < T_{\text{train}} \\
\text{Validation}, & \text{if } T_{\text{train}} \le P(x, S) < T_{\text{train}} + T_{\text{val}} \\
\text{Test}, & \text{if } T_{\text{train}} + T_{\text{val}} \le P(x, S) < 100 
\end{cases}$$

### Python Implementation

```python
import hashlib

def get_stable_split(sample_id: str, salt: str, train_pct: int = 80, val_pct: int = 10) -> str:
    """Deterministic splitting of samples using salted MD5 hashing."""
    combined = f"{sample_id}_{salt}".encode('utf-8')
    hasher = hashlib.md5(combined)
    hex_digest = hasher.hexdigest()
    
    # Extract first 8 characters and map to [0, 99]
    val = int(hex_digest[:8], 16) % 100
    
    if val < train_pct:
        return "train"
    elif val < (train_pct + val_pct):
        return "val"
    else:
        return "test"

# Example validation
assert get_stable_split("page_001.png", "phoenix_v1") == get_stable_split("page_001.png", "phoenix_v1")
```

---

## 2. Dynamic Epoch-Specific Rotation Logic

During the initial epochs of training, large rotation angles can introduce severe geometric distortion, impeding the model's ability to learn canonical character features. As training progresses and the model learns robust representations, we dynamically expand the bounds of rotational augmentation (progressive curriculum learning).

### Mathematical Model

Let $e$ be the current epoch, and $E$ be the total number of scheduled training epochs. The maximum rotation angle $\theta_{\text{max}}(e)$ at epoch $e$ is defined using a progressive polynomial scaling factor:

$$\theta_{\text{max}}(e) = \theta_{\text{base}} + (\theta_{\text{limit}} - \theta_{\text{base}}) \cdot \left(\frac{e}{E}\right)^\gamma$$

Where:
*   $\theta_{\text{base}}$: The initial maximum rotation angle at epoch $0$ (e.g., $1.0^\circ$).
*   $\theta_{\text{limit}}$: The absolute upper bound of rotation (e.g., $15.0^\circ$).
*   $\gamma \in \mathbb{R}^+$: The curriculum growth rate exponent. If $\gamma = 1$, the scaling is linear. If $\gamma > 1$, augmentation remains mild for longer and grows rapidly near the end. If $\gamma < 1$, it expands quickly in early epochs.

### Implementation inside PyTorch Dataset

```python
import random
import torchvision.transforms.functional as TF
from torch.utils.data import Dataset

class EpochCurriculumDataset(Dataset):
    def __init__(self, samples, theta_base=1.0, theta_limit=15.0, gamma=2.0, total_epochs=100):
        self.samples = samples
        self.theta_base = theta_base
        self.theta_limit = theta_limit
        self.gamma = gamma
        self.total_epochs = total_epochs
        self.current_epoch = 0

    def set_epoch(self, epoch: int):
        self.current_epoch = min(epoch, self.total_epochs)

    def _get_max_rotation(self) -> float:
        ratio = self.current_epoch / self.total_epochs
        return self.theta_base + (self.theta_limit - self.theta_base) * (ratio ** self.gamma)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img, label = self.samples[idx]
        max_rot = self._get_max_rotation()
        angle = random.uniform(-max_rot, max_rot)
        
        # Apply the dynamic rotation
        img_rotated = TF.rotate(img, angle)
        return img_rotated, label
```

---

## 3. Dynamic Oversampling Formulas

Cherokee historical text contains highly imbalanced character distributions (syllabary frequencies). To prevent the network from overfitting to high-frequency syllables and ignoring minority characters, we apply a dynamic character-level oversampling factor to the text lines.

### Oversampling Formulation

Let $C$ be the set of all Cherokee syllabary characters, and $N_c$ be the raw count of occurrences of character $c \in C$ in the baseline dataset.
For any text line sample $x$, let $C_x \subseteq C$ be the set of unique characters present in $x$'s transcription.

The difficulty metric $\mathcal{D}(x)$ of a sample is proportional to the rarity of its constituent characters:

$$\mathcal{D}(x) = \max_{c \in C_x} \left( \frac{1}{N_c + 1} \right)$$

To construct the dynamic oversampling weight $W(x)$ for line sample $x$, we utilize a smoothed power-law ratio:

$$W(x) = \left( \frac{\max_{y} \mathcal{D}(y)}{\mathcal{D}(x) + \epsilon} \right)^\alpha$$

Where:
*   $\epsilon > 0$ is a stabilization constant (e.g., $10^{-6}$) to prevent division by zero.
*   $\alpha \in [0, 1.0]$ is the smoothing factor. When $\alpha = 0$, sampling is uniform across all samples. When $\alpha = 1.0$, sampling scales linearly with rarity.

### Sampling Probability

The probability $P(x)$ of selecting sample $x$ during batch generation is defined as:

$$P(x) = \frac{W(x)}{\sum_{j=1}^{M} W(j)}$$

Where $M$ is the total size of the unique dataset pool.

---

## 4. Noise Augmentation Parameter Blocks

To simulate ink splatter, bleed-through, paper degradation, and historical scanning artifacts, we execute structured noise injection using pre-calibrated parameter blocks within an Albumentations pipeline.

### Ink Wash and Pixel-Level Blur (Smudging) Noise

This method simulates physical wet-ink bleeding, smudging, and spot-mold deterioration on historical paper, which is particularly common in historical Cherokee scan sources like the Cherokee New Testament (CNT). 

#### Mathematical Formulation

Let $I_{i,j}$ be the pixel intensity of the image at coordinate $(i, j)$ in a grayscale or color image. Let $p \in [0, 1.0]$ be the probability of applying the noise, and let $\lambda \in [0, 1.0]$ be the intensity scale.

1.  **Salt and Pepper Injection**:
    We compute the total number of affected pixels $N = \lfloor H \times W \times \lambda \times 0.05 \rfloor$.
    - A set of $N$ coordinates is randomly selected and set to black ($[0, 0, 0]$ or $0$) to simulate ink splatter, ink bleed, or spot-mold.
    - A separate set of $\lfloor N / 2 \rfloor$ coordinates is randomly selected and set to white ($[255, 255, 255]$ or $255$) to simulate physical wear, paper fiber spots, or fading.

2.  **GaussianBlur Smudging**:
    To simulate the physical bleeding of wet ink into neighboring paper fibers, we apply a Gaussian filter to the noisy image:
    
    $$I_{\text{blurred}} = I_{\text{noisy}} * G_{\sigma}$$
    
    where the kernel size $k$ of the filter $G$ is dynamically scaled with the intensity:
    
    $$k = \begin{cases} 
    3 \times 3, & \text{if } \lambda < 0.5 \\
    5 \times 5, & \text{if } \lambda \ge 0.5 
    \end{cases}$$

3.  **Intensity Blending**:
    The final smudged image $I_{\text{final}}$ is a linear interpolation of the blurred image and the original image:
    
    where the blending coefficient $\alpha = \max(0.1, \min(0.9, \lambda))$ maps the intensity parameter directly to blending weight.

### Pixel-Level Coarse Dropout (Micro-Erasures) Noise

To simulate dry-type ink starvation and physical print-fade (often observed in historical Bible and New Testament print sources like the CNT), we apply high-frequency coarse dropout at a very fine pixel scale.

#### Mathematical Formulation

Let $I_{i, j}$ be the pixel intensity at coordinate $(i, j)$ of a grayscale image. Let $N_H$ be the number of holes, randomly sampled from a range $[h_{\text{min}}, h_{\text{max}}]$ (typically $[20, 60]$ for high-frequency density).

For each hole $k \in \{1, 2, \dots, N_H\}$, we sample a random height $h_k$ and width $w_k$ from the size range $[s_{\text{min}}, s_{\text{max}}]$ (typically $[1, 2]$ pixels for micro-level details) and a random center coordinate $(y_k, x_k)$.

Let $R_k = [y_k - \lfloor h_k/2 \rfloor, y_k + \lceil h_k/2 \rceil] \times [x_k - \lfloor w_k/2 \rfloor, x_k + \lceil w_k/2 \rceil]$ be the rectangular region defined by hole $k$.

For any pixel $(i, j)$ lying inside any rectangular region $R_k$, the intensity is set to the background fill value (typically $255$ for light backgrounds):

$$I_{\text{final}, i, j} = \begin{cases} 255, & \text{if } (i, j) \in \bigcup_{k=1}^{N_H} R_k \text{ with probability } p \\ I_{i, j}, & \text{otherwise} \end{cases}$$

### Staged Multi-Scale Elastic and Grid Distortion

Historically printed text documents exhibit multi-scale spatial deformations, which we model using a compound, dual-scale transformation to simulate both localized high-frequency paper warp (elastic transform) and wide-range low-frequency page page-folds and camera skew (grid distortion).

#### Mathematical Formulation

Let $I(x, y)$ be the input pixel intensity at coordinate $(x, y)$.

1. **Local High-Frequency Elastic Distortion**:
   Localized physical warps, paper fiber unevenness, and physical handling distress are modeled using a randomized, smoothed vector field $\Phi_{\text{elastic}}(x, y) = (x + \Delta x_e, y + \Delta y_e)$. The displacement field components $\Delta x_e$ and $\Delta y_e$ are computed by convolving random noise fields with a Gaussian kernel:
   
   $$\Delta x_e = \alpha \cdot (\eta_x * G_{\sigma}), \quad \Delta y_e = \alpha \cdot (\eta_y * G_{\sigma})$$
   
   where $\eta_x, \eta_y \sim \mathcal{N}(0, \mathbf{I})$ represent independent random Gaussian fields, $G_{\sigma}$ is a 2D Gaussian filter with standard deviation $\sigma$ (representing spatial scale), and $\alpha$ is the scaling factor (controlling amplitude).

2. **Wide-Range Low-Frequency Grid Distortion**:
   Large-scale page curvature and binding spine distortion are modeled using a displacement field $\Phi_{\text{grid}}(x, y) = (x + \Delta x_g, y + \Delta y_g)$. The input image domain is divided into a regular grid of size $M \times N$ control cells. Random displacement vectors are sampled at cell vertices and smoothly interpolated across the domain using bicubic splines:
   
   $$\Phi_{\text{grid}}(x, y) = \text{BicubicSpline}(\mathcal{V}_{M, N})$$

3. **Compound Multi-Scale Distortion Flow**:
   In the multi-scale configuration, rather than selecting one distortion type at random, both transforms are applied sequentially (compounded) to simulate realistic paper distress:
   
   $$I_{\text{distorted}}(x, y) = I\left( \Phi_{\text{elastic}}\left( \Phi_{\text{grid}}(x, y) \right) \right)$$
   
   This ensures that local character skewing and shearing effects compound naturally on top of large-scale undulating page curvature, preserving character legibility while maximizing geometric training robustness.

### Page Curl and Spine Curvature Distortion

To simulate the non-rigid spatial warp typical of book spines or page margins in historical document scans, we implement a custom OpenCV-based coordinate-mapping utility. This distortion vertically curves the text lines and horizontally compresses (squishes) text as it approaches the left or right image margin.

#### Mathematical Formulation

Let $I(x, y)$ be the input pixel intensity at coordinate $(x, y)$ of size $H 	imes W$. Let $w_{\text{curl}}$ be the width of the active distortion region, computed as $w_{\text{curl}} = \lfloor W \cdot r_{\text{curl}} \rfloor$ where $r_{\text{curl}} \in (0, 0.5]$ is the curl width ratio.

We compute the normalized margin distance $t(x) \in [0, 1.0]$ representing how close pixel $x$ is to the affected edge:

$$\text{If direction is left: } t(x) = \max\left(0.0, 1.0 - \frac{x}{w_{\text{curl}}}\right)$$

$$\text{If direction is right: } t(x) = \max\left(0.0, 1.0 - (W - 1.0 - x) / w_{\text{curl}}\right)$$

##### 1. Vertical Curvature (Bending)

Vertical curvature is modeled as a parabolic displacement applied to the $y$-coordinates. Let $b \in \mathbb{R}$ be the bending factor:

$$y_{\text{src}} = y + b \cdot H \cdot t(x)^2$$

This creates a parabolic vertical bend that decays quadratically to zero at a distance $w_{\text{curl}}$ from the margin.

##### 2. Horizontal Compression (Squishing)

Horizontal compression is modeled by mapping normalized coordinates in the active region using a fractional power function. Let $c \in [0, 1.0)$ be the compression intensity, and let $\gamma = \frac{1.0}{1.0 + c}$. 

We map target $x$-coordinates to source $x_{\text{src}}$-coordinates as follows:

*   **For direction left ($x < w_{\text{curl}}$):**
    
    $$x_{\text{src}} = w_{\text{curl}} \cdot \left(\frac{x}{w_{\text{curl}}}\right)^\gamma$$

*   **For direction right ($x > W - 1.0 - w_{\text{curl}}$):**
    
    $$x_{\text{src}} = (W - 1.0) - w_{\text{curl}} \cdot \left(\frac{W - 1.0 - x}{w_{\text{curl}}}\right)^\gamma$$

*   **Outside active regions ($t(x) = 0$):**
    
    $$x_{\text{src}} = x$$

Since $\gamma \le 1.0$, the derivative $\frac{d x_{\text{src}}}{d x} > 1.0$ near the edge, forcing a wider interval of original content in the source image to compress into a narrower target interval near the margins, simulating 3D cylindrical foreshortening.

The final distorted pixel coordinate $(x_{\text{src}}, y_{\text{src}})$ is mapped using bicubic interpolation with replicate border mode:

$$I_{\text{distorted}}(x, y) = I(x_{\text{src}}, y_{\text{src}})$$

### Configuration Specification (YAML)

```yaml
augmentation_pipeline:
  seed: 42
  stages:
    - name: ink_degradation
      probability: 0.8
      parameters:
        erosion_kernel_min: 1
        erosion_kernel_max: 3
        dilation_kernel_min: 1
        dilation_kernel_max: 2
    - name: spatial_distortion
      probability: 0.5
      parameters:
        alpha: 35.0
        sigma: 4.5
        alpha_affine: 1.5
    - name: noise_injection
      probability: 0.7
      parameters:
        gaussian_var_limit_min: 10.0
        gaussian_var_limit_max: 50.0
        salt_pepper_amount: 0.008
```

### Python Implementation

```python
import albumentations as A
import numpy as np
import cv2

def get_historical_degradation_pipeline(cfg: dict) -> A.Compose:
    return A.Compose([
        # Simulate Ink Bleed & Erosion via Morphological ops wrapped in Lambda or standard ops
        A.OneOf([
            A.Dilate(scale=(1, cfg["stages"][0]["parameters"]["dilation_kernel_max"]), p=0.5),
            A.Erode(scale=(1, cfg["stages"][0]["parameters"]["erosion_kernel_max"]), p=0.5),
        ], p=cfg["stages"][0]["probability"]),
        
        # Simulate paper warping and non-rigid physical distress
        A.ElasticTransform(
            alpha=cfg["stages"][1]["parameters"]["alpha"],
            sigma=cfg["stages"][1]["parameters"]["sigma"],
            alpha_affine=cfg["stages"][1]["parameters"]["alpha_affine"],
            border_mode=cv2.BORDER_CONSTANT,
            value=255,
            p=cfg["stages"][1]["probability"]
        ),
        
        # Add sensor and historical printing noise
        A.OneOf([
            A.GaussNoise(var_limit=(cfg["stages"][2]["parameters"]["gaussian_var_limit_min"], 
                                   cfg["stages"][2]["parameters"]["gaussian_var_limit_max"]), p=0.5),
            A.CoarseDropout(max_holes=8, max_height=8, max_width=8, fill_value=0, p=0.5),
        ], p=cfg["stages"][2]["probability"])
    ])
```

---

## 5. Binarization Bypasses

Document pre-processing systems frequently utilize global or adaptive binarization (e.g., Otsu's thresholding, Sauvola binarization) to convert images to strict binary black-and-white. However, physical degradation and ink bleed often lead to catastrophic information loss when binarized deterministically before inference.

```
Raw Gray-scale Image  ──► [ Sauvola Binarization ] ──► Broken Glyphs (Information Loss)
          │
          ▼ (Binarization Bypass Route)
 [ Grayscale Augmentations ] ──► [ CNN/ViT Encoder ] ──► Soft Probability Threshold Maps
```

### Bypass Strategy

1.  **Continuous Grayscale Training**: Models are trained directly on raw 8-bit grayscale images containing varying illumination fields. The feature extractor learns a robust boundary definition instead of delegating thresholding to hand-crafted heuristic formulas.
2.  **Differentiable Thresholding Layers**: We introduce an optional threshold bypass layer inside the PyTorch forward pass:

$$\tilde{I}_{i,j} = \sigma\left(\frac{I_{i,j} - T_{i,j}}{\tau}\right)$$

Where:
*   $I_{i,j}$ is the normalized grayscale input intensity at pixel $(i, j)$.
*   $T_{i,j}$ is the local Sauvola threshold calculated at $(i, j)$.
*   $\sigma$ is the Sigmoid activation function.
*   $\tau$ is a temperature hyperparameter (e.g., $\tau = 0.05$). As $\tau \to 0$, the activation approaches a hard step-function (strict binarization) while remaining fully differentiable during backpropagation.

---

## 6. Step Learning Rate Decay Maths

We employ a Step Learning Rate Decay schedule to stabilize gradient descent as optimization approaches complex saddle points. The learning rate $\eta_e$ at epoch $e$ is scaled systematically by decay factor $\gamma$ after every fixed interval step size $S$.

### Mathematical Equation

Let $\eta_0$ be the initial learning rate, $S$ be the step size (decay frequency in epochs), and $\gamma$ be the multiplicative factor of learning rate decay.

$$\eta_e = \eta_0 \cdot \gamma^{\lfloor \frac{e}{S} \rfloor}$$

Where:
*   $e \in \mathbb{N}_{\ge 0}$: The zero-indexed active training epoch.
*   $\gamma \in (0, 1.0)$: Typically set to $0.1$ or $0.5$.
*   $S \in \mathbb{N}_{\ge 1}$: Decides how many epochs are executed before the step decay is applied.
*   $\lfloor \cdot \rfloor$: The floor function, ensuring the exponent is a flat integer step.

### Step Decay Schedule Trace

Assuming $\eta_0 = 10^{-3}$, $\gamma = 0.5$, and $S = 20$:

| Epoch Range ($e$) | Exponent $\lfloor e / S \rfloor$ | Learning Rate Formula | Active Learning Rate ($\eta_e$) |
| :--- | :--- | :--- | :--- |
| $[0, 19]$ | $0$ | $10^{-3} \cdot (0.5)^0$ | $1.000 \times 10^{-3}$ |
| $[20, 39]$ | $1$ | $10^{-3} \cdot (0.5)^1$ | $5.000 \times 10^{-4}$ |
| $[40, 59]$ | $2$ | $10^{-3} \cdot (0.5)^2$ | $2.500 \times 10^{-4}$ |
| $[60, 79]$ | $3$ | $10^{-3} \cdot (0.5)^3$ | $1.250 \times 10^{-4}$ |

---

## 7. Execution Commands with `uv`

All pipeline operations, training tasks, and dependency resolutions must be executed using `uv` to maintain system virtual environment reproducibility.

### Environment Setup and Dependencies

Initialize and sync the environment lockfile:

```bash
# Sync local virtual environment with lockfile
uv sync
```

To add the required visual degradation, processing, and training dependencies:

```bash
# Install core computer vision and deep learning packages
uv add albumentations torch torchvision numpy opencv-python pyyaml
```

### Running the Mixed Augmentation and Training Pipeline

To launch the training pipeline with our epoch curriculum, salted split generation, and binarization bypasses:

```bash
# Run training using the production configuration
uv run scripts/train_staged.py \
  --config config/mixed_training_config.yaml \
  --salt "phoenix_ocr_split_v1" \
  --total-epochs 100 \
  --step-size 20 \
  --gamma-decay 0.5
```

To verify the deterministic nature of the dataset splits:

```bash
# Verify data distribution split using stable salted sampling
uv run scripts/verify_splits.py --dataset-dir data/raw --salt "phoenix_ocr_split_v1"
```
