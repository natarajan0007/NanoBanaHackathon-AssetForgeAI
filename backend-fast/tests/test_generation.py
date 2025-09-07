from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest
from app.models import Project, Asset, AssetFormat, GenerationJob
from app.models.asset_format import FormatType
from app.models.project import ProjectStatus

@pytest.fixture(scope="function")
def test_project_with_asset(db_session, regular_user):
    project = Project(name="Gen Test Project", user_id=regular_user.id, organization_id=regular_user.organization_id, status=ProjectStatus.READY_FOR_REVIEW)
    db_session.add(project)
    db_session.commit()
    asset = Asset(project_id=project.id, original_filename="test.jpg", storage_path="test.jpg", file_type="image/jpeg", file_size_bytes=123)
    db_session.add(asset)
    db_session.commit()
    return project

@pytest.fixture(scope="function")
def test_format(db_session, test_organization):
    asset_format = AssetFormat(name="Test Format", type=FormatType.RESIZING, width=100, height=100, organization_id=test_organization.id)
    db_session.add(asset_format)
    db_session.commit()
    return asset_format

def test_start_generation(client: TestClient, regular_user_token: str, test_project_with_asset, test_format):
    with patch('app.tasks.generation_tasks.process_generation_job.delay') as mock_task:
        response = client.post(
            "/api/v1/generate",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            json={
                "projectId": str(test_project_with_asset.id),
                "formatIds": [str(test_format.id)],
                "customResizes": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobId" in data
        mock_task.assert_called_once()

def test_get_generation_status(client: TestClient, regular_user_token: str, regular_user, db_session):
    job = GenerationJob(project_id=None, user_id=regular_user.id, status="processing", progress=50)
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/api/v1/generate/{job.id}/status", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["progress"] == 50

def test_get_generation_results_not_complete(client: TestClient, regular_user_token: str, regular_user, db_session):
    job = GenerationJob(project_id=None, user_id=regular_user.id, status="processing")
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/api/v1/generate/{job.id}/results", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 400 # Bad request as job is not complete
