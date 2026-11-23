from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_booking_correct():
    booking = {
        'name': 'string',
        'phone': '+72535664880',
        'booking_date': '2026-12-07',
        'booking_time': 14,
        'guests': 1
    }

    response = client.post('/api/bookings', json={'booking': booking})
    response_body = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    del response_body['id']
    assert response_body == booking | {'status': 'active'}

def test_post_booking_invalid_phone_time_guests():
    booking = {
        'name': 'string',
        'phone': '+725356648',
        'booking_date': '2026-12-07',
        'booking_time': 10,
        'guests': 13
    }

    response = client.post('/api/bookings', json={'booking': booking})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert r"String should match pattern '^\\+7\\d{10}$'" in response.text\
    and 'Input should be greater than or equal to 12' in response.text\
    and 'Input should be less than or equal to 10' in response.text

def test_post_booking_past_date():
    booking = {
        'name': 'string',
        'phone': '+79157680712',
        'booking_date': '2026-11-21',
        'booking_time': 13,
        'guests': 4
    }

    response = client.post('/api/bookings', json={'booking': booking})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()['message'] == 'Нельзя забронировать стол на прошедшую дату и больше чем на 30 дней вперёд.'

def test_post_booking_conflict():
    booking = {
        'name': 'string',
        'phone': '+79157680712',
        'booking_date': '2026-12-07',
        'booking_time': 13,
        'guests': 4
    }

    client.post('/api/bookings', json={'booking': booking})
    response = client.post('/api/bookings', json={'booking': booking})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'На эти дату и время уже есть бронирование. Если бронирование ваше и вы хотите изменить его, то отмените и повторите бронирование с новыми данными.' in response.json()['message']
