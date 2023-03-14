import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class SerialRecord(BaseModel):
    title: str
    description: str
    year: str
    rating: float
    episode_length: str
    genres: set[str]

    @staticmethod
    def from_dict(data: dict):
        genres = set(data.pop('genres', []))
        record = SerialRecord(genres=genres, **data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "rb") as f:
            d = f.read()
            data = orjson.loads(d.decode("utf-8"))
            print(data)
            for record in data:
                obj = SerialRecord.from_dict(record)
                self._data.append(obj)

    def delete(self, id_serial: int):
        if 0 < id_serial >= len(self._data):
            return
        self._data.pop(id_serial)

    def add(self, serial: SerialRecord):
        self._data.append(serial)

    def get(self, id_serial: int):
        if 0 < id_serial >= len(self._data):
            return
        return self._data[id_serial]

    def get_all(self) -> list[SerialRecord]:
        return self._data

    def update(self, id_serial: int, serial: SerialRecord):
        if 0 < id_serial >= len(self._data):
            return
        self._data[id_serial] = serial

    def count(self) -> int:
        return len(self._data)


db = Database()
db.load_from_filename('serials.json')

app = FastAPI(title="Serial API", version="0.1", docs_url="/docs")

app.is_shutdown = False


@app.get("/serials", response_model=list[SerialRecord], description="Vrátí seznam seriálů")
async def get_serials():
    return db.get_all()


@app.get("/serials/{id_serial}", response_model=SerialRecord)
async def get_serial(id_serial: int):
    return db.get(id_serial)


@app.post("/serials", response_model=SerialRecord, description="Přidáme seriál do DB")
async def post_serials(serial: SerialRecord):
    db.add(serial)
    return serial


@app.delete("/serials/{id_serial}", description="Sprovodíme seriál ze světa", responses={
    404: {'model': Problem}
})
async def delete_serial(id_serial: int):
    serial = db.get(id_serial)
    if serial is None:
        raise HTTPException(404, "Serial neexistuje")
    db.delete(id_serial)
    return {'status': 'smazano'}


@app.patch("/serials/{id_serial}", description="Aktualizujeme serial do DB", responses={
    404: {'model': Problem}
})
async def update_serial(id_serial: int, updated_serial: SerialRecord):
    serial = db.get(id_serial)
    if serial is None:
        raise HTTPException(404, "Serial neexistuje")
    db.update(id_serial, updated_serial)
    return {'old': serial, 'new': updated_serial}