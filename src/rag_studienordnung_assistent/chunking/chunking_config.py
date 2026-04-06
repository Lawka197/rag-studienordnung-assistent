"""
Zentrale Konfiguration für das Chunking-System.

Diese Datei enthält alle konfigurierbaren Parameter für Text-Preprocessing und -Chunking.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ChunkingConfig:
    """
    Zentrale Konfiguration für das Text-Chunking-System.

    Diese Klasse enthält alle Parameters die das Chunking-Verhalten steuern.
    """

    # CHUNK-GRÖSSEN KONFIGURATION

    max_chunk_length: int = 1800
    max_table_chunk_length: int = 3200

    # TABELLEN-ERKENNUNG KONFIGURATION

    table_block_line_limit: int = 12
    table_detection_threshold: int = 3

    # SEMESTER-ERKENNUNG KONFIGURATION

    semester_marker_threshold: int = 2

    # ANHANG-ERKENNUNG KONFIGURATION

    appendix_marker_threshold: int = 2

    # DOKUMENTTYP-STRATEGIE REIHENFOLGE

    strategy_order: dict = field(default_factory=lambda: {
        "studienordnung": [
            "semester",      # 1. Versuche nach Semestern zu teilen
            "appendix",      # 2. Versuche nach Anhängen zu teilen
            "table",         # 3. Versuche Tabellen zu erkennen
            "length",        # 4. Fallback: Nach Länge teilen
        ],
        "modulhandbuch": [
            "section",       # 1. Versuche nach Abschnitten zu teilen
            "appendix",      # 2. Versuche nach Anhängen zu teilen
            "table",         # 3. Versuche Tabellen zu erkennen
            "length",        # 4. Fallback: Nach Länge teilen
        ],
    })

    # PREPROCESSING KONFIGURATION

    normalize_multiple_newlines_threshold: int = 3

    # FRONT-MATTER KONFIGURATION

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

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ChunkingConfig":
        """
        Erstellt ChunkingConfig aus einem Dictionary.

        Nützlich um Config aus JSON/YAML zu laden.
        """
        return cls(**config_dict)

    def to_dict(self) -> dict:
        """
        Konvertiert ChunkingConfig zu Dictionary.

        Nützlich um Config zu JSON/YAML zu speichern.
        """
        return {
            "max_chunk_length": self.max_chunk_length,
            "max_table_chunk_length": self.max_table_chunk_length,
            "table_block_line_limit": self.table_block_line_limit,
            "table_detection_threshold": self.table_detection_threshold,
            "semester_marker_threshold": self.semester_marker_threshold,
            "appendix_marker_threshold": self.appendix_marker_threshold,
            "strategy_order": self.strategy_order,
            "normalize_multiple_newlines_threshold": self.normalize_multiple_newlines_threshold,
            "remove_front_matter": self.remove_front_matter,
            "verbose": self.verbose,
            "log_strategy_decisions": self.log_strategy_decisions,
        }

#DEFAULT KONFIGURATIONEN

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

# Performance-optimierte Konfiguration (schneller, aber eventuell weniger genau)
PERFORMANCE_CONFIG = ChunkingConfig(
    max_chunk_length=2000,
    table_block_line_limit=20,
    verbose=False,
    log_strategy_decisions=False,
)

# Debug-Konfiguration (viel Logging, hilft beim Verstehen)
DEBUG_CONFIG = ChunkingConfig(
    max_chunk_length=1800,
    verbose=True,
    log_strategy_decisions=True,
)

# HILFSFUNKTIONEN

def get_config(config_name: str = "default") -> ChunkingConfig:
    """
    Holt vordefinierte Konfiguration nach Name.
    """
    configs = {
        "default": DEFAULT_CONFIG,
        "aggressive": AGGRESSIVE_CONFIG,
        "conservative": CONSERVATIVE_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "debug": DEBUG_CONFIG,
    }

    if config_name not in configs:
        raise ValueError(
            f"Unbekannte Konfiguration '{config_name}'. "
            f"Gültig sind: {list(configs.keys())}"
        )

    return configs[config_name]


def print_config_comparison():
    """
    Druckt Vergleich aller vordefinierter Konfigurationen.

    Hilft um die richtige Konfiguration zu wählen.
    """
    configs = {
        "Default": DEFAULT_CONFIG,
        "Aggressive": AGGRESSIVE_CONFIG,
        "Conservative": CONSERVATIVE_CONFIG,
        "Performance": PERFORMANCE_CONFIG,
        "Debug": DEBUG_CONFIG,
    }

    print("\n" + "="*80)
    print("VERGLEICH VORDEFINIERTER KONFIGURATIONEN")
    print("="*80)

    print(f"\n{'Config':<15} | {'Max Chunk':<12} | {'Max Table':<12} | {'Verbose':<10}")
    print("-" * 60)

    for name, config in configs.items():
        print(f"{name:<15} | {config.max_chunk_length:<12} | {config.max_table_chunk_length:<12} | {str(config.verbose):<10}")

    print("\n" + "="*80)

