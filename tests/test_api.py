"""
Integration tests for API endpoints.
"""

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}



def test_analyze_frames_too_few(client):
    """Test that too few frames raises validation error."""
    response = client.post(
        "/api/v1/analyze",
        json={"frames": ["frame1", "frame2"]}  # Only 2 frames, need 3-10
    )

    assert response.status_code == 422


def test_analyze_frames_too_many(client, sample_base64_frames):
    """Test that too many frames raises validation error."""
    # Create 11 frames (max is 10)
    too_many_frames = sample_base64_frames * 3  # 15 frames

    response = client.post(
        "/api/v1/analyze",
        json={"frames": too_many_frames}
    )

    assert response.status_code == 422


def test_analyze_invalid_base64(client):
    """Test that invalid base64 raises validation error."""
    response = client.post(
        "/api/v1/analyze",
        json={"frames": ["not_valid_base64!!!", "also_invalid", "third"]}
    )

    assert response.status_code == 422


def test_analyze_no_input(client):
    """Test that missing both inputs raises error."""
    response = client.post("/api/v1/analyze")

    assert response.status_code == 422
