from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class ActionTypes(Base):
    __tablename__ = 'action_types'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='action_types_pkey'),
        UniqueConstraint('name', name='action_types_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    last_action: Mapped[List['LastAction']] = relationship('LastAction', back_populates='action_type')


class LastAction(Base):
    __tablename__ = 'last_action'
    __table_args__ = (
        ForeignKeyConstraint(['action_type_id'], ['action_types.id'], ondelete='CASCADE', name='last_action_action_type_id_fkey'),
        ForeignKeyConstraint(['rental_id'], ['rentals.id'], ondelete='SET NULL', name='last_action_rental_id_fkey'),
        ForeignKeyConstraint(['scooter_id'], ['scooter.id'], ondelete='CASCADE', name='last_action_scooter_id_fkey'),
        PrimaryKeyConstraint('id', name='last_action_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_phone: Mapped[str] = mapped_column(String(20))
    scooter_id: Mapped[int] = mapped_column(Integer)
    action_type_id: Mapped[int] = mapped_column(Integer)
    rental_id: Mapped[Optional[int]] = mapped_column(Integer)
    action_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    action_type: Mapped['ActionTypes'] = relationship('ActionTypes', back_populates='last_action')
    rental: Mapped[Optional['Rentals']] = relationship('Rentals', back_populates='last_action')
    scooter: Mapped['Scooter'] = relationship('Scooter', foreign_keys=[scooter_id], back_populates='last_action')
    scooter_: Mapped[List['Scooter']] = relationship('Scooter', foreign_keys='[Scooter.last_action_id]', back_populates='last_action_')


class Questions(Base):
    __tablename__ = 'questions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='questions_pkey'),
        Index('ix_questions_id', 'id'),
        Index('ix_questions_question_text', 'question_text')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[Optional[str]] = mapped_column(String)

    choices: Mapped[List['Choices']] = relationship('Choices', back_populates='question')


class Rentals(Base):
    __tablename__ = 'rentals'
    __table_args__ = (
        ForeignKeyConstraint(['scooter_id'], ['scooter.id'], ondelete='CASCADE', name='rentals_scooter_id_fkey'),
        ForeignKeyConstraint(['tariff_id'], ['tariffs.id'], ondelete='CASCADE', name='rentals_tariff_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='rentals_user_id_fkey'),
        PrimaryKeyConstraint('id', name='rentals_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    scooter_id: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    start_location: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    tariff_id: Mapped[int] = mapped_column(Integer)
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    end_location: Mapped[Optional[str]] = mapped_column(Text)
    total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))

    last_action: Mapped[List['LastAction']] = relationship('LastAction', back_populates='rental')
    scooter: Mapped['Scooter'] = relationship('Scooter', back_populates='rentals')
    tariff: Mapped['Tariffs'] = relationship('Tariffs', back_populates='rentals')
    user: Mapped['Users'] = relationship('Users', back_populates='rentals')
    payments: Mapped[List['Payments']] = relationship('Payments', back_populates='rental')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('name', name='roles_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    users: Mapped[List['Users']] = relationship('Users', back_populates='role')


class Scooter(Base):
    __tablename__ = 'scooter'
    __table_args__ = (
        ForeignKeyConstraint(['last_action_id'], ['last_action.id'], ondelete='SET NULL', name='fk_last_action'),
        PrimaryKeyConstraint('id', name='scooter_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(Text)
    frame: Mapped[str] = mapped_column(String(255))
    battery: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))
    connection_status: Mapped[str] = mapped_column(String(50))
    last_action_id: Mapped[Optional[int]] = mapped_column(Integer)

    last_action: Mapped[List['LastAction']] = relationship('LastAction', foreign_keys='[LastAction.scooter_id]', back_populates='scooter')
    rentals: Mapped[List['Rentals']] = relationship('Rentals', back_populates='scooter')
    last_action_: Mapped[Optional['LastAction']] = relationship('LastAction', foreign_keys=[last_action_id], back_populates='scooter_')


class Tariffs(Base):
    __tablename__ = 'tariffs'
    __table_args__ = (
        CheckConstraint("cost_type::text = ANY (ARRAY['fixed'::character varying, 'per_minute'::character varying]::text[])", name='tariffs_cost_type_check'),
        PrimaryKeyConstraint('id', name='tariffs_pkey'),
        UniqueConstraint('name', name='tariffs_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    cost_type: Mapped[str] = mapped_column(String(50))
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))

    rentals: Mapped[List['Rentals']] = relationship('Rentals', back_populates='tariff')


class Choices(Base):
    __tablename__ = 'choices'
    __table_args__ = (
        ForeignKeyConstraint(['question_id'], ['questions.id'], name='choices_question_id_fkey'),
        PrimaryKeyConstraint('id', name='choices_pkey'),
        Index('ix_choices_choice_text', 'choice_text'),
        Index('ix_choices_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    choice_text: Mapped[Optional[str]] = mapped_column(String)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    question_id: Mapped[Optional[int]] = mapped_column(Integer)

    question: Mapped[Optional['Questions']] = relationship('Questions', back_populates='choices')


class Payments(Base):
    __tablename__ = 'payments'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'completed'::character varying, 'failed'::character varying]::text[])", name='payments_status_check'),
        ForeignKeyConstraint(['rental_id'], ['rentals.id'], ondelete='CASCADE', name='payments_rental_id_fkey'),
        PrimaryKeyConstraint('id', name='payments_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rental_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    payment_method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))

    rental: Mapped['Rentals'] = relationship('Rentals', back_populates='payments')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='RESTRICT', name='fk_role'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('phone', name='users_phone_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(20))
    role_id: Mapped[int] = mapped_column(Integer, server_default=text('3'))
    balance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2), server_default=text('0.00'))

    rentals: Mapped[List['Rentals']] = relationship('Rentals', back_populates='user')
    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
