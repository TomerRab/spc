# {{ repo_name }} Delivery Repository

This repository contains the Helm charts and deployment configurations for {{ repo_name }} microservice across different environments (dev, staging, production).

## Repository Structure

```
.
├── helm/                           # Helm chart for the application
│   ├── Chart.yaml                 # Chart metadata
│   ├── values.yaml                # Default values
│   ├── values-dev.yaml           # Development overrides
│   ├── values-staging.yaml       # Staging overrides
│   ├── values-prod.yaml          # Production overrides
│   └── templates/                # Kubernetes templates
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── configmap.yaml
│       ├── serviceaccount.yaml
│       ├── hpa.yaml
│       └── _helpers.tpl
├── environments/                  # Environment-specific configurations
│   ├── dev/
│   │   ├── values.yaml           # Development environment values
│   │   └── secrets.yaml          # Development secrets (encrypted)
│   ├── staging/
│   │   ├── values.yaml           # Staging environment values
│   │   └── secrets.yaml          # Staging secrets (encrypted)
│   └── prod/
│       ├── values.yaml           # Production environment values
│       └── secrets.yaml          # Production secrets (encrypted)
├── .gitlab-ci.yml                # GitLab CI/CD pipeline for deployments
└── README.md                     # This file
```

## GitOps Workflow

This repository follows GitOps principles where:

1. **Microservice CI/CD**: The {{ repo_name }} microservice builds and pushes Docker images
2. **Delivery Updates**: Image tags are updated in this repository
3. **Automatic Deployment**: Changes trigger deployments via GitLab CI/CD
4. **Environment Promotion**: Changes flow from dev → staging → prod

## Deployment Process

### Development Environment
- **Trigger**: Commits to `develop` branch in this repository
- **Image**: Uses `latest` tag or commit SHA
- **Approval**: Automatic on merge
- **URL**: https://{{ repo_name }}-dev.example.com

### Staging Environment  
- **Trigger**: Commits to `main` branch in this repository
- **Image**: Uses release candidate tags
- **Approval**: Manual deployment
- **URL**: https://{{ repo_name }}-staging.example.com

### Production Environment
- **Trigger**: Git tags (semantic versioning: v1.0.0)
- **Image**: Uses specific version tags
- **Approval**: Manual deployment with additional validations
- **URL**: https://{{ repo_name }}.example.com

## Manual Deployment Commands

### Prerequisites
```bash
# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/

# Configure kubectl context for your cluster
kubectl config use-context your-cluster-context
```

### Deploy to Development
```bash
helm upgrade --install {{ repo_name }}-dev ./helm \
  --namespace {{ repo_name }}-dev \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-dev.yaml \
  --values ./environments/dev/values.yaml \
  --set image.tag=latest
```

### Deploy to Staging
```bash
helm upgrade --install {{ repo_name }}-staging ./helm \
  --namespace {{ repo_name }}-staging \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-staging.yaml \
  --values ./environments/staging/values.yaml \
  --set image.tag=v1.2.0-rc1
```

### Deploy to Production
```bash
helm upgrade --install {{ repo_name }}-prod ./helm \
  --namespace {{ repo_name }}-prod \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-prod.yaml \
  --values ./environments/prod/values.yaml \
  --set image.tag=v1.2.0
```

## Environment Configuration

### Development
- **Resources**: Low resource limits for cost efficiency
- **Replicas**: 1 replica
- **Autoscaling**: Disabled
- **Security**: Basic security policies
- **Monitoring**: Debug logging enabled

### Staging
- **Resources**: Production-like resources for accurate testing
- **Replicas**: 2 replicas minimum
- **Autoscaling**: Enabled (2-5 replicas)
- **Security**: Enhanced security policies
- **Monitoring**: Info-level logging

### Production
- **Resources**: High resource limits for performance
- **Replicas**: 3 replicas minimum for high availability
- **Autoscaling**: Enabled (3-10 replicas)
- **Security**: Strict security policies, network policies
- **Monitoring**: Warning-level logging, full observability

## Security Best Practices

### Secrets Management
- **Never commit secrets in plain text**
- Use Helm Secrets, Sealed Secrets, or External Secrets Operator
- Different encryption keys per environment
- Regular secret rotation

### Network Security
- Network policies enabled in staging/production
- Service mesh integration ready
- TLS termination at ingress

### Pod Security
- Non-root containers
- Read-only root filesystem
- Security contexts configured
- Resource limits enforced

## Monitoring and Observability

### Health Checks
- Kubernetes liveness and readiness probes configured
- Health check endpoints: `/health` and `/ready`

### Metrics
- Prometheus metrics scraping enabled
- Custom application metrics supported
- Resource utilization monitoring

### Logging
- Structured JSON logging
- Log aggregation ready (ELK/Loki)
- Environment-specific log levels

### Tracing
- Distributed tracing headers propagation
- OpenTelemetry integration ready

## Troubleshooting

### View Deployment Status
```bash
# Check pods
kubectl get pods -n {{ repo_name }}-dev

# Check deployment status
kubectl rollout status deployment/{{ repo_name }} -n {{ repo_name }}-dev

# View logs
kubectl logs -f deployment/{{ repo_name }} -n {{ repo_name }}-dev
```

### Rollback Deployment
```bash
# Rollback to previous version
helm rollback {{ repo_name }}-prod --namespace {{ repo_name }}-prod

# Rollback to specific revision
helm rollback {{ repo_name }}-prod 3 --namespace {{ repo_name }}-prod
```

### Debug Helm Issues
```bash
# Dry run deployment
helm install {{ repo_name }}-test ./helm --dry-run --debug

# Template rendering
helm template {{ repo_name }} ./helm --values ./helm/values-dev.yaml

# Check release history
helm history {{ repo_name }}-prod --namespace {{ repo_name }}-prod
```

## CI/CD Variables

Configure these variables in your GitLab project settings:

### Required Variables
- `KUBE_CONTEXT_DEV`: Kubernetes context for development
- `KUBE_CONTEXT_STAGING`: Kubernetes context for staging  
- `KUBE_CONTEXT_PROD`: Kubernetes context for production

### Optional Variables
- `CLUSTER_DOMAIN`: Your cluster's domain (default: example.com)
- `MICROSERVICE_IMAGE`: Full image name (default: registry.gitlab.com/group/{{ repo_name }})

## Contributing

1. **Feature Changes**: Create MR against `develop` branch
2. **Release Preparation**: Create MR against `main` branch
3. **Production Release**: Create semantic version tag (v1.0.0)
4. **Hotfixes**: Create MR against `main` with hotfix tag

## Support

For deployment issues or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review GitLab CI/CD pipeline logs
- Contact the platform team for infrastructure issues

---

**Generated by GitLab Repository Sculptor**