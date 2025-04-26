# NoisyMind-TidyAgent

A CLI scaffold for taming noisy, verbose LLM outputs into structured, validated, high-confidence answers — with full fallback logic, Prometheus metrics, and Grafana monitoring.

Built for developers and AI engineers who want agents that are reliable, auditable, and observable — not just lucky.

---

## Why This Exists

Large Language Models (LLMs) are powerful, but they often produce messy, verbose, or poorly structured outputs.  
That’s fine for playground demos — but dangerous in production.

This tool turns LLM responses into structured, validated, trackable artifacts you can monitor and trust.

It gives you:

- Strict JSON schema enforcement
- Confidence thresholding and fallback control
- Failure pattern analysis
- Real-time observability over agent performance

---

## Features

### Structured Agent Inference

- Forces strict JSON schema with Pydantic
- Rejects markdown wrapping, extra fields, and unstructured answers
- Filters out low-confidence outputs

### Resilience

- Retries with backoff on transient API failures
- Categorizes failures: API error, invalid JSON, low-confidence

### Batch Testing

- `batch_runner.py` stress-tests domain-diverse queries
- Tracks successes, fallbacks, and confidence drift

### Observability

- Exports Prometheus metrics via `metrics.txt`
- Real-time dashboarding through Prometheus and Grafana

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
```

### 3. Run a Single Query

```bash
python agent/cli.py --query "Explain Zero Trust architecture"
```

### 4. Run Batch Evaluation

```bash
python agent/batch_runner.py
```
Batch queries are loaded dynamically from `agent/queries.txt`.  
You can edit this file to customize test coverage.

### 5. Start the Metrics Server

```bash
python agent/metrics_server.py
```

### 6. Configure Prometheus

In `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "cli-agent"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

Run Prometheus via Docker:

```bash
docker run -d --name prometheus \
  -p 9090:9090 \
  -v /full/path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 7. Launch Grafana

```bash
docker run -d --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

Default login:  
Username: `admin`  
Password: `admin`

Import `agent_dashboard.json` to view fallback/success trends live.

---

## Exported Metrics

| Metric                                | Description                                    |
| ------------------------------------- | ---------------------------------------------- |
| `agent_success_total`                 | Valid structured answers                       |
| `agent_fallback_total`                | Any fallback (API error, JSON, low confidence) |
| `agent_fallback_api_error_total`      | API/network failure                            |
| `agent_fallback_json_error_total`     | Invalid JSON or schema violation               |
| `agent_fallback_confidence_low_total` | Valid format but confidence too low            |

---

## Use Cases

- Reliability monitoring for LLM-based agents
- QA validation pipelines for structured inference
- Model drift analysis over time
- Proving out structured agent reliability pre-production

---

## Project Structure

```
.
├── agent/
│   ├── cli.py
│   ├── batch_runner.py
│   ├── metrics_server.py
│   ├── log_writer.py
│   └── queries.txt
├── metrics.txt
├── prometheus.yml
├── .env
├── agent_dashboard.json
├── README.md
└── requirements.txt
```

---

## Tech Stack

- Python 3.10+
- OpenAI GPT-4 Turbo
- Pydantic
- Flask
- Prometheus
- Grafana

---

## Future Enhancements

- Add multi-agent comparison (evaluate multiple LLM models side-by-side)
- Introduce automatic Grafana alerts based on fallback thresholds
- Enable dynamic model selection at runtime via CLI flags
- Expand batch queries with categorized domains (Auth, Observability, Security)
- Integrate Slack or email notifications on high fallback rates


---

## License

MIT License
