#!/usr/bin/env python3
"""
Centralized Configuration System for Agentic Code Indexer
Provides unified configuration management across all components.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class Neo4jConfig:
    """Neo4j database configuration."""
    uri: str = "bolt://localhost:7688"
    username: str = "neo4j"
    password: str = "password"
    max_retries: int = 3
    timeout: int = 30


@dataclass
class LLMConfig:
    """LLM integration configuration."""
    provider: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"
    api_key: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = "jinaai/jina-embeddings-v2-base-code"
    max_length: int = 512
    batch_size: int = 32
    device: str = "auto"


@dataclass
class ProcessingConfig:
    """Processing pipeline configuration."""
    max_concurrent_files: int = 5
    batch_size: int = 1000
    chunk_size: int = 1000
    timeout: int = 300


@dataclass
class AgenticCodeIndexerConfig:
    """Main configuration class for Agentic Code Indexer."""
    
    # Component configurations
    neo4j: Neo4jConfig
    llm: LLMConfig
    embedding: EmbeddingConfig
    processing: ProcessingConfig
    
    # Project settings
    project_root: str = "."
    log_level: str = "INFO"
    verbose: bool = False
    
    def __init__(
        self,
        project_root: str = ".",
        neo4j_uri: Optional[str] = None,
        neo4j_username: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize configuration with environment variable support."""
        
        # Set project root
        self.project_root = str(Path(project_root).resolve())
        
        # Neo4j configuration
        self.neo4j = Neo4jConfig(
            uri=neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7688"),
            username=neo4j_username or os.getenv("NEO4J_USERNAME", "neo4j"),
            password=neo4j_password or os.getenv("NEO4J_PASSWORD", "password"),
            max_retries=int(os.getenv("NEO4J_MAX_RETRIES", "3")),
            timeout=int(os.getenv("NEO4J_TIMEOUT", "30"))
        )
        
        # LLM configuration
        self.llm = LLMConfig(
            provider=llm_provider or os.getenv("LLM_PROVIDER", "anthropic"),
            model=llm_model or os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022"),
            api_key=llm_api_key or os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            timeout=int(os.getenv("LLM_TIMEOUT", "60"))
        )
        
        # Embedding configuration
        self.embedding = EmbeddingConfig(
            model_name=os.getenv("EMBEDDING_MODEL", "jinaai/jina-embeddings-v2-base-code"),
            max_length=int(os.getenv("EMBEDDING_MAX_LENGTH", "512")),
            batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
            device=os.getenv("EMBEDDING_DEVICE", "auto")
        )
        
        # Processing configuration
        self.processing = ProcessingConfig(
            max_concurrent_files=int(os.getenv("MAX_CONCURRENT_FILES", "5")),
            batch_size=int(os.getenv("BATCH_SIZE", "1000")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            timeout=int(os.getenv("PROCESSING_TIMEOUT", "300"))
        )
        
        # General settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "project_root": self.project_root,
            "neo4j": {
                "uri": self.neo4j.uri,
                "username": self.neo4j.username,
                "password": "***" if self.neo4j.password else None,
                "max_retries": self.neo4j.max_retries,
                "timeout": self.neo4j.timeout
            },
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "api_key": "***" if self.llm.api_key else None,
                "max_tokens": self.llm.max_tokens,
                "temperature": self.llm.temperature,
                "timeout": self.llm.timeout
            },
            "embedding": {
                "model_name": self.embedding.model_name,
                "max_length": self.embedding.max_length,
                "batch_size": self.embedding.batch_size,
                "device": self.embedding.device
            },
            "processing": {
                "max_concurrent_files": self.processing.max_concurrent_files,
                "batch_size": self.processing.batch_size,
                "chunk_size": self.processing.chunk_size,
                "timeout": self.processing.timeout
            },
            "log_level": self.log_level,
            "verbose": self.verbose
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Validate Neo4j configuration
        if not self.neo4j.uri.startswith(("bolt://", "neo4j://")):
            errors.append("Neo4j URI must start with 'bolt://' or 'neo4j://'")
        
        if not self.neo4j.username:
            errors.append("Neo4j username is required")
        
        if not self.neo4j.password:
            errors.append("Neo4j password is required")
        
        # Validate LLM configuration
        if self.llm.provider == "anthropic" and not self.llm.api_key:
            errors.append("Anthropic API key is required for LLM provider 'anthropic'")
        
        if self.llm.max_tokens <= 0:
            errors.append("LLM max_tokens must be positive")
        
        if not 0 <= self.llm.temperature <= 2:
            errors.append("LLM temperature must be between 0 and 2")
        
        # Validate processing configuration
        if self.processing.max_concurrent_files <= 0:
            errors.append("max_concurrent_files must be positive")
        
        if self.processing.batch_size <= 0:
            errors.append("batch_size must be positive")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True


# Global configuration instance
_config: Optional[AgenticCodeIndexerConfig] = None


def get_config() -> AgenticCodeIndexerConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AgenticCodeIndexerConfig()
    return _config


def set_config(config: AgenticCodeIndexerConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None


# Environment variable helpers
def load_from_env() -> AgenticCodeIndexerConfig:
    """Load configuration from environment variables."""
    return AgenticCodeIndexerConfig()


def save_to_env(config: AgenticCodeIndexerConfig) -> None:
    """Save configuration to environment variables."""
    os.environ["NEO4J_URI"] = config.neo4j.uri
    os.environ["NEO4J_USERNAME"] = config.neo4j.username
    os.environ["NEO4J_PASSWORD"] = config.neo4j.password
    
    if config.llm.api_key:
        os.environ["ANTHROPIC_API_KEY"] = config.llm.api_key
    
    os.environ["LLM_PROVIDER"] = config.llm.provider
    os.environ["LLM_MODEL"] = config.llm.model
    os.environ["LOG_LEVEL"] = config.log_level
    os.environ["VERBOSE"] = str(config.verbose).lower()
