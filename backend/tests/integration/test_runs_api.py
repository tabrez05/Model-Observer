import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["db"] == "connected"


@pytest.mark.asyncio
async def test_create_run(client):
    r = await client.post("/api/v1/runs", json={
        "name": "test-run",
        "model_type": "LinearSVC",
        "dataset": "banking77",
        "hyperparams": {"C": 1.0},
        "tags": ["test"],
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "test-run"
    assert data["status"] == "queued"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_run(client):
    create = await client.post("/api/v1/runs", json={"name": "get-test"})
    run_id = create.json()["id"]

    r = await client.get(f"/api/v1/runs/{run_id}")
    assert r.status_code == 200
    assert r.json()["id"] == run_id


@pytest.mark.asyncio
async def test_list_runs(client):
    for i in range(3):
        await client.post("/api/v1/runs", json={"name": f"run-{i}"})
    r = await client.get("/api/v1/runs")
    assert r.status_code == 200
    assert r.json()["total"] == 3


@pytest.mark.asyncio
async def test_update_run_status(client):
    create = await client.post("/api/v1/runs", json={"name": "update-test"})
    run_id = create.json()["id"]

    r = await client.patch(f"/api/v1/runs/{run_id}", json={
        "status": "completed",
        "final_metrics": {"macro_f1": 0.886},
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["final_metrics"]["macro_f1"] == 0.886
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_delete_run(client):
    create = await client.post("/api/v1/runs", json={"name": "delete-test"})
    run_id = create.json()["id"]

    r = await client.delete(f"/api/v1/runs/{run_id}")
    assert r.status_code == 204

    r = await client.get(f"/api/v1/runs/{run_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_run(client):
    r = await client.get("/api/v1/runs/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
