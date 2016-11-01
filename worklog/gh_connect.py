from github3 import login, GitHubError
from django.conf import settings


class GitHubConnector(object):
    def __init__(self, username=settings.GITHUB_USER, password=settings.GITHUB_PASS):
        """
        Kwargs:
            username (str): Github username defaults to the one provided in secrets.py
            password (str): Github password defaults to the one provided in secrets.py
        """
        self.username = username
        self.github = login(username, password)
        self.authenticated = (username and password)

        if self.authenticated:
            self.orgs = self.github.organizations()
        else:
            self.orgs = self.github.organizations_with(username)

        # As of 10/3/2013, the default rate limit was 5000/hr.
        # Should your code loop infinitely, this exception will
        # leave enough requests to debug the problem without
        # having to wait an hour.
        # if self.github.ratelimit_remaining < 50:
        #     raise Exception('You have only 50 GitHub requests left for this hour')

    def get_all_issues(self):
        """
        Returns all issues for all repos associated with the account in secrets.py
        """
        issues = []
        for repo in self.get_all_repos():
            try:
                issues += list(repo.issues(state='all'))
            except GitHubError:
                continue
        return issues

    def get_all_repos(self):
        """
        Returns all repos for an account in secrets.py
        - If user is logged in, get all of their repos
        - If user is not logged in, get all of their public organizations, and then public repos of organiza
        - If user is not logged in, and has no public organizations, get all of their public repos
        """
        if self.authenticated:
            return self.github.repositories()

        repos = list(self.github.repositories_by(self.gh_username))

        for org in self.orgs or []:
            repos += list(org.repositories())

        return repos
