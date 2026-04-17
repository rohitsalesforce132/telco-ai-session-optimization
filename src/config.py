"""Configuration management for Telco AI Session Optimization."""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings."""

    # Anthropic API
    anthropic_api_key: str

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "session-events"
    kafka_consumer_group: str = "session-optimization"

    # Temporal
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "session-optimization"

    # Databases
    timescaledb_uri: str = "postgresql://user:password@localhost:5432/sessions"
    redis_url: str = "redis://localhost:6379"
    postgres_uri: str = "postgresql://user:password@localhost:5432/metadata"

    # APIs
    qod_api_url: str
    qod_api_key: str
    nefg_api_url: str
    nefg_api_key: str
    session_api_url: str
    session_api_key: str

    # Kubernetes
    gpu_pool_name: str = "shared-gpu-pool"
    gpu_memory_per_pod: int = 8192
    max_concurrent_sessions: int = 10000

    # Swarm
    total_agents: int = 20
    qod_agents: int = 5
    nefg_agents: int = 5
    session_agents: int = 5
    optimize_agents: int = 5

    # Optimization
    optimization_interval_seconds: int = 60
    prediction_horizon_minutes: int = 30

    # Observability
    jaeger_host: str = "jaeger"
    jaeger_port: int = 6831
    prometheus_port: int = 9090

    # Application
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30

    # Rate limiting
    rate_limit_per_minute: int = 1000
    rate_limit_burst: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
