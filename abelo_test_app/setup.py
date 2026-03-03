from contextlib import contextmanager

from fastapi import FastAPI


@contextmanager
async def lifespan(main_app: FastAPI):
    pass
