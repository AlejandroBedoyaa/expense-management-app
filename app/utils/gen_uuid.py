from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.types import TypeDecorator

class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type for SQLAlchemy."""
    impl = CHAR

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, str):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        return value
