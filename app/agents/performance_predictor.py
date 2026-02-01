import re
import math
from typing import Dict, Any, List
from app.agents.base import BaseAgent

class PerformancePredictorAgent(BaseAgent):
    """
    Analyzes generated marketing content and predicts engagement metrics (CTR, Reach)
    based on heuristic scoring of copy quality.
    
    Scoring Factors:
    1. Hook Strength: Length, curiosity keywords, power words.
    2. Emotional Density: Usage of emotional triggers.
    3. Readability: Paragraph length, sentence complexity.
    4. Call-To-Action (CTA): Clarity and presence.
    """
    
    def __init__(self):
        super().__init__()
        # Power words that tend to increase CTR
        self.power_words = [
            "secret", "exclusive", "limited", "today", "now", "free", "save", 
            "discover", "unlock", "proven", "hack", "trick", "reveal", "ultimate",
            "game-changer", "transform", "stop", "guaranteed", "rare"
        ]
        
    def execute(self, content_data: Dict[str, Any], emotional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run performance prediction on all generated content items.
        
        Args:
            content_data: Output from ContentWriterAgent (linkedin_post, etc.)
            emotional_data: Output from EmotionalTriggerMapperAgent (for keyword matching)
            
        Returns:
            Dict containing scores and predictions for each platform.
        """
        predictions = {}
        
        # 1. Analyze LinkedIn Post
        if "linkedin_post" in content_data:
            predictions["linkedin"] = self._analyze_post(
                content_data["linkedin_post"], 
                platform="linkedin",
                emotional_data=emotional_data
            )
            
        # 2. Analyze Meta Post
        if "meta_post" in content_data: # Or check keys loosely if needed
            predictions["meta"] = self._analyze_post(
                content_data.get("meta_post", {}), 
                platform="meta",
                emotional_data=emotional_data
            )
            
        # 3. Calculate Global Score (Average)
        scores = [p["score"] for p in predictions.values() if "score" in p]
        global_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "global_score": round(global_score, 1),
            "platform_predictions": predictions,
            "analysis_version": "1.0 (Heuristic)"
        }

    def _analyze_post(self, post_data: Dict[str, Any], platform: str, emotional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a single post."""
        
        # Extract text components
        title = post_data.get("title", "")
        body = post_data.get("content", "")
        caption = post_data.get("caption", "")
        full_text = f"{title}\n{body}\n{caption}".strip()
        
        if not full_text:
            return {"score": 0, "error": "Empty content"}

        score = 0
        max_score = 100
        strengths = []
        improvements = []
        
        # --- FACTOR 1: HOOK STRENGTH (30 points) ---
        # Hook is usually the first sentence or title
        hook = title if title else full_text.split('\n')[0]
        hook_score = 0
        
        # Check for Power Words
        found_power_words = [w for w in self.power_words if w.lower() in hook.lower()]
        if found_power_words:
            hook_score += 15
            strengths.append(f"Strong hook words: {', '.join(found_power_words[:3])}")
        else:
            improvements.append("Add a power word to the hook (e.g., 'Unlock', 'Secret')")
            
        # Check for Curiosity (Question or '...')
        if "?" in hook or "..." in hook or ":" in hook:
            hook_score += 15
            strengths.append("Hook creates curiosity")
        
        score += hook_score

        # --- FACTOR 2: EMOTIONAL RESONANCE (30 points) ---
        emo_score = 0
        if emotional_data:
            triggers = emotional_data.get("psychological_triggers", [])
            primary_emo = emotional_data.get("primary_emotion", "")
            
            # Simple keyword matching
            trigger_hits = 0
            for trigger in triggers:
                # Triggers are often phrases, split them or match partial
                words = trigger.split()
                for w in words:
                    if len(w) > 4 and w.lower() in full_text.lower():
                        trigger_hits += 1
            
            if trigger_hits > 0:
                emo_score = 30
                strengths.append(f"Resonates with target emotion ({primary_emo})")
            else:
                emo_score = 10
                improvements.append(f"Infuse more '{primary_emo}' related words")
        else:
            # Fallback if no emo data
            emo_score = 15 
            
        score += emo_score

        # --- FACTOR 3: READABILITY (20 points) ---
        # Simple heuristic: Paragraph break frequency
        read_score = 0
        num_chars = len(full_text)
        num_breaks = full_text.count('\n\n') + full_text.count('\n')
        
        # Ideal: 1 break every ~200 chars for social
        if num_chars > 0:
             density = num_chars / (num_breaks + 1)
             if density < 250: # Good, short paragraphs
                 read_score = 20
                 strengths.append("Excellent readability")
             elif density < 400:
                 read_score = 10
             else:
                 improvements.append("Break up long text blocks")
        
        score += read_score

        # --- FACTOR 4: CTA CLARITY (20 points) ---
        cta_keywords = ["link", "bio", "click", "sign up", "buy", "shop", "visit", "check", "dm", "comment"]
        cta_found = any(k in full_text.lower() for k in cta_keywords)
        
        if cta_found:
            score += 20
            strengths.append("Clear Call-to-Action")
        else:
            improvements.append("Add a clear CTA (e.g., 'Link in bio')")

        # --- PREDICT METRICS ---
        # Simulate metrics based on score
        # Base CTR for industry is ~1%
        predicted_ctr = 0.5 + (score / 100.0) * 2.0  # Range: 0.5% to 2.5%
        
        return {
            "score": score,
            "metrics": {
                "predicted_ctr": f"{round(predicted_ctr, 2)}%",
                "reach_potential": "High" if score > 80 else "Medium" if score > 50 else "Low"
            },
            "strengths": strengths,
            "improvements": improvements
        }
