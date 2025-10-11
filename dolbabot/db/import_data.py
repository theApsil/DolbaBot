from db.models import RegionIndex
from db.database import db_manager
import pandas as pd
from utils.logger import logger


def get_from_file(path: str) -> list[RegionIndex]:
    lst = list()
    with open(path, 'rb') as file:
        df = pd.read_excel(file)

    for _, row in df.iterrows():
        region_index = RegionIndex(
            city=row['city'],
            index=row['index']
        )
        lst.append(region_index)

    return lst

def import_data(path: str) -> None:
    lst = get_from_file(path)
    db_manager.init_database()

    try:
        session = db_manager.get_session()
        session.add_all(lst)
        session.commit()
        logger.info(f'Successfully imported {len(lst)} regions from {path}')
    except Exception as e:
        logger.error(f'Failed to import {path}: {e}')

if __name__ == '__main__':

    import_data('static/table.xlsx')
