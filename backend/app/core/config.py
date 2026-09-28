import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

_DEFAULT_CHECKPOINT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "model", "checkpoints", "best_model.pth")
)
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", _DEFAULT_CHECKPOINT)