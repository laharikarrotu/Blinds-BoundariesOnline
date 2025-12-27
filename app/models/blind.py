"""Blind data models."""
from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum


class BlindType(str, Enum):
    """Blind type enumeration."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    ROLLER = "roller"
    ROMAN = "roman"


class Material(str, Enum):
    """Material type enumeration."""
    FABRIC = "fabric"
    WOOD = "wood"
    METAL = "metal"
    PLASTIC = "plastic"


@dataclass(frozen=True)
class BlindData:
    """Immutable blind data structure."""
    mode: Literal['texture', 'generated']
    color: str
    blind_name: Optional[str] = None
    blind_type: Optional[BlindType] = None
    material: Material = Material.FABRIC
    
    def __post_init__(self):
        """Validate blind data."""
        if self.mode == 'texture' and not self.blind_name:
            raise ValueError("blind_name is required for texture mode")
        if self.mode == 'generated' and not self.blind_type:
            raise ValueError("blind_type is required for generated mode")
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'mode': self.mode,
            'color': self.color,
            'blind_name': self.blind_name,
            'blind_type': self.blind_type.value if self.blind_type else None,
            'material': self.material.value
        }

