# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints require an API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Create Session

Create a new session with QoS requirements.

**Endpoint:** `POST /api/session/create`

**Request:**
```json
{
  "session_id": "sess-001",
  "user_id": "user123",
  "service_type": "video_streaming",
  "qos_requirements": {
    "bandwidth_mbps": 10,
    "latency_ms": 50,
    "jitter_ms": 10,
    "packet_loss_percent": 0.1
  },
  "priority": "high"
}
```

**Response:** `201 Created`
```json
{
  "session_id": "sess-001",
  "status": "created",
  "qos_allocated": {
    "bandwidth_mbps": 10,
    "latency_ms": 50,
    "jitter_ms": 10,
    "packet_loss_percent": 0.1
  },
  "network_exposed": true,
  "created_at": "2026-04-17T10:00:00Z"
}
```

### 2. Get Session Status

Get the status of an existing session.

**Endpoint:** `GET /api/session/{session_id}`

**Response:** `200 OK`
```json
{
  "session_id": "sess-001",
  "status": "active",
  "service_type": "video_streaming",
  "qos_allocated": {
    "bandwidth_mbps": 10,
    "latency_ms": 48,
    "jitter_ms": 9,
    "packet_loss_percent": 0.08
  },
  "current_metrics": {
    "bandwidth_mbps": 9.5,
    "latency_ms": 48,
    "jitter_ms": 8,
    "packet_loss_percent": 0.07
  },
  "created_at": "2026-04-17T10:00:00Z",
  "updated_at": "2026-04-17T10:05:00Z"
}
```

### 3. Optimize QoS

Optimize QoS allocation for multiple sessions.

**Endpoint:** `POST /api/optimize/qos`

**Request:**
```json
{
  "session_ids": ["sess-001", "sess-002", "sess-003"],
  "optimization_goal": "minimize_latency"
}
```

**Response:** `200 OK`
```json
{
  "optimization_id": "opt-001",
  "sessions_optimized": 3,
  "improvements": {
    "average_latency_ms": 52,
    "previous_latency_ms": 80,
    "improvement_percent": 35
  },
  "qos_allocations": [
    {
      "session_id": "sess-001",
      "bandwidth_mbps": 12,
      "latency_ms": 45
    },
    {
      "session_id": "sess-002",
      "bandwidth_mbps": 8,
      "latency_ms": 55
    },
    {
      "session_id": "sess-003",
      "bandwidth_mbps": 10,
      "latency_ms": 56
    }
  ],
  "optimized_at": "2026-04-17T10:10:00Z"
}
```

### 4. Get Swarm Status

Get the status of the swarm (all agents).

**Endpoint:** `GET /api/swarm/status`

**Response:** `200 OK`
```json
{
  "swarm_id": "swarm-001",
  "total_agents": 20,
  "active_agents": 20,
  "agent_status": {
    "qod_agents": {
      "active": 5,
      "total": 5,
      "details": [
        {"agent_id": "qod-1", "status": "active", "tasks_processing": 2},
        {"agent_id": "qod-2", "status": "active", "tasks_processing": 1},
        {"agent_id": "qod-3", "status": "active", "tasks_processing": 3},
        {"agent_id": "qod-4", "status": "active", "tasks_processing": 2},
        {"agent_id": "qod-5", "status": "active", "tasks_processing": 1}
      ]
    },
    "nefg_agents": {
      "active": 5,
      "total": 5,
      "details": [...]
    },
    "session_agents": {
      "active": 5,
      "total": 5,
      "details": [...]
    },
    "optimize_agents": {
      "active": 5,
      "total": 5,
      "details": [...]
    }
  },
  "task_board": {
    "total_tasks": 150,
    "pending_tasks": 10,
    "in_progress_tasks": 140
  },
  "timestamp": "2026-04-17T10:15:00Z"
}
```

### 5. Get Metrics

Get system metrics (latency, throughput, cost).

**Endpoint:** `GET /api/metrics`

**Response:** `200 OK`
```json
{
  "latency": {
    "p50_ms": 32,
    "p95_ms": 48,
    "p99_ms": 72
  },
  "throughput": {
    "sessions_per_second": 12000,
    "events_per_second": 15000
  },
  "cost": {
    "cost_per_session_usd": 0.004,
    "hourly_cost_usd": 144.0,
    "daily_cost_usd": 3456.0
  },
  "gpu": {
    "utilization_percent": 85,
    "shared_pods": 12,
    "total_pods": 15
  },
  "uptime": {
    "uptime_percent": 99.99,
    "last_downtime": null
  },
  "timestamp": "2026-04-17T10:20:00Z"
}
```

### 6. Terminate Session

Terminate an existing session.

**Endpoint:** `DELETE /api/session/{session_id}`

**Response:** `200 OK`
```json
{
  "session_id": "sess-001",
  "status": "terminated",
  "resources_freed": {
    "bandwidth_mbps": 10,
    "gpu_memory_mb": 512
  },
  "terminated_at": "2026-04-17T10:30:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., session already exists) |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Rate Limiting

- **Default limit:** 1000 requests per minute per API key
- **Burst limit:** 100 requests per second
- **Rate limit headers:**
  - `X-RateLimit-Limit`: 1000
  - `X-RateLimit-Remaining`: 999
  - `X-RateLimit-Reset`: 1713343200

## Webhooks

### Session Status Webhook

Receive real-time updates when session status changes.

**Endpoint:** `POST /api/webhooks/session-status`

**Payload:**
```json
{
  "event": "session.status_changed",
  "session_id": "sess-001",
  "previous_status": "created",
  "new_status": "active",
  "timestamp": "2026-04-17T10:00:05Z"
}
```

### QoS Optimization Webhook

Receive notifications when QoS is optimized.

**Endpoint:** `POST /api/webhooks/qos-optimized`

**Payload:**
```json
{
  "event": "qos.optimized",
  "optimization_id": "opt-001",
  "sessions_affected": ["sess-001", "sess-002"],
  "improvement_percent": 35,
  "timestamp": "2026-04-17T10:10:00Z"
}
```
