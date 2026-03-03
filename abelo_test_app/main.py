from fastapi import FastAPI
from setup import lifespan

app = FastAPI(lifespan=lifespan)
