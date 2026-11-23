import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Body, FastAPI, Path, Query, status
from fastapi.responses import JSONResponse

from models import BookingCreate, BookingStore, ErrorMessage, bna_error_message, bne_error_message
from services import BookingsService

from exceptions import BookingNotAvailableException, BookingNotExistException, ValidationException


app = FastAPI()
service = BookingsService('sqlite:///database.db')

@app.post(
    '/api/bookings',
    summary='Создание бронирования.',
    response_model=BookingStore,
    status_code=status.HTTP_201_CREATED,
    response_description='Стол успешно забронирован.',
    responses={409: {'model': ErrorMessage, 'description': bna_error_message}}
)
def post_booking(booking: Annotated[BookingCreate, Body(embed=True)]):
    try:
        return service.create_booking(booking)
    except ValidationException as e:
        return JSONResponse(dict(ErrorMessage(message=str(e))), status.HTTP_422_UNPROCESSABLE_CONTENT)
    except BookingNotAvailableException as e:
        return JSONResponse(dict(ErrorMessage(message=str(e))), status.HTTP_409_CONFLICT)

@app.get(
    '/api/bookings',
    summary='Список бронирований.',
    description='Вывод списка всех бронирований (в том числе отменённых) в базе данных. '\
    'При указании даты будут выведены бронирования только на эту дату. '\
    'Если список пустой, то бронирований на эту дату нет.',
    response_description='Список бронирований.'
)
def get_bookings(date: Annotated[
    datetime.date | None,
    Query(description='(необязательно) Дата бронирований')
] = None) -> list[BookingStore]:
    return service.list_bookings(date)

@app.get(
    '/api/bookings/{id}',
    summary='Найти бронирование по идентификатору.',
    response_model=BookingStore,
    response_description='Найденное бронирование.',
    responses={404: {'model': ErrorMessage, 'description': bne_error_message}}
)
def get_booking_by_id(id: Annotated[UUID, Path(description='Номер бронирования.')]):
    try:
        return service.search_booking(id)
    except BookingNotExistException as e:
        return JSONResponse(dict(ErrorMessage(message=str(e))), status.HTTP_404_NOT_FOUND)

@app.delete(
    '/api/bookings/{id}',
    summary='Отмена бронирование по идентификатору.',
    description='Если отменить бронирование, то на его дату и время можно будет создать другое бронирование.',
    response_model=BookingStore,
    response_description='Отменённое бронирование.',
    responses={404: {'model': ErrorMessage, 'description': bne_error_message}}
)
def delete_booking(id: Annotated[UUID, Path(description='Номер бронирования.')]):
    try:
        return service.cancel_booking(id)
    except BookingNotExistException as e:
        return JSONResponse(dict(ErrorMessage(message=str(e))), status.HTTP_404_NOT_FOUND)
