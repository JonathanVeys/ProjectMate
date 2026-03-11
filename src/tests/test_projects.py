from datetime import date
import pytest
import uuid
from typing import cast, Dict, Any

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


from main import app
from src.backend.api.supabase_client import supabase

testClient = TestClient(app)

TEST_USER_ID = "aee7a9a9-da3c-450f-be3a-26890851a0aa"

@pytest.mark.integration
def test_create_project_unauthenticated():
    response = testClient.post("/projects/create", data={
        "title": "Test Project",
        "deadline": str(date.today()),
        "description": "Test description"
    })
    assert response.status_code == 401

@pytest.mark.integration
def test_create_project():
    with patch("starlette.requests.HTTPConnection.session", 
               new_callable=lambda: property(lambda self: {"user": {"id":TEST_USER_ID}})):
        
        response = testClient.post("/projects/create", data={
            "title": "Test Project",
            "deadline": str(date.today()),
            "description": "This is a test project set up to test the create_project endpoint"
        })

        try:
            assert response.status_code == 200
            assert response.json()["success"] == True
        finally:
            supabase.table("projects")\
                .delete()\
                .eq("title", "Test Project")\
                .eq("user_id", TEST_USER_ID)\
                .execute()


@pytest.mark.integration
def test_delete_project():
    # 1. Create a project directly via supabase, bypassing the endpoint
    res = supabase.table("projects").insert({
        "user_id": TEST_USER_ID,
        "title": "Project to delete",
        "deadline": str(date.today()),
        "description": "This project should be deleted",
        "summary_json": {}
    }).execute()
    res = cast(Dict[str,Any], res.data[0])
    project_id = res["id"]
    
    # 2. Now test the delete endpoint
    try:
        with patch("starlette.requests.HTTPConnection.session",
                new_callable=lambda: property(
                    lambda self: {"user": {"id": TEST_USER_ID}}
                )):
            response = testClient.delete(f"/projects/delete/{project_id}")
            assert response.status_code == 200
            assert response.json()["success"] == True
            # 3. Verify it's actually gone
            check = supabase.table("projects").select("*").eq("id", project_id).execute()
            assert check.data == []
    finally:
        supabase.table("projects").delete().eq("id", project_id).execute()
