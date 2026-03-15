"""Integration tests for application and seat endpoints."""


from tests.helpers.assertions import assert_api_success, assert_status_code
from tests.helpers.auth import auth_header


class TestApplyToProject:
    async def test_apply_success(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        # Create a project as founder
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Apply Test",
            "summary": "Test project for applications",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        # Apply as collaborator
        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={
                "seat_preference": "growth",
                "intended_role": "developer",
                "motivation": "I want to help",
                "availability": "10h/week",
            },
            headers=collab_headers,
        )
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert data["status"] == "submitted"
        assert data["seat_preference"] == "growth"

    async def test_apply_to_own_project_rejected(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Self Apply Test",
            "summary": "Cannot apply to own project",
        }, headers=headers)
        project_id = create_resp.json()["data"]["project_id"]

        resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={
                "seat_preference": "growth",
                "intended_role": "developer",
            },
            headers=headers,
        )
        assert_status_code(resp, 409)

    async def test_duplicate_application_rejected(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Dup Apply Test",
            "summary": "Test duplicate application",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        payload = {
            "seat_preference": "growth",
            "intended_role": "developer",
        }
        await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json=payload, headers=collab_headers,
        )
        resp2 = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json=payload, headers=collab_headers,
        )
        assert_status_code(resp2, 409)


class TestListApplications:
    async def test_owner_can_list(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "List Apps Test",
            "summary": "Test listing applications",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "growth", "intended_role": "designer"},
            headers=collab_headers,
        )

        resp = await client.get(
            f"/api/v1/projects/{project_id}/applications",
            headers=founder_headers,
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert len(data) == 1

    async def test_non_owner_cannot_list(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Forbidden List Test",
            "summary": "Non-owner list attempt",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        resp = await client.get(
            f"/api/v1/projects/{project_id}/applications",
            headers=collab_headers,
        )
        assert_status_code(resp, 403)


class TestReviewApplication:
    async def test_accept_application_creates_seat(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Accept Test",
            "summary": "Test accepting application",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        app_resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "growth", "intended_role": "tester"},
            headers=collab_headers,
        )
        app_id = app_resp.json()["data"]["application_id"]

        review_resp = await client.patch(
            f"/api/v1/applications/{app_id}",
            json={"decision": "accepted"},
            headers=founder_headers,
        )
        assert_status_code(review_resp, 200)
        data = assert_api_success(review_resp.json())
        assert data["status"] == "accepted"

        # Verify seat was created
        seats_resp = await client.get(
            f"/api/v1/projects/{project_id}/seats",
            headers=founder_headers,
        )
        assert_status_code(seats_resp, 200)
        seats = assert_api_success(seats_resp.json())
        assert len(seats) == 1
        assert seats[0]["seat_type"] == "growth"

    async def test_reject_application(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Reject Test",
            "summary": "Test rejecting application",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        app_resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "formal", "intended_role": "analyst"},
            headers=collab_headers,
        )
        app_id = app_resp.json()["data"]["application_id"]

        review_resp = await client.patch(
            f"/api/v1/applications/{app_id}",
            json={"decision": "rejected"},
            headers=founder_headers,
        )
        assert_status_code(review_resp, 200)
        data = assert_api_success(review_resp.json())
        assert data["status"] == "rejected"


class TestWithdrawApplication:
    async def test_withdraw_success(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Withdraw Test",
            "summary": "Test withdrawing application",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        app_resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "growth", "intended_role": "developer"},
            headers=collab_headers,
        )
        app_id = app_resp.json()["data"]["application_id"]

        withdraw_resp = await client.patch(
            f"/api/v1/applications/{app_id}/withdraw",
            headers=collab_headers,
        )
        assert_status_code(withdraw_resp, 200)
        data = assert_api_success(withdraw_resp.json())
        assert data["status"] == "withdrawn"

    async def test_withdraw_by_non_applicant_rejected(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Withdraw Forbidden Test",
            "summary": "Non-applicant withdraw attempt",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        app_resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "growth", "intended_role": "developer"},
            headers=collab_headers,
        )
        app_id = app_resp.json()["data"]["application_id"]

        # Founder tries to withdraw (should fail — only applicant can)
        resp = await client.patch(
            f"/api/v1/applications/{app_id}/withdraw",
            headers=founder_headers,
        )
        assert_status_code(resp, 403)

    async def test_withdraw_already_accepted_rejected(
        self, client, founder_account, founder_actor,
        collaborator_account, collaborator_actor,
    ):
        founder_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Withdraw After Accept Test",
            "summary": "Cannot withdraw accepted application",
        }, headers=founder_headers)
        project_id = create_resp.json()["data"]["project_id"]

        collab_headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        app_resp = await client.post(
            f"/api/v1/projects/{project_id}/applications",
            json={"seat_preference": "growth", "intended_role": "developer"},
            headers=collab_headers,
        )
        app_id = app_resp.json()["data"]["application_id"]

        # Accept first
        await client.patch(
            f"/api/v1/applications/{app_id}",
            json={"decision": "accepted"},
            headers=founder_headers,
        )

        # Try to withdraw — should fail
        resp = await client.patch(
            f"/api/v1/applications/{app_id}/withdraw",
            headers=collab_headers,
        )
        assert_status_code(resp, 409)
