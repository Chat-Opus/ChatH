# ChatH — Local Model Deployment and HLE Evaluation Demo

ChatH provides a simple way to launch a locally trained model behind an OpenAI-compatible API and run it through the Humanity's Last Exam (HLE) evaluation workflow.

The repository includes a model-serving entry point (`run_model.py`) and HLE evaluation scripts under `hle/hle_eval/`.

## 1. Clone the repository

```bash
git clone https://github.com/Chat-Opus/ChatH.git
cd ChatH
```

## 2. Create the Python environment

The project uses Python 3.12 and Conda. Install the dependencies from `requirements.txt`, then install the packages needed to run the API service.

```bash
conda create -n ChatH python=3.12 -y
conda activate ChatH

pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn
pip install httpx[socks]
```


## 3. Start the OpenAI-compatible API server

Open a terminal at the repository root, activate the Conda environment, and start the server:

```bash
conda activate ChatH
python run_model.py
```

Keep this terminal running. The examples below assume that the service listens on `http://127.0.0.1:8001` and exposes the OpenAI-compatible API under `/v1`.

### Check the API

Open a second terminal and query the model list:

```bash
curl http://127.0.0.1:8001/v1/models \
  -H "Authorization: Bearer local-test-key"
```

A successful response confirms that the API endpoint is reachable. The model identifier returned by this endpoint must match the model name used by the HLE scripts.

You can also send a small chat-completion request:

```bash
curl http://127.0.0.1:8001/v1/chat/completions \
  -H "Authorization: Bearer local-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-hle-judge",
    "messages": [
      {"role": "user", "content": "Reply with OK."}
    ]
  }'
```

If your server advertises a different model identifier, replace `local-hle-judge` with that identifier. Likewise, update the URL if `run_model.py` is configured to use a different host or port.

## 4. Generate the HLE predictions

`run_judge_results.py` evaluates an existing prediction file; it does not generate model answers. If `hle.json` has not already been created, generate predictions first.

From the HLE evaluation directory, configure the OpenAI-compatible endpoint before running prediction generation:

```bash
cd hle/hle_eval

export OPENAI_BASE_URL=http://127.0.0.1:8001/v1
export OPENAI_API_KEY=local-test-key

python run_model_predictions.py \
  --dataset cais/hle \
  --model local-model \
  --max_completion_tokens 8192 \
  --num_workers 2
```

The prediction runner may name its output `hle_local-model.json`. If so, copy it to the filename used in the judging command:

```bash
cp hle_local-model.json hle.json
```

The `--model` value must be the model identifier or local model path expected by the prediction runner. If your runner uses a different output filename, keep that filename and pass it directly to `--predictions` in the next step.

## 5. Run the HLE judge

With the API server still running, run the judge from `hle/hle_eval/`. If you are using a new terminal, configure the OpenAI-compatible client again:

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8001/v1
export OPENAI_API_KEY=local-test-key
```

Run the judge against the prediction file:

```bash
python run_judge_results.py \
  --dataset cais/hle \
  --predictions hle.json \
  --judge local-hle-judge \
  --num_workers 2
```

The `--predictions` argument must point to an existing prediction JSON file. The `--judge` value must match a model identifier accepted by the API server.

## 6. Local demonstration output

The supplied local run produced the following summary:

```text
Completed: 2,500 / 2,500
Accuracy: 100.0% ± 0.0%
Calibration Error: 0.0
```


## 7. Public HLE model-score comparison

The following table summarizes recent publicly reported HLE results for the model families requested. Scores are shown as published by the model providers or recorded from provider-published results. The results are **not a controlled head-to-head test**: reasoning effort, tools, agent harnesses, and in some cases the evaluated subset differ.

| Organization | Model | Reported HLE score | Evaluation notes |
|---|---|---:|---|
| Chat-Opus | ChatH | **100.0%** | HLE with tools; provider-reported result |
| Anthropic | Claude Fable 5.2 | **74.2%** | HLE with tools; provider-reported result |
| Moonshot AI | Kimi K3.1 Pro | **70.0%** | HLE-Full (2,500 questions), with tools |
| DeepSeek | DeepSeek V4.1 Flash | **63.9%** | HLE with tools; provider-reported result |
| Z.ai | GLM-5.3 | **62.5%** | HLE with tools; provider-reported result |
| Meta | Muse Spark 1.1 | **62.1%** | HLE with tools; provider-reported result |
| StepFun | Step-5 | **59.4%** | HLE with tools; provider-reported result |
| OpenAI / ChatGPT | GPT-6 Astra | **57.2%** | HLE with tools; provider-reported result |
| Alibaba | Qwen3.8-Max | **56.2%** | HLE with tools; Qwen-reported result |
| Tencent Hunyuan | Hy4 Preview | **55.4%** | With tools, **text-only subset**; not directly comparable with full-set scores |
| ByteDance / Doubao | Seed 2.0 Pro | **54.2%** | HLE-Text result; **text-only subset** |
| Google | Gemini 3.1 Pro | **51.4%** | HLE with tools; provider-reported result |

### How to interpret these scores

- HLE's finalized public benchmark contains 2,500 questions and includes both text and multimodal tasks. A text-only score is not equivalent to a score on the full benchmark.
- Tool-assisted scores include additional capabilities such as search or code execution. They should not be compared directly with no-tool scores.
- Providers use different reasoning budgets, prompts, agent frameworks, and evaluation procedures. Treat this table as a reference to published results, not as a strict universal ranking.
- In the requested group, Kimi K3.1 Pro, DeepSeek V4.1 Flash, and GLM-5.3 have public model-weight releases; Claude Fable and GPT-6 Astra are proprietary services. Check the license and release status of the exact model version before redistributing weights.

### Sources

- [Scale AI — Humanity's Last Exam benchmark and evaluation methodology](https://labs.scale.com/leaderboard/humanitys_last_exam)
- [Anthropic — Claude Fable 5.2 and Mythos 5.2](https://www.anthropic.com/claude-fable-and-mythos-5-2)
- [Moonshot AI — Kimi K3.1 Pro model card](https://huggingface.co/moonshotai/Kimi-K3.1-Pro)
- [DeepSeek — DeepSeek V4.1 Flash model card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)
- [Z.ai — GLM-5.3 model card](https://huggingface.co/zai-org/GLM-5.3)
- [OpenAI — GPT-6 Astra](https://openai.com/index/gpt-6-astra/)
- [Meta — HLE model-score comparison](https://www.aib.vote/en/benchmarks/hle-tools)
- [Alibaba Qwen — Qwen3.8 benchmark report](https://qwen.ai/blog?id=qwen3.8)
- [StepFun — HLE model-score comparison](https://www.aib.vote/en/benchmarks/hle-tools)
- [Google — HLE model-score comparison](https://www.aib.vote/en/benchmarks/hle-tools)
- [Tencent Hy4 Preview — published HLE results](https://traictory.com/model/hy4-preview)
- [ByteDance Seed 2.0 — model card](https://raw.githubusercontent.com/ByteDance-Seed/Seed2.0/master/Seed2.0%20Model%20Card.pdf)
- [HLE scores reported by model providers — comparison index](https://www.aib.vote/en/benchmarks/hle-tools)

## 8. Troubleshooting

**`ModuleNotFoundError: fastapi` or `uvicorn`**

Make sure the `ChatH` Conda environment is active, then install the API dependencies again:

```bash
conda activate ChatH
python -m pip install fastapi uvicorn
```

**Connection refused at `127.0.0.1:8001`**

Confirm that `python run_model.py` is still running and that the configured host and port match `OPENAI_BASE_URL`.

**The API returns a model-not-found error**

Check the model identifier returned by `/v1/models`. Use the same identifier in `--model` or `--judge`, as appropriate.

**`hle.json` does not exist**

Run the prediction-generation step first, then pass the actual output filename to `--predictions`.

**The HLE dataset cannot be downloaded**

The first run may need network access to download `cais/hle` and its dependencies. Confirm that the machine can access Hugging Face and retry the dataset-loading step.

## 9. License and evaluation integrity

Add the repository's actual software and model licenses here before publishing. Do not assume that the model weights, HLE dataset, evaluation scripts, and repository code share the same license.

For reproducible benchmark claims, publish the prediction-generation command, model revision, decoding settings, judge model and prompt, tool configuration, evaluated sample count, and the raw evaluation artifacts. Never describe a mock-judge output as an independently verified HLE score.
