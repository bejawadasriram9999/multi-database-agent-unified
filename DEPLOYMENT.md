# Deployment Guide

This guide covers deployment options for the Multi-Database Agent in different environments.

## 🚀 Quick Start

### Local Development

1. **Setup Environment**:
   ```bash
   # Run the setup script
   ./scripts/setup.sh
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Test connections
   python scripts/test_connections.py
   ```

2. **Start Services**:
   ```bash
   # Start API server
   python api_server.py
   
   # Start web UI (in another terminal)
   streamlit run chat_ui.py
   
   # Or use Google ADK
   adk web
   ```

### Docker Deployment

1. **Build and Run**:
   ```bash
   # Build the image
   docker build -t multi-database-agent .
   
   # Run with environment variables
   docker run -p 8000:8000 -p 8501:8501 \
     -e MDB_MCP_CONNECTION_STRING="your_mongodb_connection" \
     -e ORACLE_MCP_CONNECTION_STRING="your_oracle_connection" \
     -e GOOGLE_API_KEY="your_google_api_key" \
     multi-database-agent
   ```

2. **Docker Compose**:
   ```bash
   # Development with local databases
   docker-compose --profile development up
   
   # Production with reverse proxy
   docker-compose --profile production up
   ```

## 🏭 Production Deployment

### Environment Variables

Create a production `.env` file:

```env
# Production Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG_MODE=FALSE

# Database Connections
MDB_MCP_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/db
ORACLE_MCP_CONNECTION_STRING=user/pass@host:1521/service

# Google ADK
GOOGLE_API_KEY=your_production_api_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Security
ENABLE_AUTHENTICATION=TRUE
API_KEY_REQUIRED=TRUE
API_KEY=your_secure_api_key

# Performance
MAX_QUERY_RESULTS=1000
QUERY_TIMEOUT=60
CORS_ORIGINS=https://yourdomain.com
```

### Docker Compose Production

```yaml
version: '3.8'
services:
  multi-db-agent:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      - MDB_MCP_CONNECTION_STRING=${MDB_MCP_CONNECTION_STRING}
      - ORACLE_MCP_CONNECTION_STRING=${ORACLE_MCP_CONNECTION_STRING}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ENABLE_AUTHENTICATION=TRUE
      - API_KEY=${API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - multi-db-agent
    restart: unless-stopped
```

### Kubernetes Deployment

1. **Create Namespace**:
   ```bash
   kubectl create namespace multi-db-agent
   ```

2. **Create ConfigMap**:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: multi-db-agent-config
     namespace: multi-db-agent
   data:
     LOG_LEVEL: "INFO"
     MAX_QUERY_RESULTS: "1000"
     QUERY_TIMEOUT: "60"
   ```

3. **Create Secret**:
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: multi-db-agent-secrets
     namespace: multi-db-agent
   type: Opaque
   data:
     MDB_MCP_CONNECTION_STRING: <base64-encoded-connection-string>
     ORACLE_MCP_CONNECTION_STRING: <base64-encoded-connection-string>
     GOOGLE_API_KEY: <base64-encoded-api-key>
   ```

4. **Deploy Application**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: multi-db-agent
     namespace: multi-db-agent
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: multi-db-agent
     template:
       metadata:
         labels:
           app: multi-db-agent
       spec:
         containers:
         - name: multi-db-agent
           image: multi-database-agent:latest
           ports:
           - containerPort: 8000
           - containerPort: 8501
           envFrom:
           - configMapRef:
               name: multi-db-agent-config
           - secretRef:
               name: multi-db-agent-secrets
           resources:
             requests:
               memory: "512Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

## 🔧 Configuration

### Database Connection Strings

#### MongoDB
```env
# Atlas
MDB_MCP_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database

# Local
MDB_MCP_CONNECTION_STRING=mongodb://localhost:27017/database

# With options
MDB_MCP_CONNECTION_STRING=mongodb://user:pass@host:27017/db?authSource=admin&ssl=true
```

#### Oracle
```env
# Basic
ORACLE_MCP_CONNECTION_STRING=user/password@host:port/service_name

# With TNS
ORACLE_MCP_CONNECTION_STRING=user/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=service)))

# With wallet
ORACLE_MCP_CONNECTION_STRING=user/password@host:port/service_name?wallet_location=/path/to/wallet
```

### Security Configuration

#### API Authentication
```env
ENABLE_AUTHENTICATION=TRUE
API_KEY_REQUIRED=TRUE
API_KEY=your-secure-api-key-here
```

#### CORS Configuration
```env
# Single origin
CORS_ORIGINS=https://yourdomain.com

# Multiple origins
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# All origins (development only)
CORS_ORIGINS=*
```

## 📊 Monitoring

### Health Checks

- **API Health**: `GET /health`
- **Database Status**: Monitored through health endpoint
- **Agent Status**: Available through API

### Logging

- **Structured Logs**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic rotation with configurable size

### Metrics

Monitor these key metrics:
- Query response times
- Database connection status
- Error rates
- Memory and CPU usage
- Active connections

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **Network Security**: Use VPN or private networks for database connections
3. **API Keys**: Rotate API keys regularly
4. **Access Control**: Implement proper authentication and authorization
5. **Audit Logging**: Enable comprehensive audit logging
6. **Input Validation**: Validate all user inputs
7. **Rate Limiting**: Implement rate limiting to prevent abuse

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failures**:
   - Check connection strings
   - Verify network connectivity
   - Check firewall rules
   - Validate credentials

2. **MCP Server Issues**:
   - Ensure Node.js is installed
   - Check Oracle Instant Client installation
   - Verify environment variables

3. **API Authentication Issues**:
   - Check API key configuration
   - Verify CORS settings
   - Check request headers

### Debug Mode

Enable debug mode for troubleshooting:
```env
DEBUG_MODE=TRUE
LOG_LEVEL=DEBUG
```

### Log Analysis

```bash
# View logs
docker logs multi-database-agent

# Follow logs
docker logs -f multi-database-agent

# Filter error logs
docker logs multi-database-agent 2>&1 | grep ERROR
```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Deploy multiple API server instances
3. **Database Connection Pooling**: Configure connection pooling
4. **Caching**: Implement Redis for query result caching

### Performance Optimization

1. **Database Indexes**: Ensure proper indexing
2. **Query Optimization**: Monitor and optimize slow queries
3. **Resource Limits**: Set appropriate CPU and memory limits
4. **Connection Pooling**: Configure database connection pools

## 🔄 Updates and Maintenance

### Rolling Updates

```bash
# Update Docker image
docker pull multi-database-agent:latest

# Rolling update with Docker Compose
docker-compose up -d --no-deps multi-db-agent

# Kubernetes rolling update
kubectl set image deployment/multi-db-agent multi-db-agent=multi-database-agent:latest
```

### Backup and Recovery

1. **Configuration Backup**: Backup environment files and secrets
2. **Database Backup**: Regular database backups
3. **Log Backup**: Archive logs for compliance
4. **Disaster Recovery**: Test recovery procedures regularly
