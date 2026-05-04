# Deployment Guide

## Prerequisites

- Kubernetes 1.28+ with GPU support
- Docker 20.10+
- kubectl configured
- Helm 3.x (optional)
- TimescaleDB 2.x
- Redis 7+
- Kafka 3.x or Pulsar 2.x
- Temporal Server

## Local Development

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Included

- Kafka (message broker)
- Temporal (workflow orchestration)
- TimescaleDB (time-series database)
- Redis (cache/dedup)
- Jaeger (tracing)
- Prometheus (metrics)
- Grafana (visualization)

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace telco-ai
```

### 2. Deploy Dependencies

```bash
# Deploy Kafka
kubectl apply -f kubernetes/kafka/

# Deploy TimescaleDB
kubectl apply -f kubernetes/timescaledb/

# Deploy Redis
kubectl apply -f kubernetes/redis/

# Deploy Temporal
kubectl apply -f kubernetes/temporal/
```

### 3. Deploy Application

```bash
# Create secrets
kubectl create secret generic api-secrets \
  --from-literal=anthropic-api-key=YOUR_KEY \
  --namespace=telco-ai

# Deploy main application
kubectl apply -f kubernetes/deployment.yaml

# Deploy service
kubectl apply -f kubernetes/service.yaml

# Deploy HPA
kubectl apply -f kubernetes/hpa.yaml
```

### 4. Configure GPU Pool

```bash
# Deploy GPU pool configuration
kubectl apply -f kubernetes/gpu-pool.yaml
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

### Kubernetes Secrets

```bash
# Create secret for API keys
kubectl create secret generic api-secrets \
  --from-literal=anthropic-api-key=YOUR_KEY \
  --from-literal=qod-api-key=YOUR_KEY \
  --from-literal=nefg-api-key=YOUR_KEY \
  --namespace=telco-ai

# Create secret for database credentials
kubectl create secret generic db-secrets \
  --from-literal=timescaledb-uri=postgresql://user:pass@host/db \
  --from-literal=redis-url=redis://host:6379 \
  --namespace=telco-ai
```

## Scaling

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: telco-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: telco-ai-session-optimization
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### GPU Autoscaling with KEDA

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: telco-ai-gpu-scaler
spec:
  scaleTargetRef:
    name: telco-ai-gpu-worker
  minReplicaCount: 2
  maxReplicaCount: 10
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: session-optimization
      topic: session-events
      lagThreshold: '1000'
```

## Monitoring

### Prometheus Metrics

```bash
# Access Prometheus
kubectl port-forward -n telco-ai svc/prometheus 9090:9090

# Access Grafana
kubectl port-forward -n telco-ai svc/grafana 3000:3000
```

### Jaeger Tracing

```bash
# Access Jaeger
kubectl port-forward -n telco-ai svc/jaeger 16686:16686
```

## Rolling Updates

```bash
# Update deployment
kubectl set image deployment/telco-ai-session-optimization \
  telco-ai=telco-ai-session-optimization:v1.2.0 \
  -n telco-ai

# Check rollout status
kubectl rollout status deployment/telco-ai-session-optimization -n telco-ai

# Rollback if needed
kubectl rollout undo deployment/telco-ai-session-optimization -n telco-ai
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n telco-ai
kubectl describe pod <pod-name> -n telco-ai
kubectl logs <pod-name> -n telco-ai
```

### Check Service Connectivity

```bash
# Port forward to service
kubectl port-forward -n telco-ai svc/telco-ai-session-optimization 8000:80

# Test API
curl http://localhost:8000/api/swarm/status
```

### Check GPU Allocation

```bash
# Get GPU resources
kubectl describe node | grep -A 5 "nvidia.com/gpu"

# Check GPU usage
kubectl top node
```

### Check Kafka Lag

```bash
# Get consumer lag
kubectl exec -n telco-ai deployment/kafka -- \
  kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group session-optimization --describe
```

## Backup and Recovery

### TimescaleDB Backup

```bash
# Backup
kubectl exec -n telco-ai deployment/timescaledb -- \
  pg_dump -U postgres sessions > backup.sql

# Restore
kubectl exec -i -n telco-ai deployment/timescaledb -- \
  psql -U postgres sessions < backup.sql
```

### Redis Backup

```bash
# Backup
kubectl exec -n telco-ai deployment/redis -- \
  redis-cli SAVE

# Copy RDB file
kubectl cp telco-ai/redis-pod:/data/dump.rdb ./dump.rdb
```

## Security

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: telco-ai-network-policy
  namespace: telco-ai
spec:
  podSelector:
    matchLabels:
      app: telco-ai-session-optimization
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: telco-ai
    ports:
    - protocol: TCP
      port: 9092  # Kafka
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 5432  # TimescaleDB
```

### RBAC

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: telco-ai
  namespace: telco-ai
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: telco-ai-role
  namespace: telco-ai
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: telco-ai-rolebinding
  namespace: telco-ai
subjects:
- kind: ServiceAccount
  name: telco-ai
  namespace: telco-ai
roleRef:
  kind: Role
  name: telco-ai-role
  apiGroup: rbac.authorization.k8s.io
```
