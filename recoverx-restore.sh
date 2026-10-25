#!/bin/bash
# 1. Get the name of the running Kubernetes pod
POD_NAME=$(kubectl get pods -l app=recoverx-app -o jsonpath="{.items[0].metadata.name}")

# 2. Find the latest backup file in MinIO (using environment variables)
export MC_HOST_localminio="http://$MINIO_USER:$MINIO_PASS@192.168.0.8:9000"
LATEST_BACKUP=$(mc ls localminio/sentinel-backups/ | grep "db-backup" | tail -n 1 | awk '{print $NF}')

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backup found in MinIO!"
    exit 1
fi

echo "🔄 Found latest backup: $LATEST_BACKUP"
echo "⬇️ Downloading from MinIO..."

# 3. Download it to the VM
mc cp localminio/sentinel-backups/$LATEST_BACKUP /tmp/restored.db

# 4. Copy it back into the Pod
kubectl cp /tmp/restored.db default/$POD_NAME:/app/data/app.db

echo "✅ Restore complete! Refresh your browser."
