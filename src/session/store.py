import os

def get_checkpointer():
    """
    Returns the appropriate checkpointer based on environment.

    Development: MemorySaver (in-memory, lost on restart)
    Production: SqliteSaver or PostgresSaver (persistent across restarts)
    """
    env = os.getenv("APP_ENV", "development")

    if env == "production":
        # Uncomment and install langgraph-checkpoint-postgres
        # from langgraph.checkpoint.postgres import PostgresSaver
        # return PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])

        # Or SQLite for single-machine production
        from langgraph.checkpoint.sqlite import SqliteSaver
        db_path = os.getenv("CHECKPOINT_DB", "./data/sessions.db")
        return SqliteSaver.from_conn_string(db_path)
    else:
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()
