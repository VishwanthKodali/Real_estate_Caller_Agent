import csv
import io
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.database.models import Prospect

class BulkUploadProspectsService:
    @staticmethod
    def bulk_upload_prospects(campaign_id: int, file_content: bytes, db: Session, user):
        from .helpers import get_campaign_or_404
        get_campaign_or_404(campaign_id, user, db)

        text = file_content.decode("utf-8-sig")  # Handle BOM
        reader = csv.DictReader(io.StringIO(text))

        added = 0
        skipped = 0
        errors = []

        for i, row in enumerate(reader, 1):
            phone = row.get("phone", "").strip()
            if not phone:
                errors.append(f"Row {i}: missing phone number")
                continue

            existing = db.query(Prospect).filter(
                Prospect.campaign_id == campaign_id,
                Prospect.phone == phone
            ).first()
            if existing:
                skipped += 1
                continue

            try:
                prospect = Prospect(
                    campaign_id=campaign_id,
                    name=row.get("name", "").strip() or None,
                    phone=phone,
                    email=row.get("email", "").strip() or None,
                    budget_min=float(row["budget_min"]) if row.get("budget_min", "").strip() else None,
                    budget_max=float(row["budget_max"]) if row.get("budget_max", "").strip() else None,
                    preferred_unit_type=row.get("preferred_unit_type", "").strip() or None,
                    preferred_location=row.get("preferred_location", "").strip() or None,
                    source=row.get("source", "").strip() or None,
                    notes=row.get("notes", "").strip() or None,
                )
                db.add(prospect)
                added += 1
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.commit()
        return {"added": added, "skipped_duplicates": skipped, "errors": errors}