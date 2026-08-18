# Kubernetes Production Deployment MVP

A complete beginner-friendly **FastAPI + Docker + Kubernetes** project designed to demonstrate a production-style Kubernetes deployment using **Docker Desktop Kubernetes**.

This project is intended for:


- Understanding production deployment concepts

---

## Project Objective

Deploy a FastAPI backend on Kubernetes and demonstrate:

- Namespace
- ConfigMap
- Secret
- PersistentVolumeClaim (PVC)
- Deployment
- Multiple replicas
- Service
- Ingress
- Horizontal Pod Autoscaler (HPA)
- NetworkPolicy
- Readiness Probe
- Liveness Probe
- Resource Requests and Limits
- Manual Scaling
- Rolling Update
- Rollback

---

# Architecture

```text
                    USER / BROWSER
                          |
                          |
                http://backend.local
                          |
                          v
                       INGRESS
                          |
                          v
                       SERVICE
                    backend-service
                      80 -> 8000
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
            POD 1       POD 2       POD 3
              |           |           |
              |           |           |
          FastAPI      FastAPI      FastAPI
          :8000        :8000        :8000

               Kubernetes Deployment
                       backend
                          ^
                          |
                         HPA

        ConfigMap -------> Pods
        Secret ----------> Pods
        PVC -------------> Pods
        NetworkPolicy ---> Protects Pods
```

The complete flow is:

```text
Code
  |
  v
Dockerfile
  |
  v
Docker Image
  |
  v
Kubernetes Deployment
  |
  v
ReplicaSet
  |
  v
Pods
  |
  v
Service
  |
  +--------> Port Forward --------> localhost:8000
  |
  v
Ingress
  |
  v
Browser
```

---

# Project Structure

```text
kubernetes-production-deployment-mvp/
|
|-- app/
|   `-- main.py
|
|-- k8s/
|   |-- 00-namespace.yaml
|   |-- 01-configmap.yaml
|   |-- 02-secret.yaml
|   |-- 03-pvc.yaml
|   |-- 04-deployment.yaml
|   |-- 05-service.yaml
|   |-- 06-ingress.yaml
|   |-- 07-hpa.yaml
|   `-- 08-networkpolicy.yaml
|
|
|   
|  
|   
|
|-- Dockerfile
|-- requirements.txt
|-- .dockerignore
`-- README.md
```

---

# Technologies Used

- Python
- FastAPI
- Uvicorn
- Docker
- Docker Desktop
- Kubernetes
- kubectl
- NGINX Ingress Controller
- YAML

---

# Prerequisites

Install the following tools before running the project:

- Docker Desktop
- kubectl
- Git
- VS Code (recommended)

Check Docker:

```powershell
docker --version
```

Check kubectl:

```powershell
kubectl version --client
```

---

# Enable Kubernetes in Docker Desktop

Open:

```text
Docker Desktop
    |
    v
Settings
    |
    v
Kubernetes
```

Enable Kubernetes.

After Kubernetes starts, run:

```powershell
kubectl get nodes
```

Expected output should contain a node with status:

```text
Ready
```

For example:

```text
NAME             STATUS   ROLES           AGE
docker-desktop   Ready    control-plane   ...
```

Also verify the current Kubernetes context:

```powershell
kubectl config current-context
```

For Docker Desktop it should normally be:

```text
docker-desktop
```

If necessary:

```powershell
kubectl config use-context docker-desktop
```

---

# FastAPI Application

The application is located in:

```text
app/main.py
```

Important endpoints include:

```text
GET /
GET /health
GET /config
GET /pod
GET /items
POST /items
```

Swagger UI will be available at:

```text
http://localhost:8000/docs
```

after port-forwarding the Kubernetes Service.

---

# Build the Docker Image

Open PowerShell inside the project root.

Example:

```powershell
cd C:\path\to\kubernetes-production-deployment-mvp
```

Build:

```powershell
docker build -t k8s-production-backend:1.0.0 .
```

Check the image:

```powershell
docker images
```

Expected:

```text
REPOSITORY                  TAG
k8s-production-backend      1.0.0
```

---

# Test the Docker Image Locally

Before Kubernetes deployment, you can test the container directly.

Run:

```powershell
docker run -d --name k8s-backend -p 8000:8000 k8s-production-backend:1.0.0
```

Check:

```powershell
docker ps
```

Open:

```text
http://localhost:8000/docs
```

Stop the container:

```powershell
docker stop k8s-backend
```

Remove it:

```powershell
docker rm k8s-backend
```

---

# Kubernetes YAML Files

## 1. Namespace

File:

```text
k8s/00-namespace.yaml
```

Creates a namespace called:

```text
k8s-demo
```

Purpose:

A Namespace logically groups Kubernetes resources.

Architecture:

```text
Kubernetes Cluster
|
`-- Namespace: k8s-demo
    |-- Deployment
    |-- Service
    |-- ConfigMap
    |-- Secret
    |-- PVC
    |-- Ingress
    `-- HPA
```

Apply:

```powershell
kubectl apply -f k8s/00-namespace.yaml
```

Check:

```powershell
kubectl get namespaces
```

---

# 2. ConfigMap

File:

```text
k8s/01-configmap.yaml
```

Stores non-sensitive configuration such as:

```text
APP_NAME
APP_VERSION
LOG_LEVEL
```

Apply:

```powershell
kubectl apply -f k8s/01-configmap.yaml
```

Check:

```powershell
kubectl get configmap -n k8s-demo
```

Inspect:

```powershell
kubectl describe configmap backend-config -n k8s-demo
```

Concept:

```text
ConfigMap
   |
   v
Environment Variables
   |
   v
FastAPI Container
```

Do not store passwords or private API keys in ConfigMaps.

---

# 3. Secret

File:

```text
k8s/02-secret.yaml
```

Stores sensitive configuration.

Example:

```text
API_KEY
```

Apply:

```powershell
kubectl apply -f k8s/02-secret.yaml
```

Check:

```powershell
kubectl get secrets -n k8s-demo
```

Concept:

```text
Secret
  |
  v
Container Environment
  |
  v
FastAPI
```

For real production environments, consider dedicated secret-management systems such as AWS Secrets Manager, HashiCorp Vault, or External Secrets.

---

# 4. PersistentVolumeClaim

File:

```text
k8s/03-pvc.yaml
```

PVC stands for:

```text
PersistentVolumeClaim
```

The project requests:

```text
1Gi
```

of storage.

Apply:

```powershell
kubectl apply -f k8s/03-pvc.yaml
```

Check:

```powershell
kubectl get pvc -n k8s-demo
```

Expected status:

```text
Bound
```

The Deployment mounts the volume at:

```text
/data
```

Concept:

```text
PVC
 |
 v
Persistent Storage
 |
 v
/data inside container
```

For a real multi-replica application, shared application state should generally live in an external database instead of depending on a single local PVC.

---

# 5. Deployment

File:

```text
k8s/04-deployment.yaml
```

The Deployment is the main Kubernetes workload controller.

It creates and manages Pods.

The project uses:

```yaml
replicas: 3
```

Therefore:

```text
Deployment
    |
    v
ReplicaSet
    |
    +---- Pod 1
    +---- Pod 2
    `---- Pod 3
```

Apply:

```powershell
kubectl apply -f k8s/04-deployment.yaml
```

Check:

```powershell
kubectl get deployment -n k8s-demo
```

Check Pods:

```powershell
kubectl get pods -n k8s-demo
```

Show detailed Pod information:

```powershell
kubectl get pods -n k8s-demo -o wide
```

---

# Deployment Features

The Deployment demonstrates:

## Multiple Replicas

```yaml
replicas: 3
```

Three copies of the FastAPI application are created.

---

## Rolling Update

```yaml
strategy:
  type: RollingUpdate
```

Rolling updates replace old Pods gradually instead of stopping the complete application.

---

## Readiness Probe

Checks whether a Pod is ready to receive traffic.

Endpoint:

```text
/health
```

Concept:

```text
Pod starts
   |
   v
Readiness Probe
   |
   +-- Healthy --> Service sends traffic
   |
   `-- Not Ready --> No traffic
```

---

## Liveness Probe

Checks whether the application is still alive.

If the liveness probe repeatedly fails, Kubernetes can restart the container.

---

## Resource Requests

Example:

```yaml
requests:
  cpu: "100m"
  memory: "128Mi"
```

Requests tell Kubernetes how much resource the container needs for scheduling.

---

## Resource Limits

Example:

```yaml
limits:
  cpu: "500m"
  memory: "512Mi"
```

Limits define the maximum resource allocation for the container.

---

# 6. Service

File:

```text
k8s/05-service.yaml
```

The Service provides stable networking for Pods.

Apply:

```powershell
kubectl apply -f k8s/05-service.yaml
```

Check:

```powershell
kubectl get svc -n k8s-demo
```

The Service uses:

```text
ClusterIP
```

and maps:

```text
Service port 80
      |
      v
Container port 8000
```

Architecture:

```text
              Service
                 |
        +--------+--------+
        |        |        |
        v        v        v
      Pod 1    Pod 2    Pod 3
```

The Service finds the Pods using Kubernetes labels.

---

# Test Through Port Forward

Run:

```powershell
kubectl port-forward svc/backend-service 8000:80 -n k8s-demo
```

Meaning:

```text
localhost:8000
      |
      v
Kubernetes Service :80
      |
      v
Pod :8000
```

Open:

```text
http://localhost:8000/docs
```

Test health:

```text
http://localhost:8000/health
```

Test Pod information:

```text
http://localhost:8000/pod
```

---

# 7. Ingress

File:

```text
k8s/06-ingress.yaml
```

Ingress exposes HTTP routes into the cluster.

Architecture:

```text
Browser
   |
   v
Ingress
   |
   v
Service
   |
   v
Pods
```

Apply:

```powershell
kubectl apply -f k8s/06-ingress.yaml
```

Check:

```powershell
kubectl get ingress -n k8s-demo
```

The project uses:

```text
backend.local
```

Important:

The YAML uses an NGINX ingress class, so an NGINX Ingress Controller must be installed before Ingress routing will work.

Port-forwarding the Service works without Ingress and is the easiest option for initial testing.

---

# 8. Horizontal Pod Autoscaler

File:

```text
k8s/07-hpa.yaml
```

HPA stands for:

```text
Horizontal Pod Autoscaler
```

Configuration:

```text
Minimum replicas = 3
Maximum replicas = 6
Target CPU = 60%
```

Apply:

```powershell
kubectl apply -f k8s/07-hpa.yaml
```

Check:

```powershell
kubectl get hpa -n k8s-demo
```

Describe:

```powershell
kubectl describe hpa backend-hpa -n k8s-demo
```

Concept:

```text
Low CPU
  |
  v
3 Pods

CPU increases
  |
  v
4 Pods

More load
  |
  v
5 Pods

High load
  |
  v
6 Pods
```

---

# Metrics Server Requirement

CPU-based HPA requires Kubernetes metrics.

Test:

```powershell
kubectl top pods -n k8s-demo
```

If you get:

```text
Metrics API not available
```

the HPA does not currently have CPU metrics.

The Deployment and Pods can still run normally, but automatic CPU-based scaling will not function until a metrics provider is installed.

---

# 9. NetworkPolicy

File:

```text
k8s/08-networkpolicy.yaml
```

NetworkPolicy controls allowed network traffic to Pods.

Apply:

```powershell
kubectl apply -f k8s/08-networkpolicy.yaml
```

Check:

```powershell
kubectl get networkpolicy -n k8s-demo
```

Concept:

```text
Allowed Traffic
      |
      v
   Backend Pods

Blocked Traffic
      |
      X
   Backend Pods
```

NetworkPolicy behavior depends on whether the Kubernetes network implementation supports NetworkPolicy enforcement.

---

# Deploy Everything Step by Step

Run from the project root:

```powershell
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-pvc.yaml
kubectl apply -f k8s/04-deployment.yaml
kubectl apply -f k8s/05-service.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-hpa.yaml
kubectl apply -f k8s/08-networkpolicy.yaml
```

---

# Deploy Everything at Once

After understanding each file individually:

```powershell
kubectl apply -f k8s/
```

---

# Verify the Deployment

Show everything:

```powershell
kubectl get all -n k8s-demo
```

Pods:

```powershell
kubectl get pods -n k8s-demo
```

Pods with networking information:

```powershell
kubectl get pods -n k8s-demo -o wide
```

Deployment:

```powershell
kubectl get deployment -n k8s-demo
```

Service:

```powershell
kubectl get svc -n k8s-demo
```

ConfigMap:

```powershell
kubectl get configmap -n k8s-demo
```

Secret:

```powershell
kubectl get secret -n k8s-demo
```

PVC:

```powershell
kubectl get pvc -n k8s-demo
```

Ingress:

```powershell
kubectl get ingress -n k8s-demo
```

HPA:

```powershell
kubectl get hpa -n k8s-demo
```

NetworkPolicy:

```powershell
kubectl get networkpolicy -n k8s-demo
```

---

# Check Application Logs

Get Pods:

```powershell
kubectl get pods -n k8s-demo
```

Then:

```powershell
kubectl logs <pod-name> -n k8s-demo
```

Example:

```powershell
kubectl logs backend-xxxxxxxxxx-xxxxx -n k8s-demo
```

Follow live logs:

```powershell
kubectl logs -f <pod-name> -n k8s-demo
```

---

# Describe a Pod

```powershell
kubectl describe pod <pod-name> -n k8s-demo
```

This is useful for troubleshooting:

- Image issues
- Probe failures
- Scheduling problems
- Volume errors
- Environment variables
- Events

---

# Demonstrate Multiple Replicas

Check:

```powershell
kubectl get pods -n k8s-demo
```

You should normally see three backend Pods.

Architecture:

```text
Deployment
    |
    +---- Pod 1
    |
    +---- Pod 2
    |
    `---- Pod 3
```

---

# Demonstrate Manual Scaling

Scale from three Pods to five:

```powershell
kubectl scale deployment backend --replicas=5 -n k8s-demo
```

Check:

```powershell
kubectl get pods -n k8s-demo
```

You should now see five Pods.

Scale back:

```powershell
kubectl scale deployment backend --replicas=3 -n k8s-demo
```

---

# Demonstrate Rolling Update

Build a new image:

```powershell
docker build -t k8s-production-backend:2.0.0 .
```

Update the Deployment:

```powershell
kubectl set image deployment/backend backend=k8s-production-backend:2.0.0 -n k8s-demo
```

Watch rollout status:

```powershell
kubectl rollout status deployment/backend -n k8s-demo
```

Watch Pods:

```powershell
kubectl get pods -n k8s-demo -w
```

Show rollout history:

```powershell
kubectl rollout history deployment/backend -n k8s-demo
```

Concept:

```text
Version 1 Pods
     |
     v
Create Version 2 Pod
     |
     v
Wait until Ready
     |
     v
Remove old Pod
     |
     v
Continue
     |
     v
All Pods running Version 2
```

---

# Demonstrate Rollback

If the new application version has a problem:

```powershell
kubectl rollout undo deployment/backend -n k8s-demo
```

Check:

```powershell
kubectl rollout status deployment/backend -n k8s-demo
```

Show history:

```powershell
kubectl rollout history deployment/backend -n k8s-demo
```

Concept:

```text
Version 1
    |
    v
Version 2
    |
    v
Problem
    |
    v
Rollback
    |
    v
Previous Deployment Version
```

---






# Useful kubectl Commands

## Cluster

```powershell
kubectl get nodes
```

## Namespace

```powershell
kubectl get namespaces
```

## All namespace resources

```powershell
kubectl get all -n k8s-demo
```

## Pods

```powershell
kubectl get pods -n k8s-demo
```

## Deployment

```powershell
kubectl get deployment -n k8s-demo
```

## ReplicaSets

```powershell
kubectl get replicasets -n k8s-demo
```

## Service

```powershell
kubectl get svc -n k8s-demo
```

## PVC

```powershell
kubectl get pvc -n k8s-demo
```

## Ingress

```powershell
kubectl get ingress -n k8s-demo
```

## HPA

```powershell
kubectl get hpa -n k8s-demo
```

## Pod logs

```powershell
kubectl logs <pod-name> -n k8s-demo
```

## Pod details

```powershell
kubectl describe pod <pod-name> -n k8s-demo
```

## Deployment details

```powershell
kubectl describe deployment backend -n k8s-demo
```

---

# Troubleshooting

## Kubernetes API Server Not Reachable

Example error:

```text
failed to download openapi
dial tcp 127.0.0.1:xxxxx
No connection could be made because the target machine actively refused it
```

Check context:

```powershell
kubectl config current-context
```

Switch to Docker Desktop:

```powershell
kubectl config use-context docker-desktop
```

Check the cluster:

```powershell
kubectl get nodes
```

Make sure Docker Desktop Kubernetes is running.

---

## Metrics API Not Available

Error:

```text
Metrics API not available
```

This means CPU/memory metrics are not available to HPA.

Test:

```powershell
kubectl top pods -n k8s-demo
```

The normal Deployment and Service can still work.

---

## ImagePullBackOff

Check:

```powershell
kubectl describe pod <pod-name> -n k8s-demo
```

Verify the image exists:

```powershell
docker images
```

For Docker Desktop Kubernetes, local images can generally be used by the Docker Desktop Kubernetes environment depending on the container runtime configuration.

---

## Pods Not Ready

Check:

```powershell
kubectl get pods -n k8s-demo
```

Describe the Pod:

```powershell
kubectl describe pod <pod-name> -n k8s-demo
```

Check logs:

```powershell
kubectl logs <pod-name> -n k8s-demo
```

---

# Cleanup

Delete the entire application:

```powershell
kubectl delete namespace k8s-demo
```

Because most resources are inside the namespace, deleting the namespace removes them together.

Check:

```powershell
kubectl get namespaces
```

---

# Production Improvements

This MVP demonstrates important production concepts, but a real enterprise deployment may also include:

- Amazon EKS / Azure AKS / Google GKE
- Amazon ECR or another container registry
- AWS Load Balancer Controller
- TLS/HTTPS certificates
- AWS Secrets Manager
- External Secrets Operator
- PostgreSQL / Amazon RDS
- Redis / Amazon ElastiCache
- Prometheus
- Grafana
- CloudWatch
- Centralized logging
- PodDisruptionBudget
- Karpenter or Cluster Autoscaler
- CI/CD with GitHub Actions
- Helm
- Terraform
- Multi-AZ deployment
- Backup and disaster recovery
- Security scanning

---

# Final Mental Model

```text
Developer writes code
        |
        v
Dockerfile builds image
        |
        v
Docker Image
        |
        v
Deployment
        |
        v
ReplicaSet
        |
        +------------+------------+
        |            |            |
        v            v            v
      Pod 1        Pod 2        Pod 3
        \            |            /
         \           |           /
          +----------+----------+
                     |
                     v
                  Service
                     |
             +-------+-------+
             |               |
             v               v
        Port Forward       Ingress
             |               |
             v               v
     localhost:8000      backend.local
             |               |
             +-------+-------+
                     |
                     v
                   Browser
```

---

# Key Takeaway

Kubernetes separates responsibilities:

| Component | Purpose |
|---|---|
| Namespace | Organizes resources |
| ConfigMap | Stores non-sensitive configuration |
| Secret | Stores sensitive configuration |
| PVC | Requests persistent storage |
| Deployment | Manages application Pods |
| ReplicaSet | Maintains desired Pod count |
| Pod | Runs the application container |
| Service | Provides stable networking and load balancing |
| Ingress | Provides HTTP routing into the cluster |
| HPA | Automatically scales Pod replicas |
| NetworkPolicy | Controls Pod network access |
| Readiness Probe | Checks whether a Pod can receive traffic |
| Liveness Probe | Checks whether the application is alive |

The core production flow is:

```text
Deployment manages Pods
        |
Service exposes Pods internally
        |
Ingress exposes the Service externally
        |
HPA scales the Deployment
        |
RollingUpdate changes versions safely
        |
Rollback restores a previous version
```

---

## Author / Learning Project

Feel free to extend it with:

- PostgreSQL
- Redis
- Helm
- GitHub Actions
- AWS EKS
- Terraform
- Monitoring
- Centralized Logging
