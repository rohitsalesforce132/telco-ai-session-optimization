# Architecture: Telco AI Session Optimization

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Ingestion Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Kafka       │  │ Pulsar      │  │ Redis       │              │
│  │ Consumer    │  │ Consumer    │  │ Dedup       │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  Exactly-once semantics, 10K+ events/sec, <5s latency           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Swarm Coordination                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ QOD      │  │ NEFG     │  │ Session  │  │ Optimize │       │
│  │ Agents   │  │ Agents   │  │ Agents   │  │ Agents   │       │
│  │ (5)      │  │ (5)      │  │ (5)      │  │ (5)      │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  A2A Protocol: Direct peer-to-peer, no central bottleneck        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Planning & Reasoning                          │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ OODA Loop       │  │ Tree-of-Thoughts │                      │
│  │ Observe         │  │ Explore paths   │                      │
│  │ Orient          │  │ Prune invalid   │                      │
│  │ Decide          │  │ Select best     │                      │
│  │ Act             │  │ Execute         │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Execution Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Temporal    │  │ Kubernetes  │  │ Cloud Run  │              │
│  │ Workflows   │  │ GPU Pool    │  │ Serverless │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Ingestion Flow

```
Session Event → Kafka → Consumer → Dedup (Redis) → Normalize → Submit to Swarm
```

### Swarm Coordination

```
Agent A → A2A Message → Agent B
          ↓
      Direct Channel (asyncio.Queue)
          ↓
      Task Board (Shared State)
          ↓
      Conflict Detection
```

### OODA Loop Flow

```
Observe (metrics) → Orient (update model) → Decide (action) → Act (execute) → Repeat
```

### Tree-of-Thoughts Flow

```
Problem → Branch 1 → Branch 2 → Branch 3
          ↓           ↓           ↓
      Explore    Explore    Explore
          ↓           ↓           ↓
      Evaluate   Evaluate   Evaluate
          ↓           ↓           ↓
      Select Best Path → Execute
```

## Data Flow

### Session Creation

```
User Request → API → Create Session → QOD Agent → Allocate QoS → NEFG Agent → Expose Network
                                                    ↓
                                          Session Agent → Start Session
```

### QoS Optimization

```
Metrics Stream → Ingestion → Swarm → Optimize Agent → Predict Demand → Allocate Resources
                                                            ↓
                                                      QOD Agent → Update QoS
```

### Session Termination

```
User Request → API → Terminate Session → Session Agent → Stop Session → Optimize Agent → Free Resources
```
