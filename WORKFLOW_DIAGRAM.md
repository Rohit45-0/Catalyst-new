# Catalyst AI Workflow Diagram

```mermaid
graph TD
    Start[User Uploads Image] --> Category[Category Detection Agent]
    Category --> Vision[Vision Analyzer Agent]
    
    subgraph "Phase 2: Strategic Intelligence"
        Vision --> Competitor[Competitor Analysis Agent]
        Vision --> Emotional[Emotional Analysis Agent]
        Competitor --> Hook[Hook Generation Agent]
        Emotional --> Hook
    end
    
    subgraph "Phase 3: Market Research"
        Category --> Research[Market Research Agent]
        Vision --> Research
    end
    
    subgraph "Phase 4: Media Generation"
        Hook --> Video[Video Creator Agent]
        Research --> Video
        Emotional --> Video
        
        Hook --> Poster[Poster Generator Agent]
        Emotional --> Poster
    end
    
    subgraph "Phase 5: copy & Validation"
        Research --> Content[Content Writer Agent]
        Vision --> Content
        Hook --> Content
        
        Content --> Predictor[Performance Predictor Agent]
        Emotional --> Predictor
    end
    
    subgraph "Phase 6: Execution"
        Predictor --> Publisher[Social Media Publisher]
        Video --> Publisher
        Poster --> Publisher
    end
    
    Publisher --> End[LinkedIn / Meta / Instagram]
```

## Agent Roles
1. **Category Detection**: Classifies product into 7 marketing categories.
2. **Vision Analyzer**: GPT-4o analysis of visual features, materials, and colors.
3. **Competitor Analysis**: Visual comparison with market leaders.
4. **Emotional Analysis**: Maps product features to psychological triggers.
5. **Hook Generation**: Creates viral hooks (curiosity, problem-agitation).
6. **Market Research**: Brave Search for reviews and customer sentiment.
7. **Video Creator**: Generates script and 10s video (Sora-2).
8. **Poster Generator**: DALL-E 3 high-spec ad poster.
9. **Content Writer**: Generates platform-specific text (LinkedIn, Blog, Meta).
10. **Performance Predictor**: Estimates engagement scores.
11. **Publisher**: Handles API posting to social platforms.
