# Helm Charts: Kubernetes Package Manager

Helm packages Kubernetes resources into reusable charts.

## Chart Structure

my-app/
  Chart.yaml          # metadata
  values.yaml         # default values
  templates/          # Kubernetes templates
    deployment.yaml
    service.yaml
    configmap.yaml
    secrets.yaml
    ingress.yaml
    _helpers.tpl      # template helpers
  charts/             # dependencies
  README.md

## Chart.yaml

apiVersion: v2
name: my-app
description: My application Helm chart
version: 1.0.0
appVersion: "1.0.0"
type: application

## Values

replicaCount: 3
image:
  repository: myregistry/my-app
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8080

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

ingress:
  enabled: true
  host: app.example.com
  tls: true

config:
  logLevel: INFO
  environment: production

## Template Example

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "my-app.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "my-app.name" . }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: 8080
          env:
            - name: LOG_LEVEL
              value: {{ .Values.config.logLevel }}
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          resources:
            {{- toYaml .Values.resources | nindent 12 }}

## Commands

helm install my-app ./chart
helm upgrade my-app ./chart --set image.tag=1.2.0
helm rollback my-app 1
helm list
helm uninstall my-app


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.
