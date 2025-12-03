# Rasoom Multimodal Communication Protocol Foundation — MCP-Compatible Messaging, Carnatic Encoding, and Tier-Aware Routing Blueprint

## Executive Summary

Augur Omega’s evolution from a compact command-line orchestrator managing 38 specialized agents to a large-scale, tiered system (Prime, Domain, Micro) necessitates a unified communication substrate capable of transmitting nuanced human intent across agent tiers. Rasoom is that substrate. It is a binary-first, multimodal inter-agent messaging protocol and runtime layer that converts human gestures, affect, and contextual cues into machine-optimal messages while retaining interpretability at intermediate stages. It is designed to integrate with the Model Context Protocol (MCP) even when the advertised function list is empty, introducing a registry shim that enables messaging, health endpoints, and progressive function discovery without mandating immediate catalog completeness.

This foundation delivers:
- An MCP-compatible inter-agent messaging layer, with shims for empty function lists and progressive discovery.
- A seven-stage pipeline (multimodal capture → decision trees → syllabic units → Carnatic swara → mathematical equations → number series → binary encoding) engineered for reversibility and interpretability.
- Tier-aware routing primitives (unicast, multicast, broadcast, aggregation, emergency bypass) with bounded latency targets, aggregation strategies, and controlled fan-out across ~2,700 agents.
- Affective and unconscious signal encoding that persists across transformations, enabling intent disambiguation and adaptive routing (e.g., escalate to Prime when frustration/confidence markers dominate; prefer local execution when curiosity/calm are present with low ambiguity).
- Compatibility layers for the 38-agent legacy system and current microagent/kosha scaffolds, preserving CLI operability and descriptive team configurations.
- Security and governance hooks via MCP (policy checks on issuance and delivery, RBAC attributes, audit channels), with Antakhara envisioned as the enforcement and audit anchor.
- Observability, SLIs/SLOs, and a phased roadmap from scaffolding to supervised processes, discovery/scheduling, and formal governance.

Information gaps include canonical, code-level definitions for Agenta, Pranava, and Antakhara, production-grade telemetry and discovery beyond logs, and MCP function catalogs beyond an empty list. The plan explicitly recognizes these gaps and adopts adaptable interfaces to bridge them through progressive integration.

Outcome: Rasoom provides minimal viable MCP-compatible messaging immediately, with a path to production-grade orchestration, security enforcement, and performance SLAs/SLOs.

![Rasoom: binary-first inter-agent messaging with affective and tier-aware routing](assets/images/rasoom/exec_summary_hero.png)

The figure above summarizes Rasoom’s role as the binary-first inter-agent substrate designed to carry intent and affect across tiers, integrate with MCP even when function lists are empty, and preserve interpretability through layered musical and mathematical representations.[^2]

---

## Foundations: Current Architecture Baseline and Gaps

The current orchestrator enforces provider-specific controls: local CPU workloads are serialized via a semaphore set to one; cloud LLM workloads are parallelized via a semaphore set to ten, with rate-limit detection (HTTP 429) and retry/backoff behavior. Generated code is validated via regex extraction and AST parsing; logs are written to files. Scaffolding exists for microagents and koshas with consistent status, process, and health interfaces, yet the system lacks true persistence, process supervision, service discovery, and real IPC. Team configurations describe capabilities and optimization metrics but remain descriptive rather than prescriptive. These baselines define a robust simulation environment but do not yet constitute a runtime fabric.

Rasoom’s minimal viable enhancement adds:
- Health endpoints that expose status, latency, error rates, and subscription counts.
- Binary-first messaging with RS error correction and tier-aware routing.
- MCP-compatible shims enabling empty-list function discovery and progressive integration.
- Observability instrumentation (metrics, logs, traces) aligned with proposed SLIs/SLOs.

The design purposefully augments, rather than replaces, orchestrators and CLI tools.

![Current hybrid orchestrator baseline and gaps](assets/images/rasoom/baseline_arch.png)

As shown in the baseline, provider concurrency and rate limits are already enforced. Rasoom adds an inter-agent messaging fabric that operates within those constraints, turning scaffolds into supervised processes with predictable routing, telemetry, and governance hooks.[^1]

### Provider Concurrency and Rate-Limit Posture

To ground routing and concurrency, Table 1 captures the documented posture.

### Table 1: Concurrency and rate limits per provider

| Provider        | Concurrency Setting | Timeout           | Rate-Limit Handling                               | Notes                                              |
|-----------------|---------------------|-------------------|---------------------------------------------------|----------------------------------------------------|
| Local CPU       | Semaphore = 1       | ~900s for calls   | None                                             | Serial execution for sensitive workloads           |
| Cloud LLM (Groq)| Semaphore = 10      | ~30s for calls    | Detects 429 responses and retries after a pause  | Cloud-first routing with local fallback            |

Implication: Any new messaging fabric must avoid uncontrolled fan-out, respect provider timeouts, and incorporate backoff-aware routing to remain compatible with the orchestrator’s hybrid posture.

### Baseline vs. Current State

The 38-agent CLI envisioned persistent lifecycle control across specialized agents. Today, scaffolds for microagents and koshas exist, but process supervision and discovery are absent; persistence is simulated, not operational. The current system distinguishes between scaffolding (controllers and team descriptors) and working code (orchestration, validation, logging). Rasoom focuses on the missing runtime messaging layer, attaching to existing scaffolds without disrupting orchestration logic.

### Scaffolded vs. Working Components

- Scaffolded: microagents and koshas as controllers; team configurations as descriptive JSON; orchestrator routing and validation patterns.
- Working: code generation and validation flows; logging; conceptual persistence settings.
- Missing: process supervision; service discovery; health management; policy enforcement; routing to live processes; real IPC.

Rasoom introduces the minimal operational backbone (messaging, health, discovery hooks) to convert scaffolds into a working runtime fabric.

---

## Rasoom Design Goals and Constraints

Design goals:
- Preserve backward compatibility with the 38-agent system; maintain CLI operability.
- Operate with an empty MCP function list via a registry shim; support progressive discovery.
- Encode affective and unconscious signals so intent is unambiguous across tiers.
- Introduce tier-aware routing primitives with bounded latency and controlled fan-out.
- Ensure end-to-end reversibility across the seven-stage pipeline.
- Leverage Carnatic musical structures (swara, gamaka, tala) to add interpretable redundancy and emotional nuance.

Constraints:
- Minimal viable enhancement: augment orchestrator and team configurations; do not replace them.
- Binary-first payloads with RS error correction; avoid opaque semantics.
- MCP-compatible integration even when function listings are empty.
- Interpretability at intermediate stages (syllabic, musical, mathematical).

Narrative constraint: Rasoom operationalizes embodied cognition—gesture, affect, context—transforming it into computational purity (binary) while maintaining layered interpretability for debugging, governance, and human oversight.

---

## Rasoom Pipeline Specification

Rasoom’s seven-stage pipeline translates multimodal human input into a binary protocol optimized for distributed reliability. Each stage is designed for reversibility and interpretability, enabling debugging and affective preservation.

![End-to-end seven-stage Rasoom pipeline](assets/images/rasoom/pipeline.png)

### Table 2: Pipeline stage mapping

| Stage | Input | Output | Core Operation | Notes |
|-------|-------|--------|----------------|-------|
| 1. Multimodal Capture | Eye/hand/touch streams; contextual metadata | Normalized event stream | Sampling; synchronization; noise filtering | Preserves temporal ordering and multivariate correlations |
| 2. Decision Tree Conversion | Event stream | Weighted decision trees | Feature extraction; temporal coherence | Produces tier-specific granularity (Prime, Domain, Micro) |
| 3. Syllabic Mapping | Decision paths | Abugida-like syllabic units | Vowel length markers; tone indicators; tier flags | Latin base script with numeric diacritics |
| 4. Carnatic Translation | Syllables | Swara sequences with gamaka/tala | Raga constraints; octave-to-tier mapping | Adds redundancy for error resilience |
| 5. Mathematical Encoding | Swara/tala | Equations and functions | Frequency ratios; periodic functions | Prepares for numeric series |
| 6. Number Series | Equations | Prime factors; continued fractions; Gödel numbering | Lossless compression; tier addressing | Embeds routing metadata |
| 7. Binary Encoding | Number series | Binary payloads with RS | Reed–Solomon parity; interleaving; batching | Broadcast-optimized; delta compression |

### Table 3: Latency targets by scenario

| Scenario | Target Latency | Notes |
|----------|----------------|-------|
| Single-agent encode/decode | <10 ms | Includes affective encoding and error coding |
| Intra-tier broadcast | <1 ms | Local cluster; multicast-optimized |
| Cross-tier broadcast | <20 ms | Prime→Domain→Micro bounded fan-out |
| Full swarm broadcast | <100 ms | Up to ~2,500 microagents; delta compression and batching |

### Stage 1: Multimodal Input Capture

Inputs include gaze vectors with fixation durations, hand trajectories with pressure and velocity, touch interactions and dwell, on-screen navigation sequences, and contextual metadata (session history, environment state, device metrics). The capture layer normalizes sampling rates across modalities and synchronizes timestamps to maintain temporal alignment. Ambiguity indices record certainty levels for downstream routing, ensuring tentative gestures produce appropriately tentative encoded intent.

### Stage 2: Decision Tree Conversion

Event streams are converted to weighted decision trees capturing action intent (what), context (when/where), affective state (how/why), and ambiguity. Sliding windows encode temporal causality and correlation. Multi-resolution trees are produced concurrently:
- High-level trees for strategic interpretation (Prime).
- Medium-granularity trees for task decomposition (Domain).
- Atomic trees for microagent execution (Micro).

Parallel trees maintain coherence across tiers and facilitate targeted routing.

### Stage 3: Syllabic Unit Mapping

Decision paths map to syllabic units in an abugida-like structure. A Latin base script is augmented with numeric diacritics:
- Vowel length markers via subscripts/superscripts.
- Tone indicators (1–9).
- Tier flags (P/D/M) embedded as diacritics.

These diacritics enable affective nuance to shift interpretation without changing core words.

### Stage 4: Carnatic Musical Notation Translation

Syllables translate to Carnatic swara sequences (S R1 R2 G1 G2 M1 M2 P D1 D2 N1 N2 N3), with gamaka (oscillations) and tala (rhythmic cycles). Octaves map to tiers: mandra (lower) → Micro, madhya (middle) → Domain, tara (higher) → Prime. This musical layer introduces structured redundancy that improves error resilience and provides interpretable semantics for human review.

#### Table 4: Swara-to-semantics qualitative mapping

| Swara | Indicative Semantics (Qualitative) |
|-------|------------------------------------|
| S (Shadja) | Stable grounding; baseline intent confirmation |
| R1/R2 (Rishabha) | Initialization; slight escalation; uncertainty reduction |
| G1/G2 (Gandhara) | Gentle modulation; exploratory adjustment |
| M1/M2 (Madhyama) | Midpoint stabilization; balance; measured change |
| P (Panchama) | Pivot; re-centering; functional coordination |
| D1/D2 (Dhaivata) | Emphasis; increased resolve; corrective action |
| N1/N2/N3 (Nishada) | Nuance; unresolved tension; deferment or trailing context |

### Stage 5: Mathematical Equation Conversion

Swara sequences translate to equations:
- Frequency ratios as rational fractions representing intervals.
- Periodic functions modeling tala cycles.
- Wave equations encoding gamaka oscillations.

Equations facilitate compression via sparse matrix and delta encoding for broadcast efficiency.

### Stage 6: Number Series Generation

Equations convert to number series via:
- Prime factorization sequences encoding combinatorial features.
- Continued fractions for compact representation of ratios.
- Gödel-style numbering for recursive structures.

Routing metadata is embedded within the series to indicate tier targets and micro-cluster addressing, enabling efficient fan-out and aggregation.

### Stage 7: Binary Encoding

Final payloads are machine-optimal binary with RS error correction, interleaving, batching, and delta compression. Reversibility guarantees enable decode-back through the chain to reconstruct intent, affect, and context. Headers carry schema version and policy flags; payloads include affective state, decision data, syllabic units, mathematical representations, number series, and RS parity.

#### Table 5: Error-correction parameterization

| Parameter | Selection Guidance | Trade-off Considerations |
|-----------|--------------------|--------------------------|
| RS Symbol Size (m) | Align with channel word sizes (e.g., 8-bit) | Larger m improves efficiency but increases decode complexity |
| Codeword Length (n) | Based on expected burst length and message size | Longer n adds redundancy; shorter n reduces latency |
| Parity Symbols (t) | Choose t to achieve desired error-correction capability | More parity improves resilience but adds overhead |
| Interleaving Depth | Match to network burst characteristics | Higher depth combats longer bursts; adds memory/latency |
| Block Size | Calibrate to typical message length | Larger blocks improve throughput; smaller blocks reduce delay |

---

## Affective and State Encoding

Affect is carried structurally: gamaka curves encode emotional nuance; tone markers and tier flags disambiguate intent; ambiguity indices govern routing decisions. Under uncertainty, Rasoom prefers local execution and issues clarification requests; decisive affective markers (e.g., frustration or confidence) trigger oversight and corrective actions.

### Table 6: Affective state encoding and tier targeting

| Affective State | Marker System (Qualitative) | Tier Targeting Implication |
|-----------------|-----------------------------|----------------------------|
| Calm | Low gamaka amplitude; steady tala | Prefer Domain/Micro execution; minimal Prime involvement |
| Focused | Balanced gamaka; precise intervals | Domain-led with Micro atomic tasks |
| Curious | Slight oscillations; exploratory tone | Mixed routing: Domain exploration with Micro probes |
| Frustrated | Sharp gamaka; irregular emphasis | Prime oversight; Domain intervention; faster corrective actions |
| Confident | Strong pivot swara (P); resolved intervals | Prime direction with Domain coordination |
| Uncertain | Ambiguity index elevated; tentative tones | Delay cross-tier escalation; request clarification via Rasoom |

Routing decisions integrate affective thresholds to prevent message storms and unnecessary escalations.

---

## MCP Integration Plan (Empty Function List)

Rasoom integrates with MCP via a function registry shim that advertises:
- Messaging primitives: unicast, multicast, broadcast, aggregation, emergency bypass.
- Health endpoints: status, latency, error rates, subscription counts.
- Progressive discovery: functions are added as implementations mature; messaging remains functional with an empty list.

Security hooks:
- Policy checks on issuance and delivery (data sensitivity flags).
- RBAC attributes for senders and receivers.
- Governance event emission (policy violations, escalations) to audit channels.

This shim allows Rasoom to interoperate immediately with MCP-enabled tools and orchestrators, avoiding parallel protocols and enabling gradual evolution of the function catalog.[^2]

![MCP function registry shim for Rasoom messaging](assets/images/rasoom/mcp_shim.png)

The shim ensures Rasoom messages are first-class entities within MCP, aligning with empty-list scenarios while preserving a path to richer discovery.

---

## Cross-Tier Messaging Architecture (Prime/Domain/Micro)

Rasoom’s routing primitives coordinate messages across tiers while minimizing overhead and avoiding bottlenecks:
- Unicast: direct coordination.
- Multicast: cluster and swarm broadcasts.
- Broadcast: tier-wide or system-wide with bounded fan-out.
- Aggregation: micro-to-domain batch responses; domain-to-prime summaries.
- Emergency bypass: time-critical Prime→Micro directives.

Discovery, load balancing, and batching/aggregation are integral. Micro-swarm task distribution uses batching and rolling updates; domains apply backpressure; aggregation reduces chatter. Tier roles are maintained: Prime agents synthesize strategy and direct Domain clusters; Domain agents coordinate swarms; Microagents execute atomic tasks rapidly and locally isolate faults.

![Tier-aware routing and multicast topology](assets/images/rasoom/routing_topology.png)

### Table 7: Message types and tier-specific targets

| Tier Interaction | Message Pattern | Expected Latency Target | Throughput Considerations |
|------------------|-----------------|-------------------------|---------------------------|
| Prime ↔ Prime | Unicast | <1 ms | Low volume, high importance |
| Prime → Domain (cluster) | Broadcast/multicast | <5 ms | Managed fan-out; cluster-aware |
| Domain ↔ Domain | Unicast/cluster multicast | <1–5 ms | Peer coordination within cluster |
| Domain → Micro (swarm) | Multicast | <5–10 ms | Batch messages; delta compression |
| Micro → Domain | Aggregation | <5–10 ms | Batching reduces chatter |
| Prime → Micro (emergency) | Bypass multicast | <20 ms | Triggered only under time-critical conditions |

### Table 8: Scaling summary

| Metric | Target | Notes |
|--------|--------|-------|
| Active Message Paths | O(n) to O(n log n) | Hierarchical routing; caching/deduplication |
| Intra-tier Latency | <1 ms | Cluster multicast; local aggregation |
| Cross-tier Latency | <20 ms | Prime→Domain→Micro bounded fan-out |
| Full Swarm Broadcast | <100 ms | Delta compression and batching |
| Throughput | ≥100,000 messages/sec | Sustained across tiers |
| Reliability | ≥99.99% delivery | RS codes, retries, DLQ |

---

## Compatibility Layers and Backward Compatibility

Rasoom integrates with the existing 38-agent system through compatibility shims:
- CLI-to-Prime adapter: translates legacy requests into Rasoom messages.
- Tier adapters: convert between Rasoom binary payloads and microagent/kosha controllers.
- Team-config mappings: treat current descriptors as routing and capability hints without prescribing runtime behavior.

CLI tools remain accessible; team descriptors retain descriptive value; Rasoom adds operational messaging.

### Table 9: Compatibility bridges

| Component | Role | Interface |
|----------|------|-----------|
| CLI Adapter | Legacy CLI ↔ Rasoom translation | CLI request → Rasoom encode → tier targeting |
| Tier Adapter (Domain) | Rasoom ↔ controller interfaces | Binary decode → endpoint invocation → response encode |
| Tier Adapter (Micro) | Swarm multicast handling | Aggregation protocols; batch reporting |
| Team-Config Mapper | Capability profile hints | JSON descriptors → routing preferences and load hints |

---

## Security, Governance, and Antakhara Integration

Security and governance are embedded in MCP and Rasoom messaging:
- Policy checks on issuance and delivery enforce data sensitivity and role constraints.
- RBAC attributes are declared for senders and receivers; policy violations emit governance events.
- Antakhara is envisioned as the enforcement and audit anchor, consuming MCP-advertised health and policy events.

Antakhara’s precise operational role is unspecified in code; the design positions it as the interface for enforcement and audit, enabling policy evolution without mandating a specific deployment model.[^2]

### Table 10: Security control matrix

| Policy Type | Enforcement Point | MCP/Rasoom Integration |
|-------------|-------------------|------------------------|
| Data Sensitivity | Issuance and delivery | MCP function attributes; Rasoom payload flags |
| Role-Based Access | Sender/receiver | MCP RBAC declarations; policy checks on route |
| Audit Logging | All tiers | Health and audit endpoints; governance events |
| Escalation Rules | Prime/Domain | Rasoom ambiguity thresholds and bypass policies |

---

## Observability and Telemetry

Rasoom introduces first-class observability:
- Health endpoints expose status, latency, error rates, subscription counts.
- Metrics and logs aggregate at domain and prime tiers.
- End-to-end tracing spans capture, decision trees, syllabic units, swara/math/number series, binary payloads, and routing.

SLIs/SLOs are defined for messaging and orchestration. Instrumentation begins in Phase 1 and expands in Phase 2.

### Table 11: Telemetry KPIs

| KPI | Description | Target |
|-----|-------------|--------|
| Message Latency | End-to-end delivery time per tier | Meets targets in Table 7 |
| Delivery Reliability | Percent delivered successfully | ≥99.99% with retries and DLQ |
| Error Rate | Decode errors and policy violations | ≤0.01% after RS correction |
| Subscription Count | Active subscribers per multicast channel | Bounded to avoid overload |
| Retry/Backoff Events | Count per tier under rate limits | Controlled and trending down |
| Escalation Rate | Prime involvement per 1,000 messages | Stable within configured bands |

---

## Implementation Roadmap

The roadmap proceeds from scaffolding to production through three phases.

![Phased roadmap: Stabilize, Integrate, Harden](assets/images/rasoom/roadmap.png)

### Table 12: Roadmap phases and success criteria

| Phase | Milestones | Deliverables | Success Criteria |
|-------|------------|--------------|------------------|
| Phase 1 (Stabilize) | Replace simulation with real process supervision; health endpoints; baseline observability; end-to-end integration tests | Agent lifecycle service; health endpoints; log aggregation; test suite | Agents run as processes; health visible; integration tests pass |
| Phase 2 (Integrate) | Service discovery and scheduling; CI/CD; active security enforcement; benchmarking and SLAs/SLOs | Discovery service; scheduler; CI/CD; policy engine; performance reports | Dynamic scheduling; CI/CD stable; security enforced; SLA compliance |
| Phase 3 (Harden) | Formal governance and audit; Triumvirate interfaces; scale and reliability improvements | Policy engine; audit trails; Agenta/Pranava/Antakhara interfaces | Governance operational; audit-ready; reliability targets met |

Phase sequencing aligns with provider constraints and backoff behavior for rate-limit handling.[^1]

---

## Validation and Testing Strategy

Validation spans:
- Unit tests for stage-specific encode/decode and RS correctness.
- Integration tests for tier adapters, CLI-to-Prime, and MCP shim.
- Load tests for sustained throughput ≥100k messages/sec.
- Stress tests for fan-out bursts and failure scenarios.
- Fuzz tests for multimodal inputs and malformed messages.

Round-trip reversibility and affective preservation are validated across the pipeline; latency SLOs are tested under负载.

### Table 13: Test coverage matrix

| Test Category | Scope | Pass/Fail Criteria |
|---------------|-------|--------------------|
| Unit | Stage-specific encode/decode; RS decoding correctness | 100% stage-level reversibility; RS error correction within parameters |
| Integration | Tier adapters; CLI-to-Prime; MCP shim | End-to-end round-trip without semantic loss; latency within targets |
| Load | Sustained messaging throughput | ≥100k messages/sec sustained; latency within targets |
| Stress | Fan-out bursts; failure scenarios | Graceful degradation; bounded retries/backoff; DLQ handling |
| Fuzz | Multimodal inputs; malformed messages | No crashes; coherent error responses; policy violations logged |

---

## Performance and Scalability Modeling

Rasoom scales across ~2,700 agents with hierarchical routing and caching to minimize message paths and avoid bottlenecks. Error-correction overhead is balanced against reliability targets through parameter tuning for symbol size, parity, interleaving, and block length. Batching and delta compression minimize broadcast overhead to micro-swarms.

### Table 14: Error-correction trade-offs

| ECC Parameter | Impact on Reliability | Impact on Overhead |
|---------------|-----------------------|--------------------|
| Increased Parity (t) | Higher resilience to burst errors | Larger message size; higher CPU cost |
| Larger Symbol Size (m) | Better efficiency | Potential decode complexity increase |
| Higher Interleaving | Better burst handling | Added latency and memory |
| Optimized Block Size | Balanced throughput and delay | Tuning required per workload |

---

## Risk Register and Mitigations

### Table 15: Risk register

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| Simulation-to-reality migration complexity | High | High | Phase 1 focus on health and supervision; incremental wiring | Platform Engineering |
| Scheduling and discovery under high fan-out | Medium | High | Hierarchical routing; caching; bounded multicast | Platform Engineering |
| Security policy false positives | Medium | Medium | Tuning and audit; staged enforcement | Security Engineering |
| Observability blind spots | Medium | High | Instrument from Phase 1; KPI gates | SRE/DevOps |
| CLI compatibility regressions | Low | Medium | Adapter tests; backward compatibility suite | Architecture/Platform |
| ECC overhead misconfiguration | Medium | Medium | Parameter tuning; benchmarks | SRE/DevOps |

Mitigations are embedded in each phase’s milestones and success criteria, ensuring progressive risk reduction.

---

## Appendices

### Appendix A: Schema Outlines for Key Rasoom Payloads

Rasoom payloads include metadata and affective fields at each stage to ensure reversibility and interpretability.

### Table 16: Schema field definitions

| Layer | Schema Fields (Illustrative) | Notes |
|-------|------------------------------|-------|
| Multimodal Capture | timestamp; modality; normalized_value; ambiguity_index | Synchronized across modalities |
| Decision Trees | node_id; weight; intent_label; context_frame; affect_marker; tier_target | Multi-resolution outputs |
| Syllabic Units | base_syllable; vowel_length; tone; tier_flag; affect_encoding | Abugida-like structure |
| Swara Sequence | swara_list; gamaka_profile; tala_cycle; octave_tier_map | Musical redundancy |
| Equations | ratio_list; periodic_functions; wave_params; compression_hints | Sparse/delta encoding |
| Number Series | prime_factors; continued_fractions; godel_code; routing_metadata | Tier addressing embedded |
| Binary Payload | payload_bits; rs_parity; interleaving_depth; block_id; header | Header carries schema version and policy flags |

### Appendix B: Worked Example (Non-Proprietary)

Input: gentle hand gesture with elevated curiosity and mild uncertainty.

- Stage 1–2: Capture and Decision Trees
  - Slow trajectory; low pressure; moderate fixation shifts; tentative touch.
  - Trees: “explore option A” (high), “probe subset A1” (medium), “inspect item X” (atomic); ambiguity index elevated; affect marker indicates curiosity.

- Stage 3: Syllabic Mapping
  - Tone=3; vowel length=2; tier_flag=D; affective encoding preserved via tone/gamaka.

- Stage 4: Carnatic Translation
  - G1/G2 emphasis with mild gamaka; regular but slightly extended tala; octave→Domain mapping.

- Stage 5–6: Equations and Number Series
  - Frequency ratios for gentle modulation; periodic functions for extended tala; number series embed routing to Domain cluster “D-07.”

- Stage 7: Binary with RS
  - Payload includes RS parity and interleaving; header includes tier target and ambiguity threshold.

Routing: Prime→Domain broadcast (<5 ms) to D-07; Domain→Micro multicast (<5–10 ms) to swarm subset; micro aggregation returns findings; Rasoom preserves curiosity markers and ambiguity thresholds.

Decoding: Binary → number series → equations → swara → syllabic → decision trees → multimodal reconstituted event stream. Interpretability maintained; affective nuance intact.

### Appendix C: Integration Artifacts for MCP (Conceptual)

- mcp_function_list.json entries:
  - rasoom.message.send: {tier, target_id(s), payload, affective_flags, policy_tags}
  - rasoom.message.subscribe: {topic, tier, filters}
  - rasoom.health.report: {agent_id, status, latency, error_rate, subscription_count}
  - rasoom.policy.check: {sender, receiver, payload_policy_flags, enforce}
- Discovery updates:
  - Progressive function additions; shim maintains messaging even if list remains empty.

---

## Information Gaps and Assumptions

The codebase lacks canonical definitions and code artifacts for:
- Agenta as a tiered hierarchy with explicit runtime interfaces.
- Pranava as an explicit orchestration signal/routing module.
- Antakhara as an enforceable security and governance layer.

Additional gaps include:
- Production-grade telemetry beyond logs (metrics, traces, SLAs/SLOs).
- Service discovery, load balancing, and scheduling for microagents and koshas.
- Process supervision evidence for microagent scale (persistent agent manager simulates lifecycle).
- Explicit data flow/API contracts between microagents, koshas, orchestrator, and team configurations.
- MCP function listings beyond an empty protocol file.

Assumptions:
- Health endpoints can be introduced without breaking existing controllers.
- MCP function discovery can evolve gradually; the shim ensures messaging works.
- Antakhara will be implemented as an enforcement and audit layer consuming MCP-advertised events.

Where evidence is absent, the design opts for adaptable interfaces and staged integration.

---

## References

[^1]: Groq OpenAI-Compatible Chat Completions API. https://api.groq.com/openai/v1/chat/completions  
[^2]: Perplexity AI R2 CDN Asset: Perplexity Full Logo (Primary Dark). https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png
