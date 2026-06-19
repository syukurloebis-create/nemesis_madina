from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[http://localhost:5173, http://localhost:3000, http://localhost:8000],
        allow_credentials=True,
        allow_methods=[*],
        allow_headers=[*],
    )
