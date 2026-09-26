# Large Language Model (LLM) Failure Modes & Benchmarks

This document provides a comprehensive structured summary of the reproducible failure modes, evaluation benchmarks, and empirical threat vectors identified in key scholarly literature.

## 1. Architectural & Structural Failures

| Failure Mode | Core Phenomenon | Evaluation Benchmark / Dataset | Primary Citation |
| :--- | :--- | :--- | :--- |
| **The Reversal Curse** | Autoregressive models fail to generalize "B is A" after learning "A is B" due to directional asymmetry in next-token prediction. | **Custom Celebrity/Fictional Relations Dataset:** Exact forward/backward entity evaluation framework testing role reversal. | Berglund et al., 2024 |
| **"Lost in the Middle"** | Information retrieval and constraint satisfaction degrade severely when crucial context is buried in the middle of long prompts. | **Multi-Document QA & Key-Value Retrieval:** Standardized benchmarks assessing multi-hop extraction accuracy across position variations. | Liu et al., 2024 |
| **Linear Scaling / Error Cascades** | Multi-step compositional logic decays exponentially because errors compound sequentially without true planning mechanisms. | **Compositional Graphs:** Multi-step addition, multiplication, and topological sorting problems. | Dziri et al., 2023 |
| **Superficial Heuristic Dependence** | Models collapse when task parameters deviate from training frequency distributions (e.g., shifts in cipher shifting or non-standard math). | **Variant Ciphers & Non-Standard Arithmetic:** Shifting task configurations to pinpoint the precise failure thresholds of probabilistic logic. | McCoy et al., 2023 |
| **Emergent Capabilities Illusion** | Perceived "quantum leaps" in model capabilities are often artifacts of non-linear metric choices rather than actual behavioral changes. | **Reproducible Metric Selection Tests:** Mathematical re-evaluations altering performance measurement scales on BIG-bench tasks. | Schaeffer et al., 2024 |

## 2. Adversarial & Prompt Injection Vulnerabilities

| Threat Vector | Core Phenomenon | Evaluation Benchmark / Dataset | Primary Citation |
| :--- | :--- | :--- | :--- |
| **Direct Jailbreaking** | Intentional direct prompting techniques override behavioral safety alignments to generate harmful or restricted outputs. | **JailbreakBench:** Open-source, reproducible standard testing 100 distinct adversarial behaviors across diverse target models. | Chao et al., 2024 |
| **Indirect Prompt Injection** | Untrusted payloads embedded within third-party data sources (e.g., PDFs, web scraps) hijack execution context during RAG/tool usage. | **Synthetic Tool Integration Benchmarks:** Data pipeline models simulating retrieval-augmented web sweeps and file analysis vectors. | Greshake et al., 2023 |
| **Dynamic Execution Manipulation** | Evolving exploit scripts continually achieve structural control over system guidelines through algorithmic refinement. | **PIArena (Prompt Injection Arena):** Comprehensive multi-module suite tracking dynamic Attack Success Rate (ASR) baselines. | Geng et al., 2026 |
| **High-Stakes Domain Exploits** | Targeted text injections compromise domain-specific guardrails, resulting in critical real-world logic failures. | **MPIB (Medical Prompt Injection Benchmark):** Dataset mapping injection vulnerabilities to severe outcome scales like Clinical Harm Event Rates. | Wang et al., 2026 |

---

## 3. Comprehensive Taxonomy Reference

For an overarching mapping of functional reasoning cracks (such as the distinct operational boundaries between embodied logic failures, narrative logic shortcuts, and formal reasoning limits), consult the systematic synthesis framework detailed in **Song et al., 2026** (*"A Survey on Large Language Model Reasoning Failures"*). This framework organizes disparate evaluation benchmarks into a unified diagnostic infrastructure for production AI systems.
