import pytest


@pytest.mark.asyncio
async def test_get_report_basic(aclient):
    response = await aclient.get("/report", params={
        "status": "successful",
        "include_avg": True
    })

    assert response.status_code == 200
    data = response.json()
    assert "total_amount" in data
    assert "avg_amount" in data
