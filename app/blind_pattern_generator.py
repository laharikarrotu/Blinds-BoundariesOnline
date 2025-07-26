import numpy as np
from PIL import Image, ImageDraw
import colorsys

class BlindPatternGenerator:
    """
    Generates custom blind patterns programmatically
    Supports: Horizontal, Vertical, Roller, Roman blinds
    """
    
    def __init__(self):
        self.patterns = {
            'horizontal': self.generate_horizontal_blinds,
            'vertical': self.generate_vertical_blinds,
            'roller': self.generate_roller_blind,
            'roman': self.generate_roman_blinds
        }
    
    def generate_blind_pattern(self, blind_type, color, width=320, height=320, material='fabric'):
        """
        Generate a blind pattern based on type, color, and material
        
        Args:
            blind_type: 'horizontal', 'vertical', 'roller', 'roman'
            color: hex color string (e.g., '#FF0000')
            width: pattern width
            height: pattern height
            material: 'fabric', 'wood', 'metal', 'plastic'
        
        Returns:
            PIL Image of the generated blind pattern
        """
        if blind_type not in self.patterns:
            raise ValueError(f"Unsupported blind type: {blind_type}")
        
        # Convert hex color to RGB
        rgb_color = self.hex_to_rgb(color)
        
        # Generate base pattern
        pattern = self.patterns[blind_type](width, height, rgb_color)
        
        # Apply material texture
        pattern = self.apply_material_texture(pattern, material)
        
        return pattern
    
    def generate_horizontal_blinds(self, width, height, color):
        """Generate horizontal blind slats"""
        # Create base image
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Slat dimensions
        slat_height = 8
        gap_height = 2
        total_height = slat_height + gap_height
        
        # Draw horizontal slats
        for y in range(0, height, total_height):
            # Draw slat
            draw.rectangle([0, y, width, y + slat_height], fill=color, outline=self.darken_color(color))
            
            # Add slat detail (3D effect)
            draw.line([0, y + slat_height//2, width, y + slat_height//2], 
                     fill=self.lighten_color(color), width=1)
        
        return img
    
    def generate_vertical_blinds(self, width, height, color):
        """Generate vertical blind slats"""
        # Create base image
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Slat dimensions
        slat_width = 12
        gap_width = 2
        total_width = slat_width + gap_width
        
        # Draw vertical slats
        for x in range(0, width, total_width):
            # Draw slat
            draw.rectangle([x, 0, x + slat_width, height], fill=color, outline=self.darken_color(color))
            
            # Add slat detail (3D effect)
            draw.line([x + slat_width//2, 0, x + slat_width//2, height], 
                     fill=self.lighten_color(color), width=1)
        
        return img
    
    def generate_roller_blind(self, width, height, color):
        """Generate roller blind texture"""
        # Create base image
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Add subtle texture pattern
        for y in range(0, height, 4):
            # Create subtle horizontal lines
            line_color = self.lighten_color(color, 0.1)
            draw.line([0, y, width, y], fill=line_color, width=1)
        
        # Add roller mechanism at top
        draw.rectangle([0, 0, width, 15], fill=self.darken_color(color, 0.3))
        
        return img
    
    def generate_roman_blinds(self, width, height, color):
        """Generate roman blind pleats"""
        # Create base image
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Pleat dimensions
        pleat_height = 20
        pleat_gap = 5
        
        # Draw pleats
        for y in range(0, height, pleat_height + pleat_gap):
            # Draw pleat
            draw.rectangle([0, y, width, y + pleat_height], fill=color, outline=self.darken_color(color))
            
            # Add pleat detail
            draw.line([0, y + pleat_height//2, width, y + pleat_height//2], 
                     fill=self.lighten_color(color), width=2)
        
        return img
    
    def apply_material_texture(self, image, material):
        """Apply material-specific texture effects"""
        if material == 'fabric':
            return self.add_fabric_texture(image)
        elif material == 'wood':
            return self.add_wood_texture(image)
        elif material == 'metal':
            return self.add_metal_texture(image)
        elif material == 'plastic':
            return self.add_plastic_texture(image)
        else:
            return image
    
    def add_fabric_texture(self, image):
        """Add fabric-like texture"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add subtle noise
        noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + noise, 0, 255)
        
        return Image.fromarray(img_array)
    
    def add_wood_texture(self, image):
        """Add wood-like texture"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add wood grain effect
        for i in range(img_array.shape[1]):
            grain = np.random.normal(0, 8, img_array.shape[0])
            img_array[:, i] = np.clip(img_array[:, i] + grain, 0, 255)
        
        return Image.fromarray(img_array)
    
    def add_metal_texture(self, image):
        """Add metal-like texture"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add metallic shine
        shine = np.random.normal(0, 3, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + shine, 0, 255)
        
        return Image.fromarray(img_array)
    
    def add_plastic_texture(self, image):
        """Add plastic-like texture"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add smooth plastic effect
        smooth = np.random.normal(0, 2, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + smooth, 0, 255)
        
        return Image.fromarray(img_array)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def darken_color(self, color, factor=0.2):
        """Darken a color for shadows"""
        return tuple(max(0, int(c * (1 - factor))) for c in color)
    
    def lighten_color(self, color, factor=0.2):
        """Lighten a color for highlights"""
        return tuple(min(255, int(c * (1 + factor))) for c in color)
    
    def get_available_patterns(self):
        """Get list of available blind patterns"""
        return list(self.patterns.keys())
    
    def get_available_materials(self):
        """Get list of available materials"""
        return ['fabric', 'wood', 'metal', 'plastic'] 