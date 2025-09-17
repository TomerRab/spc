# Environment Configurations

This directory contains environment-specific configurations for {{ repo_name }} deployments.

## Structure

```
environments/
├── dev/
│   ├── values.yaml          # Development environment values
│   └── secrets.yaml         # Development secrets (encrypted)
├── staging/
│   ├── values.yaml          # Staging environment values
│   └── secrets.yaml         # Staging secrets (encrypted)
├── prod/
│   ├── values.yaml          # Production environment values
│   └── secrets.yaml         # Production secrets (encrypted)
└── README.md                # This file
```

## Deployment Commands

### Development
```bash
helm upgrade --install {{ repo_name }}-dev ./helm \
  --namespace {{ repo_name }}-dev \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-dev.yaml \
  --values ./environments/dev/values.yaml
```

### Staging
```bash
helm upgrade --install {{ repo_name }}-staging ./helm \
  --namespace {{ repo_name }}-staging \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-staging.yaml \
  --values ./environments/staging/values.yaml
```

### Production
```bash
helm upgrade --install {{ repo_name }}-prod ./helm \
  --namespace {{ repo_name }}-prod \
  --create-namespace \
  --values ./helm/values.yaml \
  --values ./helm/values-prod.yaml \
  --values ./environments/prod/values.yaml
```

## Security Notes

- All secrets should be encrypted using tools like Helm Secrets, Sealed Secrets, or External Secrets Operator
- Never commit unencrypted secrets to version control
- Use different encryption keys for each environment
- Regularly rotate secrets and encryption keys

## GitOps Workflow

1. **Code Change**: Microservice code is updated
2. **CI/CD Build**: Microservice CI builds and pushes new image
3. **Delivery Update**: Update image tag in appropriate environment values
4. **GitOps Sync**: ArgoCD/Flux syncs changes to Kubernetes
5. **Deployment**: New version is deployed automatically

## Environment Promotion

Changes flow through environments in this order:
1. **Development** - Latest changes, frequent deployments
2. **Staging** - Release candidates, testing and validation  
3. **Production** - Stable releases, manual approval required