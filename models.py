from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from sqlmodel import Field as sqlField, SQLModel


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
    booking_date: date = sqlField(
        title='Дата бронирования',
        description='Не в прошлом и не дальше чем через 30 дней.',
        index=True
    )
    booking_time: int = Field(
        title='Время бронирования',
        description='Только целые часы с 12 до 22.',
        ge=12,
        le=22
    )
    guests: int = Field(title='Всего гостей.', ge=1, le=10)

class BookingStatus(StrEnum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'

class BookingStore(BookingCreate, SQLModel, table=True):
    id: UUID = sqlField(primary_key=True, title='Номер бронирования.', default_factory=uuid4)
    status: BookingStatus = Field(title='Статус бронирования («активно», либо «отменено»).')

class ErrorMessage(SQLModel):
    message: str

bna_error_message: str = 'Не удалось забронировать стол на '\
    'эти дату и время, так как он уже забронирован. '\
    'Если бронирование ваше и вы хотите изменить его, '\
    'то отмените (`DELETE /api/bookings/{id}`) и повторите бронирование с новыми данными.'
bne_error_message: str = 'Бронирование с этим идентификатором не было найдено.'