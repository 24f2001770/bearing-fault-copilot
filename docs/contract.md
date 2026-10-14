# Data contract (draft v0.1)

The agreed shape of the data passed between our parts. Kushal owns this file. A change is announced in the team chat before it is merged. Every part also offers a mock mode that returns the samples below, so nobody is blocked.

## Endpoints

| Endpoint | What it does | Returns |
| --- | --- | --- |
| `GET /health` | Checks that every part is up | Status per part |
| `GET /recordings` | Lists the demo recordings | Recording ids, load, rpm, and the true label for demo use |
| `GET /signal` | Gives one window of vibration data for the chart | Sample rate and a downsampled list of samples |
| `POST /analyze` | Body: recording id and window index | The final answer below |
| `POST /confirm` | Body: request id and the human's decision (`confirmed` or `escalated`) | Stored confirmation |

## 1. Sensor result (classifier to orchestrator)

```json
{
  "recording_id": "OR007@6_0",
  "window_index": 12,
  "fault_type": "outer_race",
  "severity": "small",
  "confidence": 0.93,
  "probabilities": {"normal": 0.01, "inner_race": 0.02, "outer_race": 0.93, "ball": 0.04},
  "context": {"sensor": "drive_end", "sample_rate_hz": 12000, "load_hp": 0, "rpm": 1797}
}
```

`fault_type` is one of `normal`, `inner_race`, `outer_race`, `ball`. `severity` is one of `none`, `small` (0.007 in), `medium` (0.014 in), `large` (0.021 in).

## 2. Retrieval (orchestrator to retrieval and back)

Request:

```json
{"query": "outer race defect, small, deep groove ball bearing: causes and actions", "fault_type": "outer_race", "severity": "small", "top_k": 5}
```

Response:

```json
{"passages": [{"chunk_id": "skf-damage-p34-c2", "text": "...", "source_title": "Bearing damage and failure analysis", "source_type": "guide", "page": 34, "url": "https://..."}]}
```

`source_type` is `guide`, `playbook` or `log`. Synthetic log entries are always marked as synthetic.

## 3. Final answer (orchestrator to screen)

```json
{
  "request_id": "req-0001",
  "sensor": { },
  "explanation": "Plain-language summary of what is wrong.",
  "likely_causes": ["..."],
  "recommended_actions": [
    {"step": "...", "safety_critical": true, "citation_ids": ["skf-damage-p34-c2"]}
  ],
  "needs_human_confirm": true,
  "citations": [
    {"id": "skf-damage-p34-c2", "source_title": "...", "page": 34, "url": "https://...", "excerpt": "short snippet"}
  ],
  "uncertainty": {"level": "low", "note": "..."},
  "meta": {"model": "...", "served_on": "AMD ...", "latency_ms": {"classifier": 0, "retrieval": 0, "llm": 0, "total": 0}}
}
```

`sensor` repeats the sensor result from step 1. `uncertainty.level` is `low`, `medium` or `high`. Citation ids come only from retrieved chunks, never from the model's imagination.

## Rules

- Field names are lowercase with underscores, exactly as above.
- The data set for v0.1 is the 12 kHz drive end recordings with the SKF fault sizes (0.007, 0.014, 0.021 inch) plus normal, at all four loads.
- A change to this contract is announced in the team chat before it is merged.
