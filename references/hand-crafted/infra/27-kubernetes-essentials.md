# Kubernetes for Developers

You do not need to be a K8s admin to deploy effectively.
But you need these concepts.

## Pod Lifecycle

A pod is the smallest deployable unit. It runs one or more containers.

apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  containers:
  - name: app
    image: myapp:latest
    ports:
    - containerPort: 8080
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"

## Resources: Requests vs Limits

Requests = guaranteed resources. Limits = maximum allowed.

If pod exceeds memory limit -> OOMKilled
If pod exceeds CPU limit -> throttled

Recommendation:
- requests = expected steady-state usage
- limits = requests * 1.5 to 2

## Health Probes

livenessProbe: Is the process alive? Just HTTP 200.
readinessProbe: Is it ready for traffic? Check dependencies.
startupProbe: Has initialization finished? For slow startups.

## Deployment

A Deployment manages pods with rolling updates and rollbacks.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest

## ConfigMaps and Secrets

ConfigMaps for non-sensitive config.
Secrets for sensitive data (base64 encoded).

## Debugging Commands

kubectl get pods - list pods
kubectl logs -f pod/name - stream logs
kubectl describe pod/name - detailed status
kubectl exec -it pod/name -- /bin/sh - shell into pod
kubectl port-forward pod/name 8080:8080 - local access
kubectl top pod - resource usage


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.
