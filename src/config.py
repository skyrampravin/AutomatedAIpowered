"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot Configuration"""

    PORT = 3978
    APP_ID = os.environ.get("BOT_ID", "")
    APP_PASSWORD = os.environ.get("BOT_PASSWORD", "")
    APP_TYPE = os.environ.get("BOT_TYPE", "")
    APP_TENANTID = os.environ.get("BOT_TENANT_ID", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # OpenAI API key (may be empty; validated later)
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")  # Allow override via env

    @staticmethod
    def validate_environment():
        """Extended environment validation & sandbox guard messages."""
        env = os.environ.get("ENVIRONMENT", "") or os.environ.get("TEAMSFX_ENV", "")
        missing = []
        for var in ["BOT_ID", "BOT_PASSWORD", "OPENAI_API_KEY"]:
            if not os.environ.get(var):
                missing.append(var)
        if missing:
            print(f"[WARN] Missing required environment variables: {', '.join(missing)}")

        # Model validation
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        if not model:
            print("[WARN] OPENAI_MODEL not set; defaulting to gpt-3.5-turbo")
        elif model.lower().startswith("gpt-4") and env.lower() == "playground":
            print("[INFO] Using a GPT-4 class model in playground; ensure rate limits are acceptable.")

        # Storage type validation
        storage_type = os.environ.get("STORAGE_TYPE", "file").lower()
        supported = {"file", "azure_table", "cosmos"}
        if storage_type not in supported:
            print(f"[WARN] STORAGE_TYPE '{storage_type}' not recognized. Supported: {', '.join(supported)}. Defaulting to 'file'.")

        # Quiz question sanity
        qpd = os.environ.get("QUIZ_QUESTIONS_PER_DAY")
        if qpd:
            try:
                qpd_val = int(qpd)
                if qpd_val <= 0:
                    print("[WARN] QUIZ_QUESTIONS_PER_DAY should be > 0; ignoring invalid value.")
                elif qpd_val > 50:
                    print("[INFO] High QUIZ_QUESTIONS_PER_DAY value; consider reducing for user experience.")
            except ValueError:
                print("[WARN] QUIZ_QUESTIONS_PER_DAY must be an integer.")

        # Azure OpenAI pairing
        if os.environ.get("AZURE_OPENAI_ENDPOINT") and not os.environ.get("AZURE_OPENAI_DEPLOYMENT"):
            print("[WARN] AZURE_OPENAI_ENDPOINT set but AZURE_OPENAI_DEPLOYMENT missing.")

        # Sandbox hints
        if env.lower() == "playground":
            if os.environ.get("BOT_ID", "").startswith("00000000"):
                print("[WARN] BOT_ID appears placeholder; update with sandbox App ID.")
        if env.lower() == "production" and ".onmicrosoft" in os.environ.get("BOT_ID", ""):
            print("[INFO] Running production mode with what looks like a sandbox App ID—confirm this is intentional.")

# Execute validation on import
Config.validate_environment()
