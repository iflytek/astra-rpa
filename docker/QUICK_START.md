# AstronRPA Quick Start Guide

## 🚀 Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start all services:**
   ```bash
   docker compose up -d
   ```

3. **Access services:**
   - AI Service: http://localhost:8010
   - OpenAPI Service: http://localhost:8020
   - Resource Service: http://localhost:8030
   - Robot Service: http://localhost:8040
   - MinIO Console: http://localhost:9001

## 🛑 Stop Services

```bash
docker compose stop
```

## 📋 Service Details

| Service | Port | Description |
|---------|------|-------------|
| ai-service | 8010 | Python FastAPI AI service |
| openapi-service | 8020 | Python FastAPI OpenAPI service |
| resource-service | 8030 | Java Spring Boot resource service |
| robot-service | 8040 | Java Spring Boot robot service |
| mysql | 3306 | MySQL 8.4.6 database |
| redis | 6379 | Redis 8.0 cache |
| minio | 9000/9001 | MinIO object storage |

## 🔧 Common Commands

```bash
# View logs
docker compose logs -f [service-name]

# Restart a service
docker compose restart [service-name]

# Rebuild and start
docker compose up --build -d

# Stop and remove volumes
docker compose down -v

# Check service status
docker compose ps
```

## 🐛 Troubleshooting

1. **Port conflicts:** Change ports in `.env` file
2. **Permission issues:** Ensure Docker has proper permissions
3. **Service won't start:** Check logs with `docker compose logs [service-name]`
4. **Database issues:** Wait for MySQL to be healthy before starting other services
