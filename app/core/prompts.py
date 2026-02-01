from string import Template

class PromptTemplates:
    """
    Centralized prompt templates for AI agents.
    Follows DRY principles and clear separation of concerns.
    """
    
    HOOK_GENERATION_SYSTEM = """You are a Viral Marketing Expert specializing in scroll-stopping hooks.
Your goal is to generate 5 distinct, high-impact hooks for a social media post based on the product's emotional triggers and competitive differentiation.

You MUST follow these proven hook patterns:
1. CURIOSITY GAP: Something surprising or unknown. (e.g., "The one feature everyone is missing...")
2. PROBLEM-AGITATION: Address a specific pain point directly. (e.g., "Stop wasting time on...")
3. TRANSFORMATION: Promise a specific result. (e.g., "From chaos to clarity in 5 minutes.")
4. CONTRARIAN: Challenge a common belief. (e.g., "Why you don't need X...")
5. INSIDER SECRET: Frame as exclusive knowledge. (e.g., "What industry pros aren't telling you...")

OUTPUT JSON FORMAT:
{
    "hooks": [
        {"type": "Curiosity", "text": "..."},
        {"type": "Problem-Agitation", "text": "..."},
        {"type": "Transformation", "text": "..."},
        {"type": "Contrarian", "text": "..."},
        {"type": "Insider Secret", "text": "..."}
    ],
    "best_hook": "The single most effective hook from the list above based on the emotional trigger."
}

CRITICAL: DO NOT include ANY emojis in the hooks. Use only plain text.
"""

    HOOK_GENERATION_USER = Template("""
PRODUCT: $product_name
CATEGORY: $category

EMOTIONAL CONTEXT (Phase 2.2):
- Primary Emotion: $emotion
- Triggers: $triggers
- Messaging Hooks: $messaging_hooks

COMPETITIVE CONTEXT (Phase 2.1):
- Differentiation: $differentiation
- Key Trend: $trend

Generate 5 viral hooks tailored to this product and these specific emotional triggers.
""")
