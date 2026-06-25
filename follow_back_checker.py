#!/usr/bin/env python3
"""
GitHub Follow-Back Checker with Auto-Follow and Auto-Unfollow
Finds users you follow who haven't followed you back and optionally unfollows them.
Finds users who follow you but you haven't followed back and optionally follows them.
"""

import os
import sys
import requests
from typing import Set, Tuple


class GitHubFollowChecker:
    """Check GitHub followers vs following and optionally auto-follow/unfollow."""
    
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
    
    def follow_user(self, username: str) -> bool:
        """
        Follow a user.
        
        Args:
            username: GitHub username to follow
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/user/following/{username}"
        
        try:
            response = requests.put(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error following {username}: {e}")
            return False
    
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
    
    def get_follow_stats(self) -> Tuple[Set[str], Set[str], Set[str], Set[str], Set[str]]:
        """
        Get follow statistics and users to follow back or unfollow.
        
        Returns:
            Tuple of (followers, following, not_following_back, need_followback, mutual)
        """
        print("Fetching your followers list...")
        followers = self._fetch_users("user/followers")
        
        print("Fetching your following list...")
        following = self._fetch_users("user/following")
        
        # Users you follow but who don't follow you back
        not_following_back = following - followers
        
        # Users who follow you but you don't follow back
        need_followback = followers - following
        
        # Mutual follows
        mutual = followers & following
        
        return followers, following, not_following_back, need_followback, mutual
    
    def auto_follow(self, need_followback: Set[str]) -> Tuple[int, int]:
        """
        Automatically follow users who follow you back.
        
        Args:
            need_followback: Set of usernames to follow
            
        Returns:
            Tuple of (successful_follows, failed_follows)
        """
        successful = 0
        failed = 0
        
        print(f"\n👥 Starting auto-follow for {len(need_followback)} users...")
        
        for i, username in enumerate(sorted(need_followback), 1):
            if self.follow_user(username):
                successful += 1
                print(f"  ✓ [{i}/{len(need_followback)}] Followed: {username}")
            else:
                failed += 1
                print(f"  ✗ [{i}/{len(need_followback)}] Failed to follow: {username}")
        
        return successful, failed
    
    def auto_unfollow(self, not_following_back: Set[str]) -> Tuple[int, int]:
        """
        Automatically unfollow users who don't follow you back.
        
        Args:
            not_following_back: Set of usernames to unfollow
            
        Returns:
            Tuple of (successful_unfollows, failed_unfollows)
        """
        successful = 0
        failed = 0
        
        print(f"\n🔄 Starting auto-unfollow for {len(not_following_back)} users...")
        
        for i, username in enumerate(sorted(not_following_back), 1):
            if self.unfollow_user(username):
                successful += 1
                print(f"  ✓ [{i}/{len(not_following_back)}] Unfollowed: {username}")
            else:
                failed += 1
                print(f"  ✗ [{i}/{len(not_following_back)}] Failed to unfollow: {username}")
        
        return successful, failed
    
    def display_results(self, followers: Set[str], following: Set[str], 
                       not_following_back: Set[str], need_followback: Set[str], 
                       mutual: Set[str], auto_follow_mode: bool = False, 
                       auto_unfollow_mode: bool = False):
        """
        Display the results in a formatted way.
        
        Args:
            followers: Your followers
            following: Users you're following
            not_following_back: Users you follow who don't follow back
            need_followback: Users who follow you but you don't follow back
            mutual: Users you and they follow each other
            auto_follow_mode: Whether auto-follow is enabled
            auto_unfollow_mode: Whether auto-unfollow is enabled
        """
        print("\n" + "=" * 70)
        print("GitHub Follow-Back Checker")
        print("=" * 70)
        print(f"\nTotal Followers: {len(followers)}")
        print(f"Total Following: {len(following)}")
        print(f"Mutual Follows: {len(mutual)}")
        print(f"Need Follow-Back (they follow you): {len(need_followback)}")
        print(f"Not Following Back (you follow them): {len(not_following_back)}")
        
        # Users who follow you but you don't follow back
        if need_followback:
            print(f"\n{'─' * 70}")
            print(f"Users who follow you but you don't follow back ({len(need_followback)}):")
            print(f"{'─' * 70}")
            
            if auto_follow_mode:
                print("👥 AUTO-FOLLOW MODE ENABLED")
                print("These users will be automatically followed...\n")
                successful, failed = self.auto_follow(need_followback)
                print(f"\n✅ Successfully followed: {successful}")
                print(f"❌ Failed to follow: {failed}")
            else:
                for user in sorted(need_followback):
                    print(f"  • {user}")
                print("\n💡 To auto-follow these users, set AUTO_FOLLOW=true")
        else:
            print(f"\n✅ Great! You follow back everyone who follows you!")
        
        # Users you follow but who don't follow you back
        if not_following_back:
            print(f"\n{'─' * 70}")
            print(f"Users you follow who don't follow you back ({len(not_following_back)}):")
            print(f"{'─' * 70}")
            
            if auto_unfollow_mode:
                print("⚠️  AUTO-UNFOLLOW MODE ENABLED")
                print("These users will be automatically unfollowed...\n")
                successful, failed = self.auto_unfollow(not_following_back)
                print(f"\n✅ Successfully unfollowed: {successful}")
                print(f"❌ Failed to unfollow: {failed}")
            else:
                for user in sorted(not_following_back):
                    print(f"  • {user}")
                print("\n💡 To auto-unfollow these users, set AUTO_UNFOLLOW=true")
        else:
            print(f"\n✅ Great! Everyone you follow also follows you back!")
        
        print("\n" + "=" * 70)


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
    
    # Check if auto-follow and auto-unfollow are enabled
    auto_follow_mode = os.getenv("AUTO_FOLLOW", "false").lower() == "true"
    auto_unfollow_mode = os.getenv("AUTO_UNFOLLOW", "false").lower() == "true"
    
    # Create checker and run
    checker = GitHubFollowChecker(token)
    
    try:
        followers, following, not_following_back, need_followback, mutual = checker.get_follow_stats()
        checker.display_results(followers, following, not_following_back, 
                               need_followback, mutual, auto_follow_mode, auto_unfollow_mode)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
