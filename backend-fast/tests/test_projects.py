from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# Test creating a project
def test_create_project(client: TestClient, regular_user_token: str):
    with patch('app.tasks.asset_processing.process_uploaded_assets.delay') as mock_task:
        dummy_file_content = b"test image data"
        dummy_file_name = "test.jpg"
        with open(dummy_file_name, "wb") as f:
            f.write(dummy_file_content)

        with open(dummy_file_name, "rb") as f:
            response = client.post(
                "/api/v1/projects/upload",
                headers={"Authorization": f"Bearer {regular_user_token}"},
                data={"projectName": "My First Project"},
                files={"files": (dummy_file_name, f, "image/jpeg")}
            )
        
        os.remove(dummy_file_name)

        assert response.status_code == 200
        data = response.json()
        assert "projectId" in data
        mock_task.assert_called_once()

# Test getting a list of projects
def test_get_projects(client: TestClient, regular_user_token: str):
    # First, create a project to ensure there is one to fetch
    with patch('app.tasks.asset_processing.process_uploaded_assets.delay'):
        with open("test.jpg", "wb") as f: f.write(b'')
        client.post(
            "/api/v1/projects/upload",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            data={"projectName": "List Test Project"},
            files={"files": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
        )
        os.remove("test.jpg")

    response = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert len(data["projects"]) > 0
    assert data["projects"][0]["name"] == "List Test Project"

# Test getting a single project
def test_get_project_by_id(client: TestClient, regular_user_token: str):
    # Create a project
    with patch('app.tasks.asset_processing.process_uploaded_assets.delay') as mock_task:
        with open("test.jpg", "wb") as f: f.write(b'')
        upload_response = client.post(
            "/api/v1/projects/upload",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            data={"projectName": "Single Project Test"},
            files={"files": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
        )
        os.remove("test.jpg")
    
    project_id = upload_response.json()["projectId"]

    # Fetch the project
    response = client.get(f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Project Test"
    assert data["id"] == project_id

# Test deleting a project
def test_delete_project(client: TestClient, regular_user_token: str):
    # Create a project
    with patch('app.tasks.asset_processing.process_uploaded_assets.delay') as mock_task:
        with open("test.jpg", "wb") as f: f.write(b'')
        upload_response = client.post(
            "/api/v1/projects/upload",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            data={"projectName": "To Be Deleted"},
            files={"files": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
        )
        os.remove("test.jpg")
    
    project_id = upload_response.json()["projectId"]

    # Delete the project
    delete_response = client.delete(f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert get_response.status_code == 404
