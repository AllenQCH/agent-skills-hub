# Extended Guidance

## Contents

  - [Keras/TensorFlow](#kerastensorflow)
- [Visualization & Analysis](#visualization-analysis)
  - [Custom Charts](#custom-charts)
  - [Reports](#reports)
- [Best Practices](#best-practices)
  - [1. Organize with Tags and Groups](#1-organize-with-tags-and-groups)
  - [2. Log Everything Relevant](#2-log-everything-relevant)
  - [3. Use Descriptive Names](#3-use-descriptive-names)
  - [4. Save Important Artifacts](#4-save-important-artifacts)
  - [5. Use Offline Mode for Unstable Connections](#5-use-offline-mode-for-unstable-connections)
- [Team Collaboration](#team-collaboration)
  - [Share Runs](#share-runs)
  - [Team Projects](#team-projects)
- [Pricing](#pricing)
- [Resources](#resources)
- [See Also](#see-also)

### Keras/TensorFlow

```python
import wandb
from wandb.keras import WandbCallback

# Initialize
wandb.init(project="keras-demo")

# Add callback
model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=10,
    callbacks=[WandbCallback()]  # Auto-logs metrics
)
```

## Visualization & Analysis

### Custom Charts

```python
# Log custom visualizations
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
wandb.log({"custom_plot": wandb.Image(fig)})

# Log confusion matrix
wandb.log({"conf_mat": wandb.plot.confusion_matrix(
    probs=None,
    y_true=ground_truth,
    preds=predictions,
    class_names=class_names
)})
```

### Reports

Create shareable reports in W&B UI:
- Combine runs, charts, and text
- Markdown support
- Embeddable visualizations
- Team collaboration

## Best Practices

### 1. Organize with Tags and Groups

```python
wandb.init(
    project="my-project",
    tags=["baseline", "resnet50", "imagenet"],
    group="resnet-experiments",  # Group related runs
    job_type="train"             # Type of job
)
```

### 2. Log Everything Relevant

```python
# Log system metrics
wandb.log({
    "gpu/util": gpu_utilization,
    "gpu/memory": gpu_memory_used,
    "cpu/util": cpu_utilization
})

# Log code version
wandb.log({"git_commit": git_commit_hash})

# Log data splits
wandb.log({
    "data/train_size": len(train_dataset),
    "data/val_size": len(val_dataset)
})
```

### 3. Use Descriptive Names

```python
# ✅ Good: Descriptive run names
wandb.init(
    project="nlp-classification",
    name="bert-base-lr0.001-bs32-epoch10"
)

# ❌ Bad: Generic names
wandb.init(project="nlp", name="run1")
```

### 4. Save Important Artifacts

```python
# Save final model
artifact = wandb.Artifact('final-model', type='model')
artifact.add_file('model.pth')
wandb.log_artifact(artifact)

# Save predictions for analysis
predictions_table = wandb.Table(
    columns=["id", "input", "prediction", "ground_truth"],
    data=predictions_data
)
wandb.log({"predictions": predictions_table})
```

### 5. Use Offline Mode for Unstable Connections

```python
import os

# Enable offline mode
os.environ["WANDB_MODE"] = "offline"

wandb.init(project="my-project")
# ... your code ...

# Sync later
# wandb sync <run_directory>
```

## Team Collaboration

### Share Runs

```python
# Runs are automatically shareable via URL
run = wandb.init(project="team-project")
print(f"Share this URL: {run.url}")
```

### Team Projects

- Create team account at wandb.ai
- Add team members
- Set project visibility (private/public)
- Use team-level artifacts and model registry

## Pricing

- **Free**: Unlimited public projects, 100GB storage
- **Academic**: Free for students/researchers
- **Teams**: $50/seat/month, private projects, unlimited storage
- **Enterprise**: Custom pricing, on-prem options

## Resources

- **Documentation**: https://docs.wandb.ai
- **GitHub**: https://github.com/wandb/wandb (10.5k+ stars)
- **Examples**: https://github.com/wandb/examples
- **Community**: https://wandb.ai/community
- **Discord**: https://wandb.me/discord

## See Also

- `references/sweeps.md` - Comprehensive hyperparameter optimization guide
- `references/artifacts.md` - Data and model versioning patterns
- `references/integrations.md` - Framework-specific examples
