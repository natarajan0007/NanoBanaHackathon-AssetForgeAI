import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.asset import Asset
from app.models.generated_asset import GeneratedAsset
from app.core.config import settings

def fix_file_types():
    """
    Corrects the file_type field for existing assets in the database.
    Changes 'image/jpeg' to 'jpeg'.
    """
    print("Connecting to the database...")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("Fetching assets...")
        assets = db.query(Asset).all()
        updated_assets = 0
        for asset in assets:
            if '/' in asset.file_type:
                new_file_type = asset.file_type.split('/')[-1]
                print(f"Updating Asset {asset.id}: '{asset.file_type}' -> '{new_file_type}'")
                asset.file_type = new_file_type
                updated_assets += 1

        print(f"Updated {updated_assets} Asset records.")

        print("Fetching generated assets...")
        generated_assets = db.query(GeneratedAsset).all()
        updated_generated_assets = 0
        for gen_asset in generated_assets:
            if '/' in gen_asset.file_type:
                new_file_type = gen_asset.file_type.split('/')[-1]
                print(f"Updating GeneratedAsset {gen_asset.id}: '{gen_asset.file_type}' -> '{new_file_type}'")
                gen_asset.file_type = new_file_type
                updated_generated_assets += 1
        
        print(f"Updated {updated_generated_assets} GeneratedAsset records.")

        if updated_assets > 0 or updated_generated_assets > 0:
            print("Committing changes...")
            db.commit()
            print("Changes committed.")
        else:
            print("No records needed updating.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        print("Closing database session.")
        db.close()

if __name__ == "__main__":
    fix_file_types()
