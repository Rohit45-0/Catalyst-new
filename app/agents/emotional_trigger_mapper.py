from typing import Dict, Any, List
import json
from app.agents.base import BaseAgent

class EmotionalTriggerMapperAgent(BaseAgent):
    """
    Agent that maps product visuals to psychological emotional triggers.
    Phase 2.2 Implementation.
    """
    
    SYSTEM_PROMPT = """You are an expert Psychologist and Neuromarketer.
Your goal is to analyze a product based on its visual description and category, and identify the primary emotional triggers that drive purchasing decisions.

EMOTION FRAMEWORK:
1. ASPIRATION: Desire for self-improvement, status, or ideal lifestyle.
2. RELIEF: Solution to a pain point, safety, ease of mind.
3. BELONGING: Connection, community, acceptance.
4. ACHIEVEMENT: Success, mastery, productivity.
5. COMFORT: Safety, relaxation, pampering.
6. INNOVATION: Curiosity, future-focused, being first.

OUTPUT JSON FORMAT:
{
    "primary_emotion": "One of the above",
    "secondary_emotion": "One of the above",
    "psychological_triggers": ["Trigger 1", "Trigger 2"],
    "messaging_hooks": [
        "Hook 1 (e.g., 'Reclaim your time...')",
        "Hook 2"
    ],
    "visual_cues": ["Cue 1 identified in data", "Cue 2"]
}
"""

    def execute(self, product_data: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Run the emotional mapping analysis."""
        try:
            prompt = self._build_prompt(product_data, category)
            return self._call_llm(self.SYSTEM_PROMPT, prompt)
        except Exception as e:
            self.logger.error(f"Emotional mapping failed: {e}")
            return {"error": str(e)}

    def _build_prompt(self, product_data: Dict[str, Any], category: str) -> str:
        """Construct the analysis prompt (Pure function)."""
        
        # Extract relevant fields to keep prompt focused
        features = product_data.get("key_features", [])
        style = product_data.get("visual_style", "Unknown")
        colors = product_data.get("primary_colors", [])
        
        return f"""
PRODUCT CATEGORY: {category or 'General'}
PRODUCT NAME: {product_data.get('product_name', 'Unknown')}

VISUAL DATA:
- Style: {style}
- Colors: {', '.join(colors)}
- Key Features: {', '.join(features)}

Analyze the psychological impact of this product. Why would someone feel compelled to buy it?
Map it to the Emotion Framework.
"""
