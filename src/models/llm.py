import os
from langchain.chat_models import init_chat_model

# --- Robust GenAI Error Handling Patch ---
# Catch 500 and 504 Internal Errors from Google API which aren't natively retried
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt

_original_generate = ChatGoogleGenerativeAI._generate
_original_stream = ChatGoogleGenerativeAI._stream

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(5)
)
def _robust_generate(self, *args, **kwargs):
    return _original_generate(self, *args, **kwargs)

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(5)
)
def _robust_stream(self, *args, **kwargs):
    return _original_stream(self, *args, **kwargs)

ChatGoogleGenerativeAI._generate = _robust_generate
ChatGoogleGenerativeAI._stream = _robust_stream
# -----------------------------------------

def get_gemma_model(
    temperature: float = 0.3,
    max_retries: int = 3,
    timeout: int = 180,
):
    """
    Returns the configured Gemma model with production-grade resilience.

    max_retries=12 handles the 15 req/min Google GenAI free tier by
    retrying with exponential backoff when rate-limited, rather than
    sleeping blindly before every call.

    timeout=180 accounts for Gemma's slower inference vs frontier models.
    """
    return init_chat_model(
        model=os.getenv("GOOGLE_MODEL", "gemma-4-31b"),
        model_provider="google_genai",
        temperature=temperature,
        max_retries=max_retries,
        timeout=timeout,
        # Reduced max_tokens to 4096 to help prevent Google API 504 Deadline Exceeded errors
        max_tokens=4096,
    )


def get_fast_model():
    """
    Lighter model for simple classification tasks (e.g. trip parameter extraction).
    Uses a smaller context to stay within free-tier limits.
    """
    return init_chat_model(
        model=os.getenv("GOOGLE_FAST_MODEL", "gemma-3-12b"),
        model_provider="google_genai",
        temperature=0.1,
        max_retries=3,
        timeout=180,
        max_tokens=1024,
    )
