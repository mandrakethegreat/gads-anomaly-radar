from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Date, DateTime, func

class Base(DeclarativeBase):
    pass

class MetricsDaily(Base):
    __tablename__ = "metrics_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    customer_id: Mapped[str] = mapped_column(String(20), index=True)
    campaign_id: Mapped[str] = mapped_column(String(20), index=True)
    ad_group_id: Mapped[str] = mapped_column(String(20), index=True)

    clicks: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)  # in micros or currency units (mock uses currency)
    conversions: Mapped[float] = mapped_column(Float, default=0.0)
    conv_value: Mapped[float] = mapped_column(Float, default=0.0)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(20))  # 'campaign' or 'ad_group'
    entity_id: Mapped[str] = mapped_column(String(32), index=True)
    metric: Mapped[str] = mapped_column(String(20))       # 'cost', 'ctr', 'cvr', etc.
    direction: Mapped[str] = mapped_column(String(5))     # 'up' or 'down'
    zscore: Mapped[float] = mapped_column(Float)
    observed: Mapped[float] = mapped_column(Float)
    expected: Mapped[float] = mapped_column(Float)
    window_start: Mapped[Date] = mapped_column(Date)
    window_end: Mapped[Date] = mapped_column(Date)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
