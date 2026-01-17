"""
AgentX 5.0 Container Configuration
Docker and Kubernetes setup for AgentX 5.0 deployment
"""
import logging
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentX5Container:
    """AgentX 5.0 container configuration and management"""
    
    def __init__(self):
        self.config = {}
        self.containers = []
        
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for AgentX 5.0"""
        dockerfile = """# AgentX 5.0 Container Configuration
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AGENTX_VERSION=5.0
ENV AGENTX_MODE=production

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional AgentX dependencies
RUN pip install --no-cache-dir \\
    fastapi>=0.100.0 \\
    uvicorn>=0.23.0 \\
    pydantic>=2.0.0 \\
    redis>=5.0.0 \\
    celery>=5.3.0 \\
    kafka-python>=2.0.2

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache

# Expose ports
EXPOSE 8000 8001 6379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run system execution script
CMD ["python", "scripts/execute_all_systems.py"]
"""
        return dockerfile
    
    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for AgentX 5.0 stack"""
        compose = """version: '3.8'

services:
  agentx5:
    build: .
    container_name: agentx5-master
    restart: unless-stopped
    environment:
      - AGENTX_MODE=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/agentx
    ports:
      - "8000:8000"
      - "8001:8001"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    networks:
      - agentx-network

  redis:
    image: redis:7-alpine
    container_name: agentx5-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - agentx-network

  postgres:
    image: postgres:15-alpine
    container_name: agentx5-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=agentx
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - agentx-network

  celery-worker:
    build: .
    container_name: agentx5-worker
    restart: unless-stopped
    command: celery -A core_systems.agentx5_master_750 worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - agentx5
    networks:
      - agentx-network

  celery-beat:
    build: .
    container_name: agentx5-scheduler
    restart: unless-stopped
    command: celery -A core_systems.agentx5_master_750 beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - agentx5
    networks:
      - agentx-network

  nginx:
    image: nginx:alpine
    container_name: agentx5-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - agentx5
    networks:
      - agentx-network

volumes:
  redis-data:
  postgres-data:

networks:
  agentx-network:
    driver: bridge
"""
        return compose
    
    def generate_kubernetes_deployment(self) -> str:
        """Generate Kubernetes deployment manifest"""
        k8s_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentx5-deployment
  labels:
    app: agentx5
    version: "5.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentx5
  template:
    metadata:
      labels:
        app: agentx5
        version: "5.0"
    spec:
      containers:
      - name: agentx5
        image: agentx5:5.0
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 8001
          name: metrics
        env:
        - name: AGENTX_MODE
          value: "production"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: agentx5-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: agentx5-service
spec:
  selector:
    app: agentx5
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  - protocol: TCP
    port: 8001
    targetPort: 8001
    name: metrics
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agentx5-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agentx5-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
"""
        return k8s_yaml
    
    def save_configs(self, output_dir: str = "."):
        """Save all configuration files"""
        output_path = Path(output_dir).resolve()
        
        # Ensure we're not writing outside intended directory
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        configs = {
            'Dockerfile': self.generate_dockerfile(),
            'docker-compose.yml': self.generate_docker_compose(),
            'k8s-deployment.yaml': self.generate_kubernetes_deployment()
        }
        
        for filename, content in configs.items():
            file_path = output_path / filename
            # Validate file path is within output directory
            if not str(file_path.resolve()).startswith(str(output_path)):
                logger.error(f"Invalid file path: {filename}")
                continue
            
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Generated {filename}")
        
        return configs
    
    def generate_report(self, output_file: str = "agentx5_container_report.json") -> Dict:
        """Generate container setup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'agentx_version': '5.0',
            'container_platform': 'Docker/Kubernetes',
            'components': [
                'AgentX 5.0 Master',
                'Redis Cache',
                'PostgreSQL Database',
                'Celery Workers',
                'Celery Beat Scheduler',
                'Nginx Reverse Proxy'
            ],
            'scaling': {
                'min_replicas': 3,
                'max_replicas': 10,
                'auto_scaling': True
            },
            'monitoring': {
                'health_checks': True,
                'metrics_endpoint': ':8001/metrics',
                'logging': 'enabled'
            }
        }
        
        # Validate output file path
        output_path = Path(output_file).resolve()
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


def main():
    """Setup AgentX 5.0 container configuration"""
    container = AgentX5Container()
    
    # Generate and save configs
    configs = container.save_configs()
    
    # Generate report
    report = container.generate_report()
    
    print(f"\n{'='*60}")
    print("AGENTX 5.0 CONTAINER SETUP REPORT")
    print(f"{'='*60}")
    print(f"Version: {report['agentx_version']}")
    print(f"Platform: {report['container_platform']}")
    print(f"\nComponents:")
    for comp in report['components']:
        print(f"  • {comp}")
    print(f"\nScaling: {report['scaling']['min_replicas']}-{report['scaling']['max_replicas']} replicas")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
