#!/usr/bin/env python3
"""
GitHub Follow-Back Checker
Finds users you follow who haven't followed you back.
"""

import os
import sys
import requests
from typing import Set, Tuple


class GitHubFollowChecker:
    """Check GitHub followers vs following."""
    
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
    
    def display_results(self, non_mutual: Set[str], followers: Set[str], following: Set[str]):
        """
        Display the results in a formatted way.
        
        Args:
            non_mutual: Users you follow who don't follow back
            followers: Your followers
            following: Users you're following
        """
        print("\n" + "=" * 50)
        print("GitHub Follow-Back Checker")
        print("=" * 50)
        print(f"\nTotal Followers: {len(followers)}")
        print(f"Total Following: {len(following)}")
        print(f"Mutual Follows: {len(followers & following)}")
        
        if non_mutual:
            print(f"\nUsers you follow who don't follow you back ({len(non_mutual)}):")
            print("-" * 50)
            for user in sorted(non_mutual):
                print(f"  • {user}")
        else:
            print("\n✅ Great! Everyone you follow also follows you back!")
        
        print("\n" + "=" * 50)


def main():
    """Main entry point."""
    # Get token from environment variable
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set!")
        print("\nPlease set your token:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("\nOr create a .env file with:")
        print("  GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    # Create checker and run
    checker = GitHubFollowChecker(token)
    
    try:
        non_mutual, followers, following = checker.get_non_mutual_follows()
        checker.display_results(non_mutual, followers, following)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
