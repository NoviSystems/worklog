from github3 import GitHub
from github3.issues import Issue
from worklog import secrets

class GitHubConnector(object):
    
    def __init__(self):

        self.git_hub = GitHub(secrets.GITHUB_USER, secrets.GITHUB_PASS)
        self.orgs = list(self.git_hub.iter_orgs())      

        # As of 10/3/2013, the default rate limit was 5000/hr.
        # Should your code loop infinitely, this exception will 
        # leave enough requests to debug the problem without 
        # having to wait an hour.
        if self.git_hub.ratelimit_remaining < 500:
            raise Exception('You have only 500 GitHub requests left for this hour')
        
    def get_issues_for_repo(self, repo_name=None, github_id=None, repo_tuple=None):
        repos = self.git_hub.iter_all_repos()
        for repo in repos:
            if repo_name and repo_name == repo.name:
                return list(repo.iter_issues())
            elif github_id and github_id == repo.id:
                return list(repo.iter_issues())
            elif repo_tuple and repo_tuple[1] == repo.name:
                return list(repo.iter_issues())

    def get_all_issues(self):
        issues = []
        for org in self.orgs:
            org_repos = org.iter_repos()
            for repo in org_repos:
                issues += list(repo.iter_issues(state='open'))
                issues += list(repo.iter_issues(state='closed'))
        return issues

    def get_repos_for_org(self, org_login=None, org_id=None):
        for org in self.orgs:
            org_json = org.to_json()
            if org_json["login"] == org_login or org_json["id"] == org_id:
                return list(org.iter_repos())

    def get_all_repos(self):
        repos = []
        for org in self.orgs:
            org_repos = org.iter_repos()
            for repo in org_repos:
                repos.append(repo)
        return repos
