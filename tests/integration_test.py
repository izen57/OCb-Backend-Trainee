from uuid import UUID

from fastapi import status

from fastapi.testclient import TestClient
import pytest

from main import app


client = TestClient(app)

@pytest.mark.incremental
class TestIntegration:
    booking1_id: UUID
    booking1 = {
        'name': 'string',
        'phone': '+72535664880',
        'booking_date': '2026-12-07',
        'booking_time': 20,
        'guests': 3
    }
    booking2_id: UUID
    booking2 = {
        'name': 'Максим',
        'phone': '+79999999999',
        'booking_date': '2026-12-08',
        'booking_time': 12,
        'guests': 10
    }

    def test_post(self):
        response = client.post('/api/bookings', json={'booking': TestIntegration.booking1})
        response_body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        TestIntegration.booking1_id = response_body.pop('id')
        assert response_body == TestIntegration.booking1 | {'status': 'active'}

    def test_get_by_id(self):
        response = client.get(f'/api/bookings/{TestIntegration.booking1_id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == TestIntegration.booking1 | {'status': 'active', 'id': TestIntegration.booking1_id}

    def test_get_all1(self):
        response = client.post('/api/bookings', json={'booking': TestIntegration.booking2})
        TestIntegration.booking2_id = response.json()['id']
        response = client.get('/api/bookings')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            TestIntegration.booking1 | {'status': 'active', 'id': TestIntegration.booking1_id},
            TestIntegration.booking2 | {'status': 'active', 'id': TestIntegration.booking2_id}
        ]

    def test_get_by_date(self):
        response = client.get('/api/bookings?date=2026-12-07')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [TestIntegration.booking1 | {'status': 'active', 'id': TestIntegration.booking1_id}]

    def test_delete(self):
        response = client.delete(f'/api/bookings/{TestIntegration.booking1_id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == TestIntegration.booking1 | {'status': 'cancelled', 'id': TestIntegration.booking1_id}

    def test_get_all2(self):
        response = client.get('/api/bookings')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            TestIntegration.booking1 | {'status': 'cancelled', 'id': TestIntegration.booking1_id},
            TestIntegration.booking2 | {'status': 'active', 'id': TestIntegration.booking2_id}
        ]