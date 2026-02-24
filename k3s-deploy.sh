#!/bin/bash
set -e

echo "🚀 교회 웹사이트를 K3s에 배포합니다..."
echo "   (데이터는 K3s PersistentVolume에 영구 저장됩니다)"
echo ""

# K3s 매니페스트 생성
cat > /tmp/church-k3s.yaml <<'EOF'
---
apiVersion: v1
kind: Namespace
metadata:
  name: church
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: church-data
  namespace: church
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: church-uploads
  namespace: church
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 2Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: church-website
  namespace: church
spec:
  replicas: 1
  selector:
    matchLabels:
      app: church-website
  template:
    metadata:
      labels:
        app: church-website
    spec:
      containers:
      - name: church-website
        image: python:3.11-slim
        command: ["/bin/bash"]
        args:
          - -c
          - |
            set -e
            apt-get update && apt-get install -y sqlite3 git
            mkdir -p /tmp/church && cd /tmp/church
            git clone https://github.com/dhjin/church-website.git .
            pip install --no-cache-dir -r requirements.txt
            sed -i '1i import os' main.py
            sed -i 's|DB_PATH = "church.db"|DB_PATH = os.getenv("DB_PATH", "church.db")|' main.py
            export DB_PATH=/app/data/church.db
            python main.py
        ports:
        - containerPort: 8000
          name: http
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 128Mi
        volumeMounts:
        - name: church-data
          mountPath: /app/data
        - name: church-uploads
          mountPath: /app/uploads
        env:
        - name: DB_PATH
          value: /app/data/church.db
      volumes:
      - name: church-data
        persistentVolumeClaim:
          claimName: church-data
      - name: church-uploads
        persistentVolumeClaim:
          claimName: church-uploads
---
apiVersion: v1
kind: Service
metadata:
  name: church-service
  namespace: church
spec:
  type: NodePort
  selector:
    app: church-website
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30800
    protocol: TCP
EOF

# 기존 배포가 있으면 재배포 (롤링 업데이트)
echo "📦 K3s에 배포 중..."
kubectl apply -f /tmp/church-k3s.yaml

# Pod 준비 대기
echo "⏳ Pod 준비 중..."
kubectl wait --for=condition=ready pod -l app=church-website -n church --timeout=120s

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 배포 완료!"
echo ""
echo "📊 상태 확인:"
kubectl get pods -n church -o wide
echo ""
echo "🌐 접속 URL:"
echo "   - http://116.32.135.243/ (nginx 프록시)"
echo "   - http://<node-ip>:30800 (직접 접속)"
echo ""
echo "💾 데이터 저장소:"
kubectl get pvc -n church
echo ""
echo "📝 유용한 명령어:"
echo "   로그 확인: kubectl logs -n church -l app=church-website -f"
echo "   재배포: bash k3s-deploy.sh"
echo "   삭제: kubectl delete namespace church"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
