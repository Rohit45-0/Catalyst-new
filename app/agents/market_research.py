"""
Market Research Agent - Optimized for Minimal API Usage

This agent uses Brave Search API efficiently with just 2 queries per product:
1. Main search: product info, features, reviews
2. Supplementary search: news and videos

Optimized for scale operations.
"""

import os
import time
from typing import Dict, Any, List
import re
from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from brave import Brave


class MarketResearchAgent:
    """
    Optimized market research using minimal API calls.
    Uses only 2 queries per product instead of 7.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize with Brave API key.
        
        Optimization:
        - 2 queries per product (vs 7 previously)
        - Saves 71% of API quota
        - 100 products/month with 200 query limit
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            print("Warning: No Brave API key found. Set BRAVE_API_KEY environment variable.")
            print("   Get your free key at: https://brave.com/search/api/")
        
        self.brave = Brave(api_key=self.api_key) if self.api_key else None
        self.last_request_time = 0
        self.query_count = 0
        self.max_queries = 200
        self.emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        # Dingbats
        self.extra_symbols = re.compile(r'[✨✅⚠️🔎👁️🥊🧠🎣🌍🎥🎨✍️📈📱📸❌⬇️⏳🔄👕📘]', flags=re.UNICODE)
        
    def _rate_limit(self):
        """Enforce 1 search per second rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.2f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        self.query_count += 1
        
        if self.query_count >= self.max_queries:
            print(f"Warning: Approaching query limit ({self.query_count}/{self.max_queries})")

    def _strip_emojis(self, text: str) -> str:
        """Remove all emojis and special symbols from text."""
        if not text:
            return ""
        text = self.emoji_pattern.sub('', text)
        text = self.extra_symbols.sub('', text)
        return text
    
    def _extract_reviews_from_results(self, results: List[Dict]) -> Dict[str, List[str]]:
        """Extract reviews from search results based on source domain."""
        reviews = {
            "amazon": [],
            "reddit": [],
            "youtube": [],
            "general": []
        }
        
        for result in results:
            url = result.get('url', '').lower()
            description = result.get('description', '')
            
            if description:
                description = self._strip_emojis(description)
                # Categorize by source
                if 'amazon.com' in url:
                    reviews["amazon"].append(description)
                elif 'reddit.com' in url:
                    reviews["reddit"].append(description)
                elif 'youtube.com' in url or 'vimeo.com' in url:
                    reviews["youtube"].append(description)
                else:
                    # Only add to general if it looks like a review
                    if any(word in description.lower() for word in ['review', 'rating', 'opinion', 'experience']):
                        reviews["general"].append(description)
        
        return reviews
    
    def _extract_features(self, results: List[Dict]) -> List[str]:
        """Extract features from search results."""
        features = []
        
        for result in results:
            description = result.get('description', '')
            if description:
                description = self._strip_emojis(description)
                # Look for feature-related content
                if any(keyword in description.lower() for keyword in 
                       ['feature', 'spec', 'include', 'comes with', 'equipped', 'power', 'watt']):
                    if len(description) > 30:  # Meaningful content
                        features.append(description)
        
        return features
    
    def _get_category_suffix(self, category: str) -> str:
        """Get search suffix based on category."""
        suffixes = {
            "tech_gadgets": "specs benchmarks features vs",
            "fashion_apparel": "style fit material reviews",
            "beauty_wellness": "ingredients benefits reviews",
            "food_beverage": "taste ingredients nutrition reviews",
            "home_decor": "reviews quality style",
            "fitness_sports": "performance durability reviews",
            "b2b_saas": "pricing features reviews vs"
        }
        return suffixes.get(category, "review features specifications")

    def search_comprehensive(self, product_name: str, category: str = None) -> Dict[str, Any]:
        """
        QUERY 1: Comprehensive search for product info, reviews, and features.
        Uses a single query with count=20 to get maximum information.
        """
        if not self.brave:
            return {"results": [], "reviews": {}, "features": []}
        
        suffix = self._get_category_suffix(category)
        print(f"Query 1/2: Comprehensive search for '{product_name}' ({suffix})")
        
        all_data = {
            "results": [],
            "reviews": {"amazon": [], "reddit": [], "youtube": [], "general": []},
            "features": []
        }
        
        try:
            self._rate_limit()
            
            # Single comprehensive query with higher count
            search_results = self.brave.search(
                q=f"{product_name} {suffix}",
                count=20,  # Get more results in one query
                raw=True
            )
            
            if isinstance(search_results, dict) and 'web' in search_results:
                web_results = search_results['web'].get('results', [])
                
                # Store all results
                for result in web_results:
                    all_data["results"].append({
                        "title": result.get('title', ''),
                        "url": result.get('url', ''),
                        "description": result.get('description', ''),
                        "source": "brave_web"
                    })
                
                # Extract reviews from results
                all_data["reviews"] = self._extract_reviews_from_results(web_results)
                
                # Extract features from results
                all_data["features"] = self._extract_features(web_results)
                
                print(f"   Found: {len(web_results)} results, "
                      f"{sum(len(v) for v in all_data['reviews'].values())} reviews, "
                      f"{len(all_data['features'])} features")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        return all_data
    
    def search_news_videos(self, product_name: str) -> Dict[str, Any]:
        """
        QUERY 2: Search for news and videos.
        Optional - can be skipped if not needed.
        """
        if not self.brave:
            return {"news": [], "videos": []}
        
        print(f"News and videos for '{product_name}'")
        
        media_data = {
            "news": [],
            "videos": []
        }
        
        try:
            self._rate_limit()
            
            # Search for news and videos
            search_results = self.brave.search(
                q=f"{product_name} news video",
                count=10,
                raw=True
            )
            
            if isinstance(search_results, dict):
                # Extract news
                if 'news' in search_results and search_results['news'].get('results'):
                    for article in search_results['news']['results'][:5]:
                        media_data["news"].append({
                            "title": article.get('title', ''),
                            "url": article.get('url', ''),
                            "description": article.get('description', ''),
                            "source": "news"
                        })
                
                # Extract videos
                if 'videos' in search_results and search_results['videos'].get('results'):
                    for video in search_results['videos']['results'][:5]:
                        media_data["videos"].append({
                            "title": video.get('title', ''),
                            "url": video.get('url', ''),
                            "description": video.get('description', ''),
                            "source": "video"
                        })
                
                # Fallback to web results
                elif 'web' in search_results:
                    web_results = search_results['web'].get('results', [])
                    for result in web_results:
                        url = result.get('url', '')
                        if 'youtube.com' in url or 'vimeo.com' in url:
                            media_data["videos"].append({
                                "title": result.get('title', ''),
                                "url": url,
                                "description": result.get('description', ''),
                                "source": "video"
                            })
                
                print(f"   Found: {len(media_data['news'])} news, {len(media_data['videos'])} videos")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        return media_data

    def __call__(self, state: AgentState) -> AgentState:
        """
        Process the state with optimized 2-query approach.
        """
        print("Market Research Agent: Optimized search (2 queries only)...")
        
        if not self.brave:
            error_msg = "Brave API key not configured. Please set BRAVE_API_KEY environment variable."
            state["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return state
        
        try:
            product_data = state.get("product_data", {})
            product_name = product_data.get("product_name")
            category_data = state.get("category_data", {})
            category = category_data.get("category")
            
            if not product_name:
                product_name = "Generic Product"
                print("Warning: No product name found, using generic search")
                
            print(f"Researching: {product_name} (Category: {category})")
            print(f"Optimization: Using only 2 API queries (saves 71% quota)\n")
            
            # QUERY 1: Comprehensive search (product info + reviews + features)
            comprehensive_data = self.search_comprehensive(product_name, category)
            
            # QUERY 2: News and videos (optional)
            media_data = self.search_news_videos(product_name)
            
            # Combine all data
            search_results = comprehensive_data["results"]
            reviews = comprehensive_data["reviews"]
            features = comprehensive_data["features"]
            news = media_data["news"]
            videos = media_data["videos"]
            
            # Add video descriptions to YouTube reviews
            for video in videos:
                if video.get("description"):
                    reviews["youtube"].append(video["description"])
            
            # Count totals
            total_reviews = sum(len(v) for v in reviews.values())
            
            # Save to state
            state["market_data"] = {
                "search_term": product_name,
                "results": search_results,
                "reviews": reviews,
                "features": features,
                "news": news,
                "videos": videos,
                "metadata": {
                    "total_results": len(search_results),
                    "total_reviews": total_reviews,
                    "total_features": len(features),
                    "total_news": len(news),
                    "total_videos": len(videos),
                    "sources": ["brave_web", "amazon", "reddit", "youtube", "news"],
                    "api_provider": "Brave Search API",
                    "queries_used": 2,
                    "optimization": "2 queries instead of 7 (71% savings)"
                }
            }
            
            state["current_step"] = "market_research_complete"
            state["messages"].append(
                SystemMessage(
                    content=f"Gathered market data via Brave Search (2 queries): {len(search_results)} results, "
                           f"{total_reviews} reviews, {len(features)} features, {len(news)} news, "
                           f"{len(videos)} videos for {product_name}"
                )
            )
            
            print(f"\nMarket research complete!")
            print(f"   Search Results: {len(search_results)}")
            print(f"   Reviews: {total_reviews}")
            print(f"   Features: {len(features)}")
            print(f"   News: {len(news)}")
            print(f"   Videos: {len(videos)}")
            print(f"   API Queries Used: 2 (saved 5 queries!)")
            
        except Exception as e:
            error_msg = f"Market Research Error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            import traceback
            traceback.print_exc()
            
        return state
