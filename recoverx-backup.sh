#!/bin/bash
# 1. Connect to MinIO using environment variables
mc alias set backupstore http://192.168.0.8:9000 $MINIO_USER $MINIO_PASS

# 2. Get the app pod name
POD_NAME=$(kubectl get pods -l app=recoverx-app -o jsonpath="{.items[0].metadata.name}")

# 3. Copy the REAL database file from the Pod to the VM
kubectl cp default/$POD_NAME:/app/data/app.db /tmp/app.db

# 4. Create a timestamped filename
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="db-backup-$TIMESTAMP.db"

# 5. Upload the database to MinIO with a 1-day COMPLIANCE lock
mc cp /tmp/app.db backupstore/sentinel-backups/$BACKUP_FILE --retention-mode COMPLIANCE --retention-duration 1d

# 6. Clean up local file
rm /tmp/app.db
