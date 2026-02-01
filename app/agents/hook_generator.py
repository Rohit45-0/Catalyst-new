from typing import Dict, Any, List
import json
from app.agents.base import BaseAgent
from app.core.prompts import PromptTemplates

class HookGeneratorAgent(BaseAgent):
    """
    Generates viral social media hooks by combining emotional triggers
    and competitive insights. Phase 2.3 Implementation.
    """
    
    SYSTEM_PROMPT = PromptTemplates.HOOK_GENERATION_SYSTEM
    
    def execute(self, product_data: Dict[str, Any], emotional_data: Dict[str, Any] = None, competitor_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the hook generation analysis."""
        try:
            prompt = self._build_prompt(product_data, emotional_data, competitor_data)
            return self._call_llm(self.SYSTEM_PROMPT, prompt)
        except Exception as e:
            self.logger.error(f"Hook generation failed: {e}")
            return {"error": str(e)}

    def _build_prompt(self, product_data: Dict[str, Any], emotional_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> str:
        """Construct prompt using PromptTemplates."""
        
        # Prepare context data
        emotion_str = emotional_data.get('primary_emotion', 'Unknown') if emotional_data else 'Unknown'
        triggers = ', '.join(emotional_data.get('psychological_triggers', [])) if emotional_data else ''
        hooks_preview = ', '.join(emotional_data.get('messaging_hooks', [])) if emotional_data else ''
        
        diff_str = str(competitor_data.get('analysis', {}).get('differentiation_score', 'N/A')) if competitor_data else 'N/A'
        trend_str = ', '.join(competitor_data.get('analysis', {}).get('visual_trends', [])) if competitor_data else ''
        
        return PromptTemplates.HOOK_GENERATION_USER.substitute(
            product_name=product_data.get('product_name', 'Unknown'),
            category=product_data.get('category', 'General'),
            emotion=emotion_str,
            triggers=triggers,
            messaging_hooks=hooks_preview,
            differentiation=diff_str,
            trend=trend_str
        )
