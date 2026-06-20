#!/usr/bin/env python3
"""
GitHub Follow-Back Checker with Auto-Unfollow
Finds users you follow who haven't followed you back and optionally unfollows them.
"""

import os
import sys
import requests
from typing import Set, Tuple


class GitHubFollowChecker:
    """Check GitHub followers vs following and optionally auto-unfollow."""
    
    def __init__(self, token: str):
        """
        Initialize the checker with a GitHub token.
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _fetch_users(self, endpoint: str) -> Set[str]:
        """
        Fetch all users from a paginated endpoint.
        
        Args:
            endpoint: API endpoint (e.g., 'user/followers')
            
        Returns:
            Set of usernames
        """
        users = set()
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/{endpoint}"
            params = {"page": page, "per_page": per_page}
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from {endpoint}: {e}")
                sys.exit(1)
            
            data = response.json()
            
            if not data:
                break
            
            for user in data:
                users.add(user["login"])
            
            page += 1
        
        return users
    
    def unfollow_user(self, username: str) -> bool:
        """
        Unfollow a user.
        
        Args:
            username: GitHub username to unfollow
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/user/following/{username}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error unfollowing {username}: {e}")
            return False
    
    def get_non_mutual_follows(self) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Get users you follow who don't follow you back.
        
        Returns:
            Tuple of (non_mutual, followers, following)
        """
        print("Fetching your followers list...")
        followers = self._fetch_users("user/followers")
        
        print("Fetching your following list...")
        following = self._fetch_users("user/following")
        
        # Find users you follow but who don't follow you back
        non_mutual = following - followers
        
        return non_mutual, followers, following
    
    def auto_unfollow(self, non_mutual: Set[str]) -> Tuple[int, int]:
        """
        Automatically unfollow users who don't follow you back.
        
        Args:
            non_mutual: Set of usernames to unfollow
            
        Returns:
            Tuple of (successful_unfollows, failed_unfollows)
        """
        successful = 0
        failed = 0
        
        print(f"\n🔄 Starting auto-unfollow for {len(non_mutual)} users...")
        
        for i, username in enumerate(sorted(non_mutual), 1):
            if self.unfollow_user(username):
                successful += 1
                print(f"  ✓ [{i}/{len(non_mutual)}] Unfollowed: {username}")
            else:
                failed += 1
                print(f"  ✗ [{i}/{len(non_mutual)}] Failed to unfollow: {username}")
        
        return successful, failed
    
    def display_results(self, non_mutual: Set[str], followers: Set[str], following: Set[str], auto_unfollow_mode: bool = False):
        """
        Display the results in a formatted way.
        
        Args:
            non_mutual: Users you follow who don't follow back
            followers: Your followers
            following: Users you're following
            auto_unfollow_mode: Whether auto-unfollow is enabled
        """
        print("\n" + "=" * 60)
        print("GitHub Follow-Back Checker")
        print("=" * 60)
        print(f"\nTotal Followers: {len(followers)}")
        print(f"Total Following: {len(following)}")
        print(f"Mutual Follows: {len(followers & following)}")
        
        if non_mutual:
            print(f"\nUsers you follow who don't follow you back ({len(non_mutual)}):")
            print("-" * 60)
            
            if auto_unfollow_mode:
                print("⚠️  AUTO-UNFOLLOW MODE ENABLED")
                print("These users will be unfollowed automatically...\n")
                successful, failed = self.auto_unfollow(non_mutual)
                print(f"\n✅ Successfully unfollowed: {successful}")
                print(f"❌ Failed to unfollow: {failed}")
            else:
                for user in sorted(non_mutual):
                    print(f"  • {user}")
                print("\n💡 To auto-unfollow these users, set AUTO_UNFOLLOW=true")
        else:
            print("\n✅ Great! Everyone you follow also follows you back!")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    # Get token from environment variable
    token = os.getenv("GITHUB_TOKEN") or os.getenv("PAT_TOKEN")
    
    if not token:
        print("Error: GITHUB_TOKEN or PAT_TOKEN environment variable not set!")
        print("\nPlease set your token:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("  or")
        print("  export PAT_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Check if auto-unfollow is enabled
    auto_unfollow_mode = os.getenv("AUTO_UNFOLLOW", "false").lower() == "true"
    
    # Create checker and run
    checker = GitHubFollowChecker(token)
    
    try:
        non_mutual, followers, following = checker.get_non_mutual_follows()
        checker.display_results(non_mutual, followers, following, auto_unfollow_mode)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
