from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import torch
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class LLM:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLM, cls).__new__(cls)
            model_name = settings.llm_model_name
            logger.info(f"Loading LLM: {model_name}...")

            try:
                # Detect device
                device = 0 if torch.cuda.is_available() else -1
                logger.info(f"Using device: {'GPU' if device == 0 else 'CPU'}")

                # Initialize pipeline based on model type
                if "t5" in model_name:
                    cls._pipeline = pipeline(
                        "text2text-generation",
                        model=model_name,
                        device=device,
                        max_length=512
                    )
                else:
                    # For Mistral/Llama etc.
                    cls._pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        device=device,
                        max_new_tokens=512
                    )
                
                logger.info("LLM loaded successfully.")

            except Exception as e:
                logger.error(f"Failed to load LLM: {e}")
                raise e

        return cls._instance

    def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        try:
            if self._pipeline.task == "text2text-generation":
                # T5 style
                result = self._pipeline(prompt)
                return result[0]['generated_text']
            else:
                # Causal LM style
                result = self._pipeline(prompt, return_full_text=False)
                return result[0]['generated_text']
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "Error generating response."
