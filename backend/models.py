from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
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


class Permissions(Base):
    __tablename__ = 'permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='permissions_pkey'),
        UniqueConstraint('name', name='permissions_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    role: Mapped[List['Roles']] = relationship('Roles', secondary='role_permissions', back_populates='permission')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('name', name='roles_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    permission: Mapped[List['Permissions']] = relationship('Permissions', secondary='role_permissions', back_populates='role')
    users: Mapped[List['Users']] = relationship('Users', back_populates='role')


class Scooter(Base):
    __tablename__ = 'scooter'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='scooter_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(Text)
    frame: Mapped[str] = mapped_column(String(255))
    battery: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))
    connection_status: Mapped[str] = mapped_column(String(50))
    last_action_id: Mapped[Optional[int]] = mapped_column(Integer)

    rentals: Mapped[List['Rentals']] = relationship('Rentals', back_populates='scooter')


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


t_role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, primary_key=True, nullable=False),
    Column('permission_id', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE', name='role_permissions_permission_id_fkey'),
    ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE', name='role_permissions_role_id_fkey'),
    PrimaryKeyConstraint('role_id', 'permission_id', name='role_permissions_pkey')
)


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
    hashed_password: Mapped[Optional[str]] = mapped_column(String(256))
    username: Mapped[Optional[str]] = mapped_column(String(256))
    disabled: Mapped[Optional[Boolean]] = Column(Boolean, default=False)

    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
    rentals: Mapped[List['Rentals']] = relationship('Rentals', back_populates='user')
    user_sessions: Mapped[List['UserSessions']] = relationship('UserSessions', back_populates='user')


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

    scooter: Mapped['Scooter'] = relationship('Scooter', back_populates='rentals')
    tariff: Mapped['Tariffs'] = relationship('Tariffs', back_populates='rentals')
    user: Mapped['Users'] = relationship('Users', back_populates='rentals')
    payments: Mapped[List['Payments']] = relationship('Payments', back_populates='rental')


class UserSessions(Base):
    __tablename__ = 'user_sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_sessions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    jwt_token: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped['Users'] = relationship('Users', back_populates='user_sessions')


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
