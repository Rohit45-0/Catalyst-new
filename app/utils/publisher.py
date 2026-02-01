import os
import requests
import json
from typing import Dict, Any, Optional
from pathlib import Path

class SocialMediaPublisher:
    """
    Handles automated posting to various social media platforms via their APIs.

    Supported Platforms:
    - LinkedIn (UGC Post API) with automatic token refresh
    - Meta (Facebook/Instagram Graph API)
    - Medium (Post API)
    """

    def __init__(self):
        """Initialize with API tokens from environment variables."""
        # Force reload .env to ensure we have latest tokens
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # LinkedIn - with automatic token refresh support
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_refresh_token = os.getenv("LINKEDIN_REFRESH_TOKEN")
        self.linkedin_person_id = os.getenv("LINKEDIN_PERSON_ID")
        self.linkedin_org_id = os.getenv("LINKEDIN_ORGANIZATION_ID")

        # Meta
        self.meta_access_token = os.getenv("META_ACCESS_TOKEN")
        self.meta_page_id = os.getenv("META_PAGE_ID")
        self.instagram_id = os.getenv("INSTAGRAM_BUSINESS_ID")

        # Medium
        self.medium_token = os.getenv("MEDIUM_INTEGRATION_TOKEN")
        self.medium_user_id = os.getenv("MEDIUM_USER_ID")

        # LinkedIn credentials for token refresh
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "77entx67zq9zwo")
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "77entx67zq9zwo")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

        # X (Twitter)
        self.x_consumer_key = os.getenv("X_CONSUMER_KEY")
        self.x_consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.x_access_token = os.getenv("X_ACCESS_TOKEN")
        self.x_access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
        import re
        self.emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        self.extra_symbols = re.compile(r'[✨✅⚠️🔎👁️🥊🧠🎣🌍🎥🎨✍️📈📱📸❌⬇️⏳🔄👕📘]', flags=re.UNICODE)

    def _clean_content(self, text: str) -> str:
        """Strip emojis and non-ASCII for maximum compatibility."""
        if not text:
            return ""
        # Remove emojis
        text = self.emoji_pattern.sub('', text)
        text = self.extra_symbols.sub('', text)
        # Force to ASCII, ignoring errors (will remove other non-standard chars)
        return text.encode('ascii', 'ignore').decode('ascii')

    def _refresh_linkedin_token(self) -> bool:
        """
        Automatically refresh LinkedIn access token using refresh token.
        No user interaction needed!
        """
        if not self.linkedin_refresh_token:
            print("   No refresh token available. Cannot auto-refresh.")
            return False

        try:
            print("   Access token expired. Refreshing automatically...")
            url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.linkedin_refresh_token,
                "client_id": self.linkedin_client_id,
                "client_secret": self.linkedin_client_secret
            }
            response = requests.post(url, data=data)

            if response.status_code == 200:
                token_data = response.json()
                new_token = token_data.get("access_token")

                if new_token:
                    self.linkedin_token = new_token

                    # Update .env file
                    env_path = Path(".env")
                    if env_path.exists():
                        content = env_path.read_text()
                        if "LINKEDIN_ACCESS_TOKEN=" in content:
                            content = content.replace(
                                [line for line in content.split("\n") if line.startswith("LINKEDIN_ACCESS_TOKEN=")][0],
                                f"LINKEDIN_ACCESS_TOKEN={new_token}"
                            )
                        else:
                            content += f"\nLINKEDIN_ACCESS_TOKEN={new_token}"
                        env_path.write_text(content)

                    print(f"   Token refreshed successfully!")
                    return True
            else:
                print(f"   Failed to refresh token: {response.text}")
                return False
        except Exception as e:
            print(f"   Error refreshing token: {str(e)}")
            return False

    def _upload_linkedin_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to LinkedIn and return the asset URN for posting.

        Multi-step process:
        1. Register upload with LinkedIn
        2. Get upload URL
        3. Upload binary image data
        4. Return asset URN
        """
        if not image_path or not os.path.exists(image_path):
            print(f"   Image not found: {image_path}")
            return None

        try:
            print(f"  [*] Uploading image to LinkedIn...")

            # Step 1: Register the upload
            register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "Content-Type": "application/json"
            }

            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:organization:{self.linkedin_org_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            response = requests.post(register_url, json=register_payload, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"  [!] Registration failed ({response.status_code})")
                print(f"      Error: {response.text[:200]}")
                return None

            register_data = response.json()
            print(f"  [DEBUG] Registration response keys: {register_data.keys()}")

            # Extract upload URL - handle different response formats
            upload_url = None
            asset_id = None

            if "value" in register_data:
                value = register_data["value"]
                asset_id = value.get("asset")

                # Try to get upload URL from uploadMechanism
                upload_mechanism = value.get("uploadMechanism", {})
                if upload_mechanism:
                    # Try different possible keys
                    mech_key = "com.linkedin.digitalmedia.uploading.AssetUploadHttpPutUploadMechanism"
                    if mech_key in upload_mechanism:
                        upload_url = upload_mechanism[mech_key].get("uploadUrl")
                    else:
                        # Try to get first available upload mechanism
                        for key, val in upload_mechanism.items():
                            if isinstance(val, dict) and "uploadUrl" in val:
                                upload_url = val["uploadUrl"]
                                break

            if not upload_url or not asset_id:
                print(f"  [!] Missing upload URL or asset ID")
                print(f"      Asset ID: {asset_id}")
                print(f"      Upload URL: {upload_url}")
                return None

            print(f"  [+] Got upload URL, uploading image...")

            # Step 2: Upload the image binary
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()

            print(f"  [*] Image size: {len(image_data)} bytes")

            put_headers = {
                "Content-Type": "image/jpeg"
            }

            put_response = requests.put(upload_url, data=image_data, headers=put_headers, timeout=30)

            if put_response.status_code not in [200, 201]:
                print(f"  [!] Upload failed ({put_response.status_code})")
                print(f"      Error: {put_response.text[:200]}")
                return None

            print(f"  [+] Image uploaded successfully!")
            print(f"  [*] Asset ID: {asset_id}")
            return asset_id

        except Exception as e:
            print(f"   Image upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _upload_linkedin_video(self, video_path: str) -> Optional[str]:
        """
        Upload video to LinkedIn and return the asset URN.
        Similar to image upload but uses feedshare-video recipe.
        """
        if not video_path or not os.path.exists(video_path):
            print(f"   Video not found: {video_path}")
            return None

        try:
            print(f"  [*] Uploading video to LinkedIn...")

            # Step 1: Register the upload
            register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "Content-Type": "application/json"
            }

            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": f"urn:li:organization:{self.linkedin_org_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            response = requests.post(register_url, json=register_payload, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"  [!] Registration failed ({response.status_code})")
                print(f"      Error: {response.text.encode('ascii', 'replace').decode()[:200]}")
                return None

            register_data = response.json()
            # print(f"DEBUG REG: {register_data}") # Safe debug
            
            # Extract upload URL
            upload_url = None
            asset_id = register_data.get("value", {}).get("asset")

            value = register_data.get("value", {})
            upload_mechanism = value.get("uploadMechanism", {})

            if upload_mechanism:
                # Try finding any uploadUrl
                mech_key = "com.linkedin.digitalmedia.uploading.AssetUploadHttpPutUploadMechanism"
                if mech_key in upload_mechanism:
                    upload_url = upload_mechanism[mech_key].get("uploadUrl")
                # Fallback: look for any key with uploadUrl
                if not upload_url:
                     for k, v in upload_mechanism.items():
                         if isinstance(v, dict) and 'uploadUrl' in v:
                             upload_url = v['uploadUrl']
                             break

            if not upload_url or not asset_id:
                print(f"  [!] Missing upload URL or asset ID for video")
                print(f"      Response: {str(register_data).encode('ascii', 'replace').decode()[:500]}")
                return None

            print(f"  [+] Got upload URL, uploading video binary...")

            # Step 2: Upload the video binary
            filesize = os.path.getsize(video_path)
            print(f"  [*] Video size: {filesize} bytes")
            
            with open(video_path, "rb") as vid_file:
                video_data = vid_file.read()

            put_headers = {"Content-Type": "application/octet-stream"}
            put_response = requests.put(upload_url, data=video_data, headers=put_headers, timeout=120)

            if put_response.status_code not in [200, 201]:
                print(f"  [!] Upload failed ({put_response.status_code})")
                print(f"      Error: {put_response.text[:200]}")
                return None

            print(f"  [+] Video uploaded successfully!")
            print(f"  [*] Asset ID: {asset_id}")
            return asset_id

        except Exception as e:
            print(f"   Video upload error: {str(e)}")
            return None

    def post_to_linkedin(self, title: str, content: str, hashtags: list, image_path: Optional[str] = None, video_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post content to LinkedIn with optional image.

        Auto-refreshes token on 401 error.
        """
        if not self.linkedin_token:
            return {"status": "error", "message": "LinkedIn token not configured"}

        try:
            # Prepare content
            full_text = f"{title}\n\n{content}"
            if hashtags:
                full_text += "\n\n" + " ".join([f"#{tag.lstrip('#')}" for tag in hashtags])

            # Clean content using robust helper
            text = self._clean_content(full_text)

            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            payload = {
                "author": f"urn:li:organization:{self.linkedin_org_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Determine Media Type (Video > Image > None)
            media_category = "NONE"
            media_item = None

            if video_path:
                print(f"  [*] Uploading video to LinkedIn: {video_path}...")
                video_asset = self._upload_linkedin_video(video_path)
                if video_asset:
                    media_category = "VIDEO"
                    media_item = video_asset
                else:
                    print("   LinkedIn Video upload failed. Falling back to image...")
            
            if media_category == "NONE" and image_path:
                print(f"  [*] Uploading image to LinkedIn: {image_path}...")
                image_asset = self._upload_linkedin_image(image_path)
                if image_asset:
                     media_category = "IMAGE"
                     media_item = image_asset
                else:
                     print("   LinkedIn Image upload failed.")

            # Construct specificContent based on media
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = media_category
            
            if media_item:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "media": media_item
                    }
                ]


            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 401:
                # Token expired, try to refresh
                if self._refresh_linkedin_token():
                    # Retry with new token
                    headers["Authorization"] = f"Bearer {self.linkedin_token}"
                    response = requests.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                post_id = response.headers.get("X-RestLi-Id", "unknown")
                print(f"  [+] LinkedIn post published! ID: {post_id}")
                return {
                    "status": "success",
                    "message": "Post published to LinkedIn",
                    "data": {"id": post_id}
                }
            else:
                print(f"  [!] Failed to post to LinkedIn: {response.status_code}")
                print(f"      Response: {response.text}")
                return {
                    "status": "error",
                    "message": f"LinkedIn API error: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            error_msg = f"LinkedIn posting error: {str(e)}"
            print(f"   {error_msg}")
            return {"status": "error", "message": error_msg}

    def _get_page_access_token(self) -> Optional[str]:
        """
        Exchange User Token for Page Access Token.
        Required for posting to Page Feed.
        """
        if not self.meta_access_token or not self.meta_page_id:
            return None
            
        try:
            url = f"https://graph.facebook.com/v18.0/{self.meta_page_id}"
            params = {
                "access_token": self.meta_access_token,
                "fields": "access_token"
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return data["access_token"]
            
            print(f"  [!] Could not fetch Page Token. Using User Token fallback.")
            return self.meta_access_token # Fallback
            
        except Exception as e:
            print(f"  [!] Error fetching Page Token: {e}")
            return self.meta_access_token

    def _upload_meta_image(self, image_path: str, page_token: str) -> Optional[str]:
        """
        Upload image to Facebook Page and return the photo ID.
        Uses the Photos API for proper image posting.
        """
        try:
            import os
            if not os.path.exists(image_path):
                print(f"  [!] Image file not found: {image_path}")
                return None
            
            url = f"https://graph.facebook.com/v18.0/{self.meta_page_id}/photos"
            
            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                data = {
                    'access_token': page_token,
                    'published': 'false'  # Upload but don't publish yet
                }
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code in [200, 201]:
                    photo_id = response.json().get('id')
                    print(f"  [+] Image uploaded to Meta. Photo ID: {photo_id}")
                    return photo_id
                else:
                    print(f"  [!] Meta image upload failed: {response.status_code}")
                    print(f"      {response.text}")
                    return None
                    
        except Exception as e:
            print(f"  [!] Error uploading image to Meta: {e}")
            return None

    def _upload_meta_video(self, video_path: str, page_token: str, caption: str) -> Optional[str]:
        """
        Upload video to Facebook Page.
        Returns the Video ID if successful.
        """
        try:
            import os
            if not os.path.exists(video_path):
                print(f"  [!] Video file not found: {video_path}")
                return None
            
            # Use graph-video for video uploads
            url = f"https://graph-video.facebook.com/v18.0/{self.meta_page_id}/videos"
            
            filesize = os.path.getsize(video_path)
            print(f"  [*] Uploading video to Meta ({filesize} bytes)...")
            
            with open(video_path, 'rb') as video_file:
                files = {'source': (os.path.basename(video_path), video_file, 'video/mp4')}
                data = {
                    'access_token': page_token,
                    'description': caption,
                    'published': 'true' 
                }
                
                # specific timeout for video
                response = requests.post(url, files=files, data=data, timeout=120)
                
                if response.status_code in [200, 201]:
                    vid_id = response.json().get('id')
                    print(f"  [+] Video uploaded to Meta! ID: {vid_id}")
                    return vid_id
                else:
                    print(f"  [!] Meta video upload failed: {response.status_code}")
                    print(f"      {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"  [!] Error uploading video to Meta: {e}")
            return None

    def post_to_meta(self, caption: str, hashtags: list, image_path: Optional[str] = None, video_path: Optional[str] = None) -> Dict[str, Any]:
        """Post to Meta (Facebook Page) with optional image."""
        if not self.meta_access_token or not self.meta_page_id:
            return {"status": "error", "message": "Meta credentials not configured"}

        try:
            # 1. Get Page Token (Critical for permissions)
            page_token = self._get_page_access_token()
            
            text_raw = caption
            if hashtags:
                text_raw += "\n\n" + " ".join([f"#{tag.lstrip('#')}" for tag in hashtags])
            
            # Clean content
            text = self._clean_content(text_raw)

            # 2. Check for Video (Takes precedence or assumes separated logic)
            if video_path:
                # For video, the upload AND post happen in one step often, 
                # OR we upload and it appears in feed.
                # _upload_meta_video handles the posting/publishing if 'published=true'.
                vid_id = self._upload_meta_video(video_path, page_token, text)
                
                if vid_id:
                    return {
                        "status": "success",
                        "message": "Video published to Meta",
                        "data": {"id": vid_id}
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Meta video upload failed"
                    }

            # 3. If image, use Photos API
            if image_path:
                photo_id = self._upload_meta_image(image_path, page_token)
                
                if photo_id:
                    # Post with photo using the photo ID
                    url = f"https://graph.facebook.com/v18.0/{self.meta_page_id}/feed"
                    payload = {
                        "message": text,
                        "attached_media[0]": json.dumps({"media_fbid": photo_id}),
                        "access_token": page_token
                    }
                else:
                    # Fallback to text-only if image upload failed
                    print("   Image upload failed, posting text-only...")
                    url = f"https://graph.facebook.com/v18.0/{self.meta_page_id}/feed"
                    payload = {
                        "message": text,
                        "access_token": page_token
                    }
            else:
                # Text-only post
                url = f"https://graph.facebook.com/v18.0/{self.meta_page_id}/feed"
                payload = {
                    "message": text,
                    "access_token": page_token
                }

            print(f"  [*] Posting to Meta (Facebook Page ID: {self.meta_page_id})...")
            
            response = requests.post(url, data=payload)

            print(f"  [DEBUG] Meta Response Status: {response.status_code}")
            print(f"  [DEBUG] Meta Response Body: {response.text}")

            if response.status_code in [200, 201]:
                response_data = response.json()
                post_id = response_data.get("id", "unknown")
                print(f"  [+] Meta post published! ID: {post_id}")
                return {
                    "status": "success",
                    "message": "Post published to Meta",
                    "data": response_data
                }
            else:
                error_details = response.text
                print(f"  [!] Meta posting failed: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Meta API error: {response.status_code}",
                    "details": error_details
                }
        except Exception as e:
            error_msg = f"Meta posting error: {str(e)}"
            print(f"   {error_msg}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": error_msg}

    def _upload_instagram_video(self, video_path: str, caption: str) -> Optional[str]:
        """
        Upload video to Instagram (Reels) using Resumable Upload.
        Returns the Container ID (creation_id) ready for publishing.
        """
        try:
            if not self.instagram_id:
                print("   Instagram Business ID not set.")
                return None
                
            import os
            filesize = os.path.getsize(video_path)
            print(f"  [*] Uploading to Instagram ({filesize} bytes)...")
            
            # Step 1: Initialize Upload
            init_url = f"https://graph.facebook.com/v19.0/{self.instagram_id}/media"
            init_params = {
                "media_type": "REELS",
                "upload_type": "resumable",
                "caption": caption,
                "access_token": self.meta_access_token
            }
            res_init = requests.post(init_url, data=init_params)
            if res_init.status_code != 200:
                print(f"  [!] IG Init failed: {res_init.text}")
                return None
                
            init_data = res_init.json()
            upload_uri = init_data.get("uri")
            container_id = init_data.get("id")
            
            # Step 2: Upload Binary
            with open(video_path, "rb") as f:
                video_data = f.read()
                
            headers = {
                "Authorization": f"OAuth {self.meta_access_token}",
                "offset": "0",
                "file_size": str(filesize)
            }
            res_upload = requests.post(upload_uri, data=video_data, headers=headers, timeout=300)
            if res_upload.status_code != 200:
                print(f"  [!] IG Upload failed: {res_upload.text}")
                return None
                
            # Step 3: Wait for Processing (Status Check)
            import time
            status_url = f"https://graph.facebook.com/v19.0/{container_id}"
            status_params = {"fields": "status_code", "access_token": self.meta_access_token}
            
            print("  [*] Waiting for IG video processing...")
            for i in range(20):
                time.sleep(5)
                res_status = requests.get(status_url, params=status_params)
                if res_status.status_code == 200:
                    status_data = res_status.json()
                    status_code = status_data.get("status_code")
                    if status_code == "FINISHED":
                        print("  [+] IG Video Processed.")
                        return container_id
                    elif status_code == "ERROR":
                         print("  [!] IG Video Processing Error.")
                         return None
                else:
                     print(f"  [!] IG Status Check failed: {res_status.text}")
            
            print("  [!] IG Video Check Timed Out.")
            return container_id # Try returning anyway?

        except Exception as e:
            print(f"  [!] Error uploading info to Instagram: {e}")
            return None

    def post_to_instagram(self, caption: str, video_path: str) -> Dict[str, Any]:
        """Post video Reel to Instagram."""
        if not self.instagram_id or not self.meta_access_token:
             return {"status": "error", "message": "Instagram credentials missing"}
             
        try:
             # 1. Upload & Create Container
             container_id = self._upload_instagram_video(video_path, caption)
             if not container_id:
                 return {"status": "error", "message": "Failed to upload video to Instagram"}
             
             # 2. Publish
             publish_url = f"https://graph.facebook.com/v19.0/{self.instagram_id}/media_publish"
             publish_params = {
                 "creation_id": container_id,
                 "access_token": self.meta_access_token
             }
             
             print("  [*] Publishing to Instagram...")
             res_pub = requests.post(publish_url, data=publish_params)
             
             if res_pub.status_code == 200:
                 pub_id = res_pub.json().get("id")
                 print(f"  [+] Instagram Post Published! ID: {pub_id}")
                 return {
                     "status": "success",
                     "message": "Published to Instagram",
                     "data": {"id": pub_id}
                 }
             else:
                 print(f"  [!] IG Publish failed: {res_pub.text}")
                 return {
                     "status": "error",
                     "message": f"IG Publish failed: {res_pub.status_code}",
                     "details": res_pub.text
                 }
                 
        except Exception as e:
            return {"status": "error", "message": f"Instagram error: {str(e)}"}

    def post_to_twitter(self, content: str, hashtags: list, media_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to X (Twitter) using Tweepy v2 API.
        Supports text and single media (image or video).
        """
        if not all([self.x_consumer_key, self.x_consumer_secret, self.x_access_token, self.x_access_token_secret]):
            return {"status": "error", "message": "X (Twitter) credentials missing"}

        try:
            import tweepy
            
            # v1.1 API for Media Upload (v2 doesn't support upload yet)
            auth = tweepy.OAuth1UserHandler(
                self.x_consumer_key, self.x_consumer_secret,
                self.x_access_token, self.x_access_token_secret
            )
            api = tweepy.API(auth)
            
            # v2 Client for Posting
            client = tweepy.Client(
                consumer_key=self.x_consumer_key,
                consumer_secret=self.x_consumer_secret,
                access_token=self.x_access_token,
                access_token_secret=self.x_access_token_secret
            )

            media_id = None
            if media_path and os.path.exists(media_path):
                print(f"  [*] Uploading media to X: {media_path}...")
                try:
                    # Upload media (supports chunked upload via media_upload for small files, chunked_upload for large)
                    # For video, chunked is safer.
                    media = api.media_upload(filename=media_path)
                    media_id = media.media_id
                    print(f"  [+] Media uploaded. ID: {media_id}")
                except Exception as e:
                    print(f"  [!] X Media Upload failed: {e}")

            # Prepare text
            text = content
            if hashtags:
                text += "\n\n" + " ".join([f"#{tag.lstrip('#')}" for tag in hashtags])
            
            # Limit length
            if len(text) > 280:
                print("  [!] Tweet too long, truncating...")
                text = text[:277] + "..."

            print("  [*] Posting to X (Twitter)...")
            
            if media_id:
                response = client.create_tweet(text=text, media_ids=[media_id])
            else:
                response = client.create_tweet(text=text)

            post_id = response.data['id']
            print(f"  [+] Tweet posted! ID: {post_id}")
            
            return {
                "status": "success",
                "message": "Published to X (Twitter)",
                "data": {"id": post_id}
            }

        except Exception as e:
            error_msg = f"X posting error: {str(e)}"
            print(f"  [!] {error_msg}")
            return {"status": "error", "message": error_msg}

    def post_to_medium(self, title: str, content: str, tags: list) -> Dict[str, Any]:
        """Post to Medium blog platform."""
        if not self.medium_token or not self.medium_user_id:
            return {"status": "error", "message": "Medium credentials not configured"}

        try:
            url = f"https://api.medium.com/v1/users/{self.medium_user_id}/posts"
            headers = {
                "Authorization": f"Bearer {self.medium_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "title": title,
                "content": content,
                "contentFormat": "markdown",
                "publishStatus": "public",
                "tags": tags[:5]  # Medium allows max 5 tags
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "message": "Post published to Medium",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Medium API error: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {"status": "error", "message": f"Medium posting error: {str(e)}"}
