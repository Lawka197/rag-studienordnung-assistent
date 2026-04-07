import logging
import requests

logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self, model: str = "neural-chat", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/api/generate"

        logger.info(f"Initialized Ollama LLM (model={model})")
        self._test_connection()

    def _test_connection(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama ist erreichbar")
            else:
                logger.warning("Ollama antwortet aber Status != 200")
        except Exception as e:
            logger.warning(
                f"Ollama nicht erreichbar auf {self.base_url}. "
                f"Starte mit: ollama serve"
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: str = None,
    ) -> str:
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        logger.debug(f"Generating with Ollama (model={self.model})...")

        try:
            response = requests.post(
                self.chat_endpoint,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            result = response.json()
            answer = result.get("response", "").strip()

            logger.debug(f"Generated {len(answer)} characters")

            return answer

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Ollama nicht erreichbar auf {self.base_url}. "
                f"Starte mit: ollama serve"
            )
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise

    def answer_question(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
    ) -> str:
        system_prompt = (
            "Du bist ein hilfreicher Assistent für Studien-Fragen. "
            "Antworte basierend auf dem gegebenen Kontext. "
            "Wenn die Antwort nicht im Kontext steht, sage das klar."
        )

        prompt = f"""Kontext:
{context}

Frage: {question}

Antwort:"""

        return self.generate(prompt, temperature=temperature, system_prompt=system_prompt)


