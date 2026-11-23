import datetime
from uuid import UUID


class BookingNotAvailableException(Exception):
    def __init__(self, date: datetime.date, time: int):
        self.__date: datetime.date = date
        self.__time: int = time

    def __str__(self) -> str:
        return f'Не удалось забронировать стол на дату {self.__date} и время {self.__time}:00. '\
        'На эти дату и время уже есть бронирование. '\
        'Если бронирование ваше и вы хотите изменить его, то отмените и повторите бронирование с новыми данными.'

class BookingNotExistException(Exception):
    def __init__(self, booking_id: UUID):
        self.__booking_id: UUID = booking_id

    def __str__(self) -> str:
        return f'Бронирование с идентификатором {self.__booking_id} не было найдено.'

class ValidationException(Exception):
    def __init__(self, message: str):
        self.__message: str = message

    def __str__(self) -> str:
        return self.__message