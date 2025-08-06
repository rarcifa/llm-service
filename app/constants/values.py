from pathlib import Path

USE_HTTP_API = True
OLLAMA_CLI = "ollama"
OLLAMA_CMD = "run"
CHROMA_COLLECTION_NAME = "agent_docs"
EMBEDDING_PATH = "./chroma_db"
FEEDBACK_PATH = "feedback/feedback.jsonl"
ENCODING = "utf-8"
PROMPT_DIR = Path("prompts")
REQUIRED_KEYS = {"name", "system_prompt", "prompt_template"}
INPUT_FILE = Path(FEEDBACK_PATH)
OUTPUT_FILE = Path("data/fine_tune_data.jsonl")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
INJECTION_PATTERNS = [
    "(ignore|disregard)\\s+previous\\s+instructions",
    "(you are|pretend to be)\\s+a\\s+.*",
    "(delete|disable|shutdown).*",
    "(prompt|system):",
    "(simulate|emulate)\\s+.*",
]
PROFANITY_LIST = ["damn", "hell", "shit", "fuck"]
DOCS_PATH = "./data"
CHUNK_SIZE = 300
SUPPORTED_EXT = ["*.txt", "*.md"]
MANIFEST_PATH = Path("manifest.yaml")
PROMPT_DIR = "prompts"
