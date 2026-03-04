import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

print("🔍 Verifying imports...")

try:
    from models.cron import CronJob, CronExecution, Base
    print("✅ models.cron imported successfully")
except Exception as e:
    print(f"❌ Failed to import models.cron: {e}")
    sys.exit(1)

try:
    from schemas.cron import (
        CronJobBase, CronJobCreate, CronJobResponse,
        CronJobStatus, CronExecutionBase, CronExecutionResponse,
        CronExecutionStatus, CronStats
    )
    print("✅ schemas.cron imported successfully")
except Exception as e:
    print(f"❌ Failed to import schemas.cron: {e}")
    sys.exit(1)

try:
    from services.cron_service import CronService
    print("✅ services.cron_service imported successfully")
except Exception as e:
    print(f"❌ Failed to import services.cron_service: {e}")
    sys.exit(1)

try:
    from api.v1 import cron_routes
    print("✅ api.v1.cron_routes imported successfully")
except Exception as e:
    print(f"❌ Failed to import api.v1.cron_routes: {e}")
    sys.exit(1)

try:
    from models import Base as MainBase
    print("✅ models.__init__ imported successfully")
except Exception as e:
    print(f"❌ Failed to import models.__init__: {e}")
    sys.exit(1)

try:
    from schemas import CronJobBase as MainCronJobBase
    print("✅ schemas.__init__ imported successfully")
except Exception as e:
    print(f"❌ Failed to import schemas.__init__: {e}")
    sys.exit(1)

print("\n🎉 All imports verified successfully!")
