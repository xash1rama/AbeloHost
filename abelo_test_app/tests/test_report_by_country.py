import pytest


@pytest.mark.asyncio
async def test_get_report_by_country(aclient):
    response = await aclient.get("/report/by-country", params={
        "sort_by": "total",
        "top_n": 5
    })

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert len(data) <= 5
        assert "country" in data[0]
        assert "total" in data[0]
