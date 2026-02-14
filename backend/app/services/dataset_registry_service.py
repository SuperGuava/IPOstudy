from sqlalchemy.orm import Session

from app.connectors.krx_connector import KrxConnector
from app.models.snapshot import DatasetRegistry


class DatasetRegistryService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_dataset(self, dataset_key: str) -> DatasetRegistry:
        row = self.session.get(DatasetRegistry, dataset_key)
        if row is None:
            msg = f"dataset not found: {dataset_key}"
            raise KeyError(msg)
        return row

    def fetch_dataset(
        self,
        dataset_key: str,
        params: dict[str, str],
        connector: KrxConnector,
    ) -> dict:
        row = self.get_dataset(dataset_key)
        return connector.fetch_dataset(row.bld, params)
