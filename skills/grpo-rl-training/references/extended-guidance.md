# Extended Guidance

## Contents

  - [3. Custom Dataset Integration](#3-custom-dataset-integration)
- [Deployment and Inference](#deployment-and-inference)
  - [Save and Merge LoRA](#save-and-merge-lora)
  - [Inference Example](#inference-example)
- [Best Practices Checklist](#best-practices-checklist)
- [Troubleshooting Guide](#troubleshooting-guide)
  - [Debugging Workflow](#debugging-workflow)
  - [Quick Fixes](#quick-fixes)
- [References and Resources](#references-and-resources)
- [Usage Instructions for Agents](#usage-instructions-for-agents)
- [Additional Reference](#additional-reference)

### 3. Custom Dataset Integration
```python
def load_custom_knowledge_base(csv_path):
    """Example: School communication platform docs."""
    import pandas as pd
    df = pd.read_csv(csv_path)

    dataset = Dataset.from_pandas(df).map(lambda x: {
        'prompt': [
            {'role': 'system', 'content': CUSTOM_SYSTEM_PROMPT},
            {'role': 'user', 'content': x['question']}
        ],
        'answer': x['expert_answer']
    })
    return dataset
```

---

## Deployment and Inference

### Save and Merge LoRA
```python
# Merge LoRA adapters into base model
if hasattr(trainer.model, 'merge_and_unload'):
    merged_model = trainer.model.merge_and_unload()
    merged_model.save_pretrained("production_model")
    tokenizer.save_pretrained("production_model")
```

### Inference Example
```python
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="production_model",
    tokenizer=tokenizer
)

result = generator(
    [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': "What is 15 + 27?"}
    ],
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)
print(result[0]['generated_text'])
```

---

## Best Practices Checklist

**Before Training:**
- [ ] Validate dataset format (prompts as List[Dict])
- [ ] Test reward functions on sample data
- [ ] Calculate expected max_prompt_length from data
- [ ] Choose appropriate num_generations based on GPU memory
- [ ] Set up logging (wandb recommended)

**During Training:**
- [ ] Monitor reward progression (should increase)
- [ ] Check reward_std (should stay > 0.1)
- [ ] Watch for OOM errors (reduce batch size if needed)
- [ ] Sample generations every 50-100 steps
- [ ] Validate format compliance on holdout set

**After Training:**
- [ ] Merge LoRA weights if using PEFT
- [ ] Test on diverse prompts
- [ ] Compare to baseline model
- [ ] Document reward weights and hyperparameters
- [ ] Save reproducibility config

---

## Troubleshooting Guide

### Debugging Workflow
1. **Isolate reward functions** - Test each independently
2. **Check data distribution** - Ensure diversity in prompts
3. **Reduce complexity** - Start with single reward, add gradually
4. **Monitor generations** - Print samples every N steps
5. **Validate extraction logic** - Ensure answer parsing works

### Quick Fixes
```python
# Debug reward function
def debug_reward(completions, **kwargs):
    responses = [comp[0]['content'] for comp in completions]
    for i, r in enumerate(responses[:2]):  # Print first 2
        print(f"Response {i}: {r[:200]}...")
    return [1.0] * len(responses)  # Dummy rewards

# Test without training
trainer = GRPOTrainer(..., reward_funcs=[debug_reward])
trainer.generate_completions(dataset[:1])  # Generate without updating
```

---

## References and Resources

**Official Documentation:**
- TRL GRPO Trainer: https://huggingface.co/docs/trl/grpo_trainer
- DeepSeek R1 Paper: https://arxiv.org/abs/2501.12948
- Unsloth Docs: https://docs.unsloth.ai/

**Example Repositories:**
- Open R1 Implementation: https://github.com/huggingface/open-r1
- TRL Examples: https://github.com/huggingface/trl/tree/main/examples

**Recommended Reading:**
- Progressive Disclosure Pattern for agent instructions
- Reward shaping in RL (Ng et al.)
- LoRA paper (Hu et al., 2021)

---

## Usage Instructions for Agents

When this skill is loaded:

1. **Read this entire file** before implementing GRPO training
2. **Start with the simplest reward function** (e.g., length-based) to validate setup
3. **Use the templates** in `templates/` directory as starting points
4. **Reference examples** in `examples/` for task-specific implementations
5. **Follow the workflow** sequentially (don't skip steps)
6. **Debug incrementally** - add one reward function at a time

**Critical Reminders:**
- Always use multiple reward functions (3-5 is optimal)
- Monitor reward metrics, not loss
- Test reward functions before training
- Start small (num_generations=4), scale up gradually
- Save checkpoints frequently (every 100 steps)

This skill is designed for **expert-level implementation**. Beginners should start with supervised fine-tuning before attempting GRPO.

## Additional Reference

Read [Readme notes](readme-notes.md) when the packaged examples or background details are needed.
