import os
from github import Github
from datetime import datetime, timedelta
import requests

try:
    # Get GitHub token from environment variable
    g = Github(os.environ["GITHUB_TOKEN"])
    
    # Get repository and other environment variables
    repo = g.get_repo(os.environ['REPO_NAME'])
    repo_name = os.environ['REPO_NAME']
    pulls = repo.get_pulls(state='open')
    GCHAT_MESSAGE = []
    pr_number_str = os.environ.get('PR_NUMBER')
    pr_number = int(pr_number_str) if pr_number_str else None
    pr = repo.get_pull(pr_number) if pr_number else None
    MERGE_PR = os.environ.get("MERGE_PR")
    CLOSE_PR = os.environ.get("CLOSE_PR")
    VERSION_FILE = os.environ.get("VERSION_FILE")
    EVENT = os.environ['EVENT']
    GCHAT_WEBHOOK_URL = os.environ['WEBHOOK']
    EVENT_CHECK = os.environ['EVENT_CHECK_VARIABLE']

    # Function to send the message to Google Chat
    def send_message_to_google_chat(message, webhook_url):
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload)
        return response

    # Define messages for Google Chat and comment body in GitHub
    msg = {
        "stale_label": 'This PR is stale because it has been open 15 days with no activity. Remove the stale label and update PR; otherwise, it will be closed in the next 2 days.',
        "stale_days": 3,
        "stale_close_days": 2,
        "staled_PR_closing": 'This PR was closed because it has been stalled for 2 days with no activity.',
        "check_PR_target": 'Do not accept PR target from feature branch to the master branch.',
        "check_description": 'No Description on PR body. Please add a valid description.',
        "approve_merge": 'Pull Request Approved and Merged!',
        "approve_comment": 'This pull request was approved and merged because of a slash command.',
        "closing_comment": 'This pull request was closed because of a slash command.',
        "check_version_file": 'The VERSION file exists. All ok',
        "version_file_inexistence": "The VERSION file does not exist. Closing this pull request.",
        "tagcheck_success": "The VERSION didn't match with the tag. All ok",
        "tagcheck_reject": "The tag from VERSION file already exists. Please update the VERSION file.",
        "label": "Please remove the DO NOT MERGE LABEL",
    }

    # Define default messages based on events
    if pr:
        msg["default"] = f"An Event is created on PR:\nTitle: {pr.title}\nURL: {pr.html_url}\nStatus: {pr.state}"
        msg["opened"] = f"New Pull Request Created by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}\nStatus: {pr.state}"
        msg["edited"] = f"Pull Request Edited by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}\nStatus: {pr.state}"
        msg["closed"] = f"Pull Request Closed by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}\nStatus: {pr.state}"
        msg["reopened"] = f"Pull Request Reopened by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}\nStatus: {pr.state}"

    # Get current datetime and add 5 days
    now = datetime.now() + timedelta(days=3)

    # Check events based on the workflow type
    if EVENT_CHECK == 'stale':
        # 1. Add "Stale" label to the PR if no activity for 15 days
        for pull in pulls:
            time_diff = now - pull.updated_at
            stale_label_present = any(label.name == "Stale" for label in pull.labels)
            if time_diff > timedelta(days=msg.get("stale_days")) and not stale_label_present:
                pull.create_issue_comment(msg.get("stale_label"))
                pull.add_to_labels('Stale')
                GCHAT_MESSAGE.append(f"@{pull.user.login}: {msg.get('stale_label')}")
                GCHAT_MESSAGE.append(f"URL: {pull.html_url}\nStatus: {pull.state}")
               
        # 2. Close stalled PR if no activity for 2 days
        for pull in pulls:
            if "Stale" in [label.name for label in pull.labels]:
                if time_diff > timedelta(days=msg.get("stale_close_days")):
                    pull.edit(state="closed")
                    pull.create_issue_comment(msg.get("staled_PR_closing"))
                    GCHAT_MESSAGE.append(f"@{pull.user.login}: {msg.get('staled_PR_closing')}")
                    GCHAT_MESSAGE.append(f"URL: {pull.html_url}\nStatus: {pull.state}")

    if EVENT_CHECK == 'pull':
        # 3. Check if the PR targets the master branch directly
        for pull in pulls:
            if pull.base.ref == 'master' and not pull.head.ref.startswith('release/'):
                pull.edit(state='closed')
                pull.create_issue_comment(msg.get("check_PR_target"))
                GCHAT_MESSAGE.append(msg.get("check_PR_target"))

        # 4. Check if the PR has a description
        for pull in pulls:
            if not pull.body:
                pull.edit(state='closed')
                pull.create_issue_comment(msg.get("check_description"))
                GCHAT_MESSAGE.append(msg.get("check_description"))

        # 5. Check if the version from "VERSION" file exists as a tag
        if pr and VERSION_FILE:
            tags = repo.get_tags()
            tag_exist = False
            for tag in tags:
                if tag.name == VERSION_FILE:
                    tag_exist = True
                    break
            if not tag_exist:
                print(msg.get("tagcheck_success"))
            else:
                pr.create_issue_comment(msg.get("tagcheck_reject"))
                pr.edit(state='closed')
                GCHAT_MESSAGE.append(msg.get("tagcheck_reject"))
        else:
            pr.create_issue_comment(msg.get("version_file_inexistence"))
            pr.edit(state='closed')
            GCHAT_MESSAGE.append(msg.get("version_file_inexistence"))

        # 6. Close PRs with DO NOT MERGE label
        if pr:
            labels = pr.get_labels()
            if "DO NOT MERGE" in [label.name for label in labels]:
                pr.edit(state='closed')
                pr.create_issue_comment(msg.get("label"))
                GCHAT_MESSAGE.append(msg.get("label"))

    if EVENT_CHECK == 'slash':
        # 7.1 Check if the Approved comment is in the PR comments
        if MERGE_PR == 'true':
            if pr:
                pr.merge(merge_method='merge', commit_message=msg.get("approve_merge"))
                pr.create_issue_comment(msg.get("approve_comment"))
                GCHAT_MESSAGE.append(msg.get("approve_comment"))

        # 7.2 Check if the Close comment is in the PR comments
        if CLOSE_PR == 'true':
            if pr:
                pr.edit(state="closed")
                pr.create_issue_comment(msg.get("closing_comment"))
                GCHAT_MESSAGE.append(msg.get("closing_comment"))

    # Include PR comments in the Google Chat message
    if pr:
        comments = pr.get_issue_comments()
        if comments:
            for comment in comments:
                user_login = comment.user.login if comment.user else "Unknown"
                GCHAT_MESSAGE.append(f"Issue Comment by {user_login}: {comment.body}")

    # Google Chat integration with GitHub
    if EVENT_CHECK and GCHAT_WEBHOOK_URL:
        if EVENT_CHECK != 'stale':
            user=pr.user.login
            message="@" + user

        message = msg.get("default")
        message = msg.get(EVENT, message)

        if EVENT_CHECK == 'stale':
            message = '\n'.join(GCHAT_MESSAGE)
        else:
            for n in GCHAT_MESSAGE:
                message = message + '\n' + n

        response = send_message_to_google_chat(message, GCHAT_WEBHOOK_URL)
        print(response)

except Exception as e:
    print(f"Failed to run the job. Exception: {str(e)}")
