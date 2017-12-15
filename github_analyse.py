# -*- coding: utf-8
"""With GitHub Api for repository get list of top contributors and number of open and closed
pull requests, issues and number 'old' pulls and issues."""
import json
import urllib
import urlparse

from datetime import datetime


def insert_repo_url():
    """User's insert repository url and check that url from https://github.com"""
    repo_url = raw_input('Please insert github repository url with space in end of line: ')
    if 'https://github.com' not in repo_url:
        print 'Please insert correct repository url, it\'s must be url from https://github.com'
        insert_repo_url()
    return repo_url.replace('github.com', 'api.github.com/repos')[:-1]


def request_for_contributors(repo):
    """Request with GitHub Api for list top-30 contributors"""
    repo_contrs = '{}/contributors'.format(repo)
    print 'Top Contributors'
    print ('-' * 30)
    try:
        response = urllib.urlopen(repo_contrs)
        for i in json.loads(response.read())[:30]:
            print i['login'], i['contributions']
    except TypeError:
        print 'Please check that repository exist'
        exit(1)
    except IOError:
        print 'Please check you internet connection'
        exit(1)


def request_for_pulls_and_issues(repo, parameter_name, old_days):
    """Request with GitHub Api for pulls and issues"""
    response_open = urllib.urlopen('{}/{}?state=open&per_page=100'.format(repo, parameter_name))
    data_open = json.loads(response_open.read())

    response_closed = urllib.urlopen('{}/{}?state=closed&per_page=100'.format(repo, parameter_name))
    data_closed = json.loads(response_closed.read())

    now = datetime.now()
    old_problems = 0
    for i in data_open:
        if (now - datetime.strptime(i['created_at'][:10], '%Y-%m-%d')).days > old_days:
            old_problems += 1

    return pagination(response_open, data_open), pagination(response_closed, data_closed), old_problems


def pagination(response, data):
    """Get number of pulls or issues with pagination (one page contains only 30 pulls or issues)"""
    if response.info().getheader('Link'):
        last_page_url = response.info().getheader('Link').split(',')[1].split(';')[0][2:-1]
        response_last_page = urllib.urlopen(last_page_url)
        data_last_page = json.loads(response_last_page.read())
        parsed = urlparse.urlparse(last_page_url)
        problems = (int(urlparse.parse_qs(parsed.query)['page'][0]) - 1) * 100 + len(data_last_page)
    else:
        problems = len(data)
    return problems


if __name__ == '__main__':
    repo_name = insert_repo_url()
    request_for_contributors(repo_name)
    open_pr, closed_pr, old_pr = request_for_pulls_and_issues(repo_name, 'pulls', 30)
    print ('-' * 30)
    print "Open pull requests - {}".format(open_pr)
    print "Closed pull requests - {}".format(closed_pr)
    print 'Old pull requests (open more than 30 days) - {}'.format(old_pr)
    open_is, closed_is, old_is = request_for_pulls_and_issues(repo_name, 'issues', 14)
    print ('-' * 30)
    print "Open issues - {}".format(open_is - open_pr)
    print "Closed issues - {}".format(closed_is - closed_pr)
    print 'Old issues (open more than 14 days) - {}'.format(old_is)