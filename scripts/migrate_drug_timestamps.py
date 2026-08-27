import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import db
from bson import ObjectId
from datetime import datetime, timezone

async def migrate_drug_timestamps():
    print("Connecting to MongoDB and checking drug timestamps...")
    cursor = db.drugs.find({})
    total_drugs = await db.drugs.count_documents({})
    print(f"Total drugs found in database: {total_drugs}")

    updated_count = 0
    async for drug in cursor:
        d_id = drug.get("_id")
        name = drug.get("drugName") or (drug.get("ProductOverview") or {}).get("drugName") or str(d_id)
        cid = drug.get("cid") or (drug.get("ProductOverview") or {}).get("cid") or "Unknown CID"
        po = drug.get("ProductOverview") if isinstance(drug.get("ProductOverview"), dict) else {}

        # 1. Determine creation timestamp
        created_at = drug.get("createdAt") or po.get("createdAt")
        if not created_at and d_id and ObjectId.is_valid(str(d_id)):
            created_at = ObjectId(str(d_id)).generation_time.isoformat()
        if not created_at:
            created_at = datetime.now(timezone.utc).isoformat()

        # 2. Determine update timestamp
        updated_at = drug.get("updatedAt") or po.get("updatedAt") or created_at

        # 3. Determine if update is required
        needs_update = (
            not drug.get("createdAt") or
            not drug.get("updatedAt") or
            ("ProductOverview" in drug and isinstance(drug["ProductOverview"], dict) and (
                not drug["ProductOverview"].get("createdAt") or
                not drug["ProductOverview"].get("updatedAt")
            ))
        )

        if needs_update and d_id:
            update_fields = {
                "createdAt": created_at,
                "updatedAt": updated_at
            }
            if "ProductOverview" in drug and isinstance(drug["ProductOverview"], dict):
                update_fields["ProductOverview.createdAt"] = created_at
                update_fields["ProductOverview.updatedAt"] = updated_at

            await db.drugs.update_one(
                {"_id": d_id},
                {"$set": update_fields}
            )
            updated_count += 1
            print(f"  Updated drug: {name} (CID: {cid}) -> createdAt: {created_at}, updatedAt: {updated_at}")

    print(f"\nMigration completed! Updated {updated_count} out of {total_drugs} drugs in MongoDB.")

if __name__ == "__main__":
    asyncio.run(migrate_drug_timestamps())
