# LyricGetter

LyricGetter is a pet project of mine, written using FastAPI. The idea is to upload songs and lyrics will be pulled from Genius API.

## Installation

For local environment use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements/dev.txt
alembic revision --autogenerate
alembic upgrade head
```

For docker environment use these commands
```bash
sudo docker-compose up --build
```

## Usage

Check /docs for swagger UI and endpoints

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
