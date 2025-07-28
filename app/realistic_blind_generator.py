import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import colorsys
import math

class RealisticBlindGenerator:
    """
    Generates realistic 3D blinds with depth, shadows, and realistic appearance
    """
    
    def __init__(self):
        self.blind_types = {
            'horizontal': self.create_horizontal_blinds_3d,
            'vertical': self.create_vertical_blinds_3d,
            'roller': self.create_roller_blind_3d,
            'roman': self.create_roman_blinds_3d
        }
    
    def create_realistic_blind(self, blind_type, color, width, height, material='fabric', 
                             depth_factor=0.8, shadow_intensity=0.3):
        """
        Create realistic 3D blind with depth and shadows
        
        Args:
            blind_type: 'horizontal', 'vertical', 'roller', 'roman'
            color: hex color string
            width, height: dimensions
            material: 'fabric', 'wood', 'metal', 'plastic'
            depth_factor: 3D depth effect (0.5-1.0)
            shadow_intensity: shadow strength (0.1-0.5)
        """
        if blind_type not in self.blind_types:
            raise ValueError(f"Unsupported blind type: {blind_type}")
        
        # Convert hex to RGB
        rgb_color = self.hex_to_rgb(color)
        
        # Create 3D blind
        blind_image = self.blind_types[blind_type](
            width, height, rgb_color, material, depth_factor, shadow_intensity
        )
        
        return blind_image
    
    def create_horizontal_blinds_3d(self, width, height, color, material, depth_factor, shadow_intensity):
        """Create realistic horizontal blinds with 3D depth"""
        # Create base image with alpha channel
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Slat dimensions
        slat_height = max(8, height // 40)  # Adaptive slat height
        gap_height = max(2, slat_height // 4)
        total_height = slat_height + gap_height
        
        # Calculate number of slats
        num_slats = height // total_height
        
        # Create 3D slats with depth
        for i in range(num_slats):
            y = i * total_height
            
            # Main slat (front face)
            main_color = color
            draw.rectangle([0, y, width, y + slat_height], fill=main_color)
            
            # Top edge (highlight)
            highlight_color = self.lighten_color(color, 0.3)
            draw.rectangle([0, y, width, y + 2], fill=highlight_color)
            
            # Bottom edge (shadow)
            shadow_color = self.darken_color(color, 0.4)
            draw.rectangle([0, y + slat_height - 2, width, y + slat_height], fill=shadow_color)
            
            # Left edge (depth)
            left_depth = int(width * 0.02)
            depth_color = self.darken_color(color, 0.2)
            draw.rectangle([0, y, left_depth, y + slat_height], fill=depth_color)
            
            # Right edge (depth)
            right_depth = int(width * 0.02)
            draw.rectangle([width - right_depth, y, width, y + slat_height], fill=depth_color)
            
            # Add material texture
            if material == 'wood':
                self.add_wood_texture_3d(draw, 0, y, width, slat_height, color)
            elif material == 'metal':
                self.add_metal_texture_3d(draw, 0, y, width, slat_height, color)
            elif material == 'plastic':
                self.add_plastic_texture_3d(draw, 0, y, width, slat_height, color)
            else:  # fabric
                self.add_fabric_texture_3d(draw, 0, y, width, slat_height, color)
        
        # Add overall shadow for depth
        self.add_overall_shadow(img, shadow_intensity)
        
        return img
    
    def create_vertical_blinds_3d(self, width, height, color, material, depth_factor, shadow_intensity):
        """Create realistic vertical blinds with 3D depth"""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Slat dimensions
        slat_width = max(12, width // 30)  # Adaptive slat width
        gap_width = max(2, slat_width // 6)
        total_width = slat_width + gap_width
        
        # Calculate number of slats
        num_slats = width // total_width
        
        # Create 3D slats with depth
        for i in range(num_slats):
            x = i * total_width
            
            # Main slat (front face)
            main_color = color
            draw.rectangle([x, 0, x + slat_width, height], fill=main_color)
            
            # Left edge (highlight)
            highlight_color = self.lighten_color(color, 0.3)
            draw.rectangle([x, 0, x + 2, height], fill=highlight_color)
            
            # Right edge (shadow)
            shadow_color = self.darken_color(color, 0.4)
            draw.rectangle([x + slat_width - 2, 0, x + slat_width, height], fill=shadow_color)
            
            # Top edge (depth)
            top_depth = int(height * 0.02)
            depth_color = self.darken_color(color, 0.2)
            draw.rectangle([x, 0, x + slat_width, top_depth], fill=depth_color)
            
            # Bottom edge (depth)
            bottom_depth = int(height * 0.02)
            draw.rectangle([x, height - bottom_depth, x + slat_width, height], fill=depth_color)
            
            # Add material texture
            if material == 'wood':
                self.add_wood_texture_3d(draw, x, 0, slat_width, height, color)
            elif material == 'metal':
                self.add_metal_texture_3d(draw, x, 0, slat_width, height, color)
            elif material == 'plastic':
                self.add_plastic_texture_3d(draw, x, 0, slat_width, height, color)
            else:  # fabric
                self.add_fabric_texture_3d(draw, x, 0, slat_width, height, color)
        
        # Add overall shadow for depth
        self.add_overall_shadow(img, shadow_intensity)
        
        return img
    
    def create_roller_blind_3d(self, width, height, color, material, depth_factor, shadow_intensity):
        """Create realistic roller blind with 3D depth"""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Main blind surface
        main_color = color
        draw.rectangle([0, 0, width, height], fill=main_color)
        
        # Add roller tube at top (3D effect)
        tube_height = int(height * 0.05)
        tube_color = self.darken_color(color, 0.3)
        draw.rectangle([0, 0, width, tube_height], fill=tube_color)
        
        # Add tube highlight
        highlight_color = self.lighten_color(tube_color, 0.2)
        draw.rectangle([0, 0, width, tube_height//2], fill=highlight_color)
        
        # Add subtle texture lines (fabric folds)
        line_spacing = max(4, height // 50)
        for y in range(tube_height, height, line_spacing):
            line_color = self.darken_color(color, 0.1)
            draw.line([0, y, width, y], fill=line_color, width=1)
        
        # Add material texture
        if material == 'fabric':
            self.add_fabric_texture_3d(draw, 0, tube_height, width, height - tube_height, color)
        elif material == 'wood':
            self.add_wood_texture_3d(draw, 0, tube_height, width, height - tube_height, color)
        elif material == 'metal':
            self.add_metal_texture_3d(draw, 0, tube_height, width, height - tube_height, color)
        else:  # plastic
            self.add_plastic_texture_3d(draw, 0, tube_height, width, height - tube_height, color)
        
        # Add overall shadow for depth
        self.add_overall_shadow(img, shadow_intensity)
        
        return img
    
    def create_roman_blinds_3d(self, width, height, color, material, depth_factor, shadow_intensity):
        """Create realistic roman blinds with 3D depth and folds"""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create folded sections
        num_folds = 5
        fold_height = height // num_folds
        
        for i in range(num_folds):
            y = i * fold_height
            
            # Main fold section
            main_color = color
            draw.rectangle([0, y, width, y + fold_height], fill=main_color)
            
            # Add fold shadow (bottom of each fold)
            shadow_height = int(fold_height * 0.2)
            shadow_color = self.darken_color(color, 0.3)
            draw.rectangle([0, y + fold_height - shadow_height, width, y + fold_height], fill=shadow_color)
            
            # Add fold highlight (top of each fold)
            highlight_height = int(fold_height * 0.2)
            highlight_color = self.lighten_color(color, 0.2)
            draw.rectangle([0, y, width, y + highlight_height], fill=highlight_color)
            
            # Add material texture
            if material == 'fabric':
                self.add_fabric_texture_3d(draw, 0, y, width, fold_height, color)
            elif material == 'wood':
                self.add_wood_texture_3d(draw, 0, y, width, fold_height, color)
            elif material == 'metal':
                self.add_metal_texture_3d(draw, 0, y, width, fold_height, color)
            else:  # plastic
                self.add_plastic_texture_3d(draw, 0, y, width, fold_height, color)
        
        # Add overall shadow for depth
        self.add_overall_shadow(img, shadow_intensity)
        
        return img
    
    def add_fabric_texture_3d(self, draw, x, y, width, height, color):
        """Add realistic fabric texture with 3D effect"""
        # Add subtle weave pattern
        for i in range(0, width, 3):
            for j in range(0, height, 3):
                if (i + j) % 6 == 0:
                    pixel_color = self.lighten_color(color, 0.05)
                    draw.point([x + i, y + j], fill=pixel_color)
        
        # Add fabric grain lines
        for i in range(0, width, 8):
            line_color = self.darken_color(color, 0.1)
            draw.line([x + i, y, x + i, y + height], fill=line_color, width=1)
    
    def add_wood_texture_3d(self, draw, x, y, width, height, color):
        """Add realistic wood grain texture"""
        # Add wood grain lines
        for i in range(0, height, 2):
            grain_color = self.darken_color(color, 0.15)
            draw.line([x, y + i, x + width, y + i], fill=grain_color, width=1)
        
        # Add wood knots
        for _ in range(3):
            knot_x = x + np.random.randint(0, width)
            knot_y = y + np.random.randint(0, height)
            knot_size = np.random.randint(3, 8)
            knot_color = self.darken_color(color, 0.3)
            draw.ellipse([knot_x, knot_y, knot_x + knot_size, knot_y + knot_size], fill=knot_color)
    
    def add_metal_texture_3d(self, draw, x, y, width, height, color):
        """Add realistic metal texture with reflections"""
        # Add metallic shine lines
        for i in range(0, width, 6):
            shine_color = self.lighten_color(color, 0.4)
            draw.line([x + i, y, x + i, y + height], fill=shine_color, width=1)
        
        # Add subtle reflection spots
        for _ in range(5):
            spot_x = x + np.random.randint(0, width)
            spot_y = y + np.random.randint(0, height)
            spot_size = np.random.randint(2, 5)
            spot_color = self.lighten_color(color, 0.6)
            draw.ellipse([spot_x, spot_y, spot_x + spot_size, spot_y + spot_size], fill=spot_color)
    
    def add_plastic_texture_3d(self, draw, x, y, width, height, color):
        """Add realistic plastic texture"""
        # Add subtle surface variation
        for i in range(0, width, 4):
            for j in range(0, height, 4):
                if np.random.random() > 0.7:
                    pixel_color = self.lighten_color(color, 0.1)
                    draw.point([x + i, y + j], fill=pixel_color)
    
    def add_overall_shadow(self, img, intensity):
        """Add overall shadow for 3D depth effect"""
        # Create shadow mask
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Add gradient shadow from top-left
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Calculate shadow intensity based on position
                shadow_val = int(intensity * 255 * (i + j) / (img.size[0] + img.size[1]))
                shadow_draw.point([i, j], fill=(0, 0, 0, shadow_val))
        
        # Composite shadow with original image
        img = Image.alpha_composite(img, shadow)
        return img
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def lighten_color(self, color, factor=0.2):
        """Lighten a color by given factor"""
        r, g, b = color
        return (
            min(255, int(r + (255 - r) * factor)),
            min(255, int(g + (255 - g) * factor)),
            min(255, int(b + (255 - b) * factor))
        )
    
    def darken_color(self, color, factor=0.2):
        """Darken a color by given factor"""
        r, g, b = color
        return (
            max(0, int(r * (1 - factor))),
            max(0, int(g * (1 - factor))),
            max(0, int(b * (1 - factor)))
        )
    
    def get_available_types(self):
        """Get available blind types"""
        return list(self.blind_types.keys())
    
    def get_available_materials(self):
        """Get available materials"""
        return ['fabric', 'wood', 'metal', 'plastic'] 