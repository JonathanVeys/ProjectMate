# test_supabase_client.py
import pytest
from src.backend.utils.supabase_client import supabase

@pytest.mark.integration
def test_supabase_client_is_initialised():
    """Test that the client object was created successfully"""
    assert supabase is not None

@pytest.mark.integration
def test_supabase_client_can_reach_database():
    """Test that we can make a real query to Supabase"""
    # Pick any table you know exists, just fetch one row
    response = supabase.table("projects").select("*").limit(1).execute()
    assert response.data is not None

@pytest.mark.integration
def test_supabase_environment_variables_are_set():
    """Test that required env vars are present"""
    import os
    assert os.getenv("SUPABASE_URL") is not None, "SUPABASE_URL is not set"
    assert os.getenv("SUPABASE_SERVICE_ROLE_KEY") is not None, "SUPABASE_SERVICE_ROLE_KEY is not set"