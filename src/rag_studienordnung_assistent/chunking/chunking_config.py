from dataclasses import dataclass, field
from typing import List


@dataclass
class ChunkingConfig:
    """
    Zentrale Konfiguration für das Text-Chunking-System.
    Diese Klasse enthält alle Parameters die das Chunking-Verhalten steuern.
    """
    max_chunk_length: int = 1800
    max_table_chunk_length: int = 5000

    # TABELLEN-ERKENNUNG
    table_block_line_limit: int = 12
    table_detection_threshold: int = 2

    # SEMESTER-ERKENNUNG
    semester_marker_threshold: int = 2

    # ANHANG-ERKENNUNG
    appendix_marker_threshold: int = 2

    # DOKUMENTTYP-STRATEGIE REIHENFOLGE
    strategy_order: dict = field(default_factory=lambda: {
        "studienordnung": [
            "semester",
            "appendix",
            "table",
            "length",
        ],
        "modulhandbuch": [
            "section",
            "appendix",
            "table",
            "length",
        ],
    })

    # PREPROCESSING
    normalize_multiple_newlines_threshold: int = 3

    # FRONT-MATTER
    remove_front_matter: bool = True

    # DEBUGGING UND LOGGING
    verbose: bool = False
    log_strategy_decisions: bool = False

    # VALIDIERUNG UND DEFAULTS
    def __post_init__(self):
        if self.max_chunk_length <= 0:
            raise ValueError(f"max_chunk_length muss > 0 sein, got {self.max_chunk_length}")

        if self.max_table_chunk_length <= 0:
            raise ValueError(f"max_table_chunk_length muss > 0 sein, got {self.max_table_chunk_length}")

        if self.max_table_chunk_length <= self.max_chunk_length:
            import warnings
            warnings.warn(
                f"max_table_chunk_length ({self.max_table_chunk_length}) sollte > max_chunk_length ({self.max_chunk_length}) sein. "
                f"Tabellen-Chunks können sonst nicht größer als normale Chunks sein!"
            )

        if self.table_block_line_limit <= 0:
            raise ValueError(f"table_block_line_limit muss > 0 sein, got {self.table_block_line_limit}")

        valid_strategies = {"semester", "appendix", "table", "section", "length"}
        for doc_type, strategies in self.strategy_order.items():
            for strategy in strategies:
                if strategy not in valid_strategies:
                    raise ValueError(
                        f"Unbekannte Strategie '{strategy}' für '{doc_type}'. "
                        f"Gültig sind: {valid_strategies}"
                    )


# Standard-Konfiguration (gut für die meisten Fälle)
DEFAULT_CONFIG = ChunkingConfig()

# Aggressive Konfiguration (kleinere Chunks, bessere Retrieval-Genauigkeit)
AGGRESSIVE_CONFIG = ChunkingConfig(
    max_chunk_length=1200,
    max_table_chunk_length=2000,
    table_block_line_limit=8,
)

# Conservative Konfiguration (größere Chunks, bessere Kontextualität)
CONSERVATIVE_CONFIG = ChunkingConfig(
    max_chunk_length=2500,
    max_table_chunk_length=4000,
    table_block_line_limit=15,
)

# HILFSFUNKTIONEN

def get_config(config_name: str = "default") -> ChunkingConfig:
    configs = {
        "default": DEFAULT_CONFIG,
        "aggressive": AGGRESSIVE_CONFIG,
        "conservative": CONSERVATIVE_CONFIG,
    }

    if config_name not in configs:
        raise ValueError(
            f"Unbekannte Konfiguration '{config_name}'. "
            f"Gültig sind: {list(configs.keys())}"
        )

    return configs[config_name]

