global:
  scrape_interval: 10s
  scrape_timeout: 10s

rule_files:
  - alerts.yml

scrape_configs:
  - job_name: paralarva
    metrics_path: /metrics
    static_configs:
      - targets:
          - 'localhost:8000'
          - 'MINIKUBE_IP:30300'
