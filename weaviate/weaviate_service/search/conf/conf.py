from os import getenv
from pathlib import Path
from dotenv import load_dotenv


dir_ = Path(__file__).resolve().parent
param_path = Path(__file__).resolve().parent.joinpath("configuration.env")
load_dotenv(param_path)

Weaviate_HOST = getenv("Weaviate_HOST", default=None)