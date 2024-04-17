from datetime import UTC, datetime
from logging import getLogger
from uuid import uuid4

from geoalchemy2 import Geometry, load_spatialite
from geoalchemy2.shape import to_shape
from shapely import from_geojson, to_wkt
from sqlalchemy import Column, DateTime, Float, String, create_engine, func
from sqlalchemy.event import listen
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from stat_fastapi.models.constraints import Constraints
from stat_fastapi.models.order import Order

from .models import OffNadirRange, ValidatedOpportunitySearch

logger = getLogger(__name__)

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(UTC)


class OrderEntity(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True)
    product_id = Column(String, nullable=False)
    geom = Column(Geometry(srid=4326), nullable=False)
    dt_start = Column(DateTime(True), nullable=False)
    dt_end = Column(DateTime(True), nullable=False)
    off_nadir_min = Column(Float, nullable=False)
    off_nadir_max = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(True), nullable=False, default=func.now(), onupdate=func.now()
    )

    @classmethod
    def from_search(cls, search: ValidatedOpportunitySearch) -> "OrderEntity":
        order_id = str(uuid4())
        geom = from_geojson(search.geometry.model_dump_json(by_alias=True))
        return OrderEntity(
            id=order_id,
            product_id=search.product_id,
            geom=f"SRID=4326;{to_wkt(geom)}",
            dt_start=search.datetime[0],
            dt_end=search.datetime[1],
            off_nadir_min=search.constraints.off_nadir.minimum,
            off_nadir_max=search.constraints.off_nadir.maximum,
            status="pending",
        )

    def to_feature(self) -> Order:
        # SQLite drops TZ, patching back with UTC ¯\_(ツ)_/¯
        return Order(
            geometry=to_shape(self.geom),
            properties=Constraints(
                datetime=(
                    self.dt_start.replace(tzinfo=UTC),
                    self.dt_end.replace(tzinfo=UTC),
                ),
                off_nadir=OffNadirRange(
                    minimum=self.off_nadir_min,
                    maximum=self.off_nadir_max,
                ),
                status=self.status,
                created_at=self.created_at.replace(tzinfo=UTC),
                updated_at=self.updated_at.replace(tzinfo=UTC),
            ),
            id=self.id,
            product_id=self.product_id,
            links=[],
        )


class Repository:
    sessionmaker: sessionmaker[Session]
    session: Session | None = None

    def __init__(self, database_url: str) -> None:
        logger.info(f"using database {database_url}")
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        listen(engine, "connect", self._init_spatialite)
        Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _init_spatialite(self, *args, **kwargs):
        logger.info("initialising Spatialite...")
        load_spatialite(
            *args, init_mode="WGS84", transaction=True, journal_mode="OFF", **kwargs
        )
        logger.debug("initialised Spatialite")

    def __enter__(self) -> Session:
        self.session = self.sessionmaker()
        return self.session

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.session.close()

    def add_order(self, search: ValidatedOpportunitySearch) -> Order:
        entity = OrderEntity.from_search(search)
        with self as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)

        return entity.to_feature()

    def get_order(self, order_id: str) -> Order | None:
        with self as session:
            entity = (
                session.query(OrderEntity).filter(OrderEntity.id == order_id).first()
            )
        if entity is None:
            return None

        return entity.to_feature()
