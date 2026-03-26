"""
Test suite for Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) pattern for clear test structure
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Arrange-Act-Assert: Verify all activities are returned"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == 3
        assert all(activity in data for activity in expected_activities)

    def test_get_activities_returns_activity_details(self, client):
        """Arrange-Act-Assert: Verify activity details structure"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_succeeds(self, client):
        """Arrange-Act-Assert: Successfully sign up a new student"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

        # Verify student was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Arrange-Act-Assert: Return 404 when activity doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_fails(self, client):
        """Arrange-Act-Assert: Prevent students from signing up twice"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_multiple_different_students_succeeds(self, client):
        """Arrange-Act-Assert: Multiple different students can sign up"""
        # Arrange
        activity_name = "Chess Club"
        new_students = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        # Act & Assert for each student
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all students were added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert all(email in participants for email in new_students)


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_succeeds(self, client):
        """Arrange-Act-Assert: Successfully unregister an enrolled student"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

        # Verify student was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Arrange-Act-Assert: Return 404 when activity doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """Arrange-Act-Assert: Return 400 when student isn't enrolled"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"

    def test_unregister_then_resign_up_succeeds(self, client):
        """Arrange-Act-Assert: Student can re-enroll after unregistering"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act - Unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act - Sign up again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify student is re-enrolled
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
