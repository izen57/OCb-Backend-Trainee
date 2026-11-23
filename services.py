import datetime as dt
from uuid import UUID, uuid4

from exceptions import BookingNotAvailableException, BookingNotExistException, ValidationException
from models import BookingCreate, BookingOut, BookingStore


class BookingsServiceDict():
    def __init__(self):
        self.__repository: dict[UUID, BookingStore] = {}
        self.__id_generator = uuid4

    def __is_available(self, date: dt.date, time: int) -> bool:
        for booking in self.__repository.values():
            if booking.booking_date == date and booking.booking_time == time and booking.status == 'active':
                return False
        return True

    def create_booking(self, booking: BookingCreate) -> BookingOut:
        if booking.booking_date < dt.date.today()\
        or booking.booking_date - dt.date.today() > dt.timedelta(30):
            raise ValidationException('Нельзя забронировать стол на прошедшую дату и больше чем на 30 дней вперёд.')
        if not self.__is_available(booking.booking_date, booking.booking_time):
            raise BookingNotAvailableException(booking.booking_date, booking.booking_time)

        id: UUID = self.__id_generator()
        self.__repository[id] = BookingStore(**dict(booking), status='active')
        return BookingOut(id=id, **dict(self.__repository[id]))

    def cancel_booking(self, id: UUID) -> BookingOut:
        booking: BookingStore | None = self.__repository.get(id)
        if booking is None: raise BookingNotExistException(id)

        booking.status = 'cancelled'
        return BookingOut(id=id, **dict(booking))

    def search_booking(self, id: UUID) -> BookingOut:
        booking: BookingStore | None = self.__repository.get(id)
        if booking is None: raise BookingNotExistException(id)
        return BookingOut(id=id, **dict(booking))

    def list_bookings(self, date: dt.date | None) -> list[BookingOut]:
        result: list[BookingOut] = []

        if date is None:
            for id, booking in self.__repository.items():
                result.append(BookingOut(id=id, **dict(booking)))
        else:
            for id, booking in self.__repository.items():
                if booking.booking_date == date:
                    result.append(BookingOut(id=id, **dict(booking)))

        return result