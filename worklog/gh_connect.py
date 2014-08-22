from github3 import GitHub, GitHubError
from django.conf import settings


class GitHubConnector(object):
    def __init__(self, gh_username=settings.GITHUB_USER, gh_password=settings.GITHUB_PASS):
        """
        Kwargs:
            gh_username (str): Github username defaults to the one provided in secrets.py
            gh_password (str): Github password defaults to the one provided in secrets.py
        """
        self.git_hub = GitHub(gh_username, gh_password)
        self.orgs = list(self.git_hub.iter_orgs())

        # As of 10/3/2013, the default rate limit was 5000/hr.
        # Should your code loop infinitely, this exception will
        # leave enough requests to debug the problem without
        # having to wait an hour.
        if self.git_hub.ratelimit_remaining < 500:
            raise Exception('You have only 500 GitHub requests left for this hour')

    def get_issues_for_repo(self, repo_name=None, github_id=None):
        """ Returns all the issues for a given repo name or id in the users account (not organization)

        Kwargs:
            repo_name (str, optional): The name of a repo
            github_id (str, optional): The github id of a repo
        """
        repos = self.git_hub.iter_all_repos()
        for repo in repos:
            if repo_name and repo_name == repo.name:
                return list(repo.iter_issues())
            elif github_id and github_id == repo.id:
                return list(repo.iter_issues())
        return []

    def get_all_issues(self):
        """ Returns all issues for all repos associated with the account in secrets.py """
        issues = []
        for org in self.orgs:
            org_repos = org.iter_repos()
            for repo in org_repos:
                try:
                    issues += list(repo.iter_issues(state='open'))
                    issues += list(repo.iter_issues(state='closed'))
                except GitHubError:
                    continue
        return issues

    def get_repos_for_org(self, org_login=None, org_name=None):
        """ Returns all repos for the organization

        Kwargs:
            org_login (str, optional): Login for the organization
            org_name (str, optional): Name of the organization
        """
        for org in self.orgs:
            org_json = org.to_json()
            if org_json["login"] == org_login or org_json["id"] == org_name:
                return list(org.iter_repos())

    def get_all_repos(self):
        """ Returns all repos for all organizations associated with the account in secrets.py """
        repos = []
        for org in self.orgs:
            org_repos = org.iter_repos()
            for repo in org_repos:
                repos.append(repo)
        return repos
