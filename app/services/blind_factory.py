"""Factory pattern for blind generators."""
from typing import Protocol
from PIL import Image
from app.models.blind import BlindData


class BlindGenerator(Protocol):
    """Protocol for blind generators."""
    def generate(self, width: int, height: int, blind_data: BlindData) -> Image.Image:
        """Generate blind image."""
        ...


class TextureBlindGenerator:
    """Generator for texture-based blinds."""
    
    def generate(self, width: int, height: int, blind_data: BlindData) -> Image.Image:
        """Generate texture-based blind."""
        from app.core.config import config
        from pathlib import Path
        import numpy as np
        
        blind_path = Path(config.BLINDS_DIR) / blind_data.blind_name
        if not blind_path.exists():
            raise ValueError(f"Blind texture {blind_data.blind_name} not found")
        
        blind_texture = Image.open(blind_path)
        blind_texture = blind_texture.resize((width, height), Image.LANCZOS)
        
        # Apply color tint
        if blind_data.color and blind_data.color != "#000000":
            color_rgb = tuple(int(blind_data.color[i:i+2], 16) for i in (1, 3, 5))
            tinted = blind_texture.copy().convert('RGBA')
            tinted_data = np.array(tinted)
            tinted_data[:, :, 0] = (tinted_data[:, :, 0] * color_rgb[0]) // 255
            tinted_data[:, :, 1] = (tinted_data[:, :, 1] * color_rgb[1]) // 255
            tinted_data[:, :, 2] = (tinted_data[:, :, 2] * color_rgb[2]) // 255
            blind_texture = Image.fromarray(tinted_data)
        
        return blind_texture


class GeneratedBlindGenerator:
    """Generator for algorithmically generated blinds."""
    
    def generate(self, width: int, height: int, blind_data: BlindData) -> Image.Image:
        """Generate algorithmically created blind."""
        try:
            # Try importing from app directory first
            try:
                from app.realistic_blind_generator import RealisticBlindGenerator
            except ImportError:
                # Fallback to root level import
                from realistic_blind_generator import RealisticBlindGenerator
            
            generator = RealisticBlindGenerator()
            
            return generator.create_realistic_blind(
                blind_type=blind_data.blind_type.value if blind_data.blind_type else "horizontal",
                color=blind_data.color,
                width=width,
                height=height,
                material=blind_data.material.value,
                depth_factor=0.8,
                shadow_intensity=0.3
            )
        except (ImportError, Exception) as e:
            raise ValueError(f"Realistic blind generator not available: {e}")


class BlindGeneratorFactory:
    """Factory for creating blind generators."""
    
    @staticmethod
    def create(blind_data: BlindData) -> BlindGenerator:
        """
        Create appropriate generator based on blind data.
        Strategy pattern implementation.
        
        Args:
            blind_data: Blind configuration
            
        Returns:
            Appropriate blind generator
        """
        if blind_data.mode == 'texture':
            return TextureBlindGenerator()
        else:
            return GeneratedBlindGenerator()

