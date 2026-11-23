from datetime import date
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    name: str = Field(
        title='Имя гостя (от 2 до 50 символов).',
        min_length=2,
        max_length=50
    )
    phone: str = Field(
        title='Номер в формате +7XXXXXXXXXX (ровно 10 цифр после +7).',
        pattern=r'^\+7\d{10}$'
    )
    booking_date: date = Field(
        title='Дата бронирования',
        description='Не в прошлом и не дальше чем через 30 дней.'
    )
    booking_time: int = Field(
        title='Время бронирования',
        description='Только целые часы с 12 до 22.',
        ge=12,
        le=22
    )
    guests: int = Field(title='Всего гостей.', ge=1, le=10)

class BookingStore(BookingCreate):
    status: Literal['active', 'cancelled'] = Field(title='Статус бронирования («активно», либо «отменено»).')

class BookingOut(BookingStore):
    id: UUID = Field(title='Номер бронирования.')

class ErrorMessage(BaseModel):
    message: str

bna_error_message: str = 'Не удалось забронировать стол на '\
    'эти дату и время, так как он уже забронирован. '\
    'Если бронирование ваше и вы хотите изменить его, '\
    'то отмените (`DELETE /api/bookings/{id}`) и повторите бронирование с новыми данными.'
bne_error_message: str = 'Бронирование с этим идентификатором не было найдено.'