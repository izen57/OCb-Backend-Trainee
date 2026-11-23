import datetime as dt
from uuid import UUID

from sqlmodel import SQLModel, Session, create_engine, select

from exceptions import BookingNotAvailableException, BookingNotExistException, ValidationException
from models import BookingCreate, BookingStatus, BookingStore


class BookingsService():
    def __init__(self, sqlite_url: str):
        self.__sqlite_url = sqlite_url
        self.__engine = create_engine(self.__sqlite_url, connect_args={'check_same_thread': False})
        SQLModel.metadata.create_all(self.__engine)

    def __is_available(self, session: Session, date: dt.date, time: int) -> bool:
        return session.exec(
            select(BookingStore.id)
            .where(BookingStore.booking_date == date,
                BookingStore.booking_time == time,
                BookingStore.status == 'active'
            )
            .limit(1)
        ).first() is None

    def create_booking(self, booking: BookingCreate) -> BookingStore:
        if booking.booking_date < dt.date.today()\
        or booking.booking_date - dt.date.today() > dt.timedelta(30):
            raise ValidationException('Нельзя забронировать стол на прошедшую дату и больше чем на 30 дней вперёд.')
 
        with Session(self.__engine) as session:
            if not self.__is_available(session, booking.booking_date, booking.booking_time):
                raise BookingNotAvailableException(booking.booking_date, booking.booking_time)

            booking = BookingStore(**dict(booking), status=BookingStatus.ACTIVE)
            session.add(booking)
            session.commit()
            session.refresh(booking)
            return booking

    def cancel_booking(self, id: UUID) -> BookingStore:
        with Session(self.__engine) as session: 
            booking: BookingStore | None = session.get(BookingStore, id)
            if booking is None: raise BookingNotExistException(id)

            booking.status = BookingStatus.CANCELLED
            session.add(booking)
            session.commit()
            session.refresh(booking)
            return session.get_one(BookingStore, id)

    def search_booking(self, id: UUID) -> BookingStore:
        with Session(self.__engine) as session:
            booking: BookingStore | None = session.get(BookingStore, id)
            if booking is None: raise BookingNotExistException(id)
            return booking

    def list_bookings(self, date: dt.date | None) -> list[BookingStore]:
        with Session(self.__engine) as session: 
            return list(session.exec(select(BookingStore)).all())\
            if date is None\
            else list(session.exec(
                select(BookingStore)
                .where(BookingStore.booking_date == date)
            ))
