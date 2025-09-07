from fastapi.testclient import TestClient

# Note: All fixtures like client, admin_token, etc., are now in conftest.py

def test_full_platform_lifecycle(client: TestClient, admin_token: str):
    # 1. Create Platform
    create_response = client.post(
        "/api/v1/admin/platforms",
        json={"name": "Platform Lifecycle Test"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 200
    platform_data = create_response.json()
    platform_id = platform_data["id"]
    assert platform_data["name"] == "Platform Lifecycle Test"

    # 2. Read Platform
    list_response = client.get("/api/v1/admin/platforms", headers={"Authorization": f"Bearer {admin_token}"})
    assert list_response.status_code == 200
    assert any(p['id'] == platform_id for p in list_response.json())

    # 3. Update Platform
    update_response = client.put(
        f"/api/v1/admin/platforms/{platform_id}",
        json={"name": "Updated Platform Name"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Platform Name"

    # 4. Delete Platform
    delete_response = client.delete(f"/api/v1/admin/platforms/{platform_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_response.status_code == 204

    # Verify Deletion
    final_list_response = client.get("/api/v1/admin/platforms", headers={"Authorization": f"Bearer {admin_token}"})
    assert not any(p['id'] == platform_id for p in final_list_response.json())

def test_full_format_lifecycle(client: TestClient, admin_token: str):
    # 1. Create
    create_res = client.post(
        "/api/v1/admin/formats",
        json={"name": "Format Lifecycle Test", "type": "resizing", "category": "Web", "width": 800, "height": 600},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_res.status_code == 200
    format_id = create_res.json()["id"]

    # 2. Read
    list_res = client.get("/api/v1/admin/formats", headers={"Authorization": f"Bearer {admin_token}"})
    assert any(f['id'] == format_id for f in list_res.json())

    # 3. Update
    update_res = client.put(
        f"/api/v1/admin/formats/{format_id}",
        json={"name": "Updated Format"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Format"

    # 4. Delete
    delete_res = client.delete(f"/api/v1/admin/formats/{format_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_res.status_code == 204

def test_full_text_style_set_lifecycle(client: TestClient, admin_token: str):
    # 1. Create
    style_data = {"name": "Style Lifecycle Test", "styles": {"title": {"fontFamily": "Arial", "fontSize": 12, "fontWeight": "normal", "color": "#fff"}}}
    create_res = client.post("/api/v1/admin/text-style-sets", json=style_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_res.status_code == 200
    set_id = create_res.json()["id"]

    # 2. Read
    list_res = client.get("/api/v1/admin/text-style-sets", headers={"Authorization": f"Bearer {admin_token}"})
    assert any(s['id'] == set_id for s in list_res.json())

    # 3. Update
    update_res = client.put(f"/api/v1/admin/text-style-sets/{set_id}", json={"name": "New Style Name"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Style Name"

    # 4. Delete
    delete_res = client.delete(f"/api/v1/admin/text-style-sets/{set_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_res.status_code == 204

def test_get_and_update_all_rules(client: TestClient, admin_token: str):
    # Test Adaptation Rules
    get_adapt_res = client.get("/api/v1/admin/rules/adaptation", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_adapt_res.status_code == 200
    put_adapt_res = client.put(
        "/api/v1/admin/rules/adaptation",
        json={"focalPointLogic": "product-centric", "layoutGuidance": {}},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert put_adapt_res.status_code == 200
    assert put_adapt_res.json()["focalPointLogic"] == "product-centric"

    # Test AI Behavior Rules
    get_ai_res = client.get("/api/v1/admin/rules/ai-behavior", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_ai_res.status_code == 200
    put_ai_res = client.put(
        "/api/v1/admin/rules/ai-behavior",
        json={"adaptationStrategy": "extend", "imageQuality": "medium"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert put_ai_res.status_code == 200
    assert put_ai_res.json()["adaptationStrategy"] == "extend"

def test_unauthorized_access_to_admin_api(client: TestClient, regular_user_token: str):
    response = client.get("/api/v1/admin/platforms", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 403