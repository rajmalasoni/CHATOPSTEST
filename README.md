# GitHub Actions Workflow for PR Management using Docker,Python ,Bash script

This GitHub Actions workflow automates various tasks related to pull request (PR) management, such as checking for stale PRs, enforcing certain rules, and responding to slash commands.

## Workflow Overview

The workflow is triggered by different events, including stale PR checks, pull request updates, and slash commands. It performs a series of actions based on the event type and the configured rules.

## Workflow Components

### 1. **Environment Setup**
   - Uses GitHub token for authentication.
   - Retrieves necessary environment variables like repository name, PR number, event type, etc.

### 2. **Messages for Google Chat Notifications**
   - Defines messages to be sent to Google Chat for various events such as stale PRs, PR closures, approvals, etc.

### 3. **Event Handling**
   - Handles events based on the workflow type (`stale`, `pull`, `slash`).
   - Checks for stale PRs, enforces rules for PR targets and descriptions, checks for existing tags, and responds to slash commands.

### 4. **Google Chat Integration**
   - Sends notifications to Google Chat based on the event and associated actions.

### 5. **Error Handling**
   - Catches and prints any exceptions that occur during workflow execution.

## Usage

To use this workflow in your repository:
1. Copy the provided code into a `.github/workflows` directory in your repository.
2. Configure the required environment variables such as `GITHUB_TOKEN`, `REPO_NAME`, `WEBHOOK`, etc., either in GitHub Secrets or directly in the workflow file.
3. Customize the workflow as needed, such as adjusting the stale PR days, specifying message templates, etc.

## Notes

- Make sure to review and test the workflow thoroughly before enabling it in your repository.
- Ensure that the necessary permissions are granted to the GitHub token used by the workflow.
- Update the workflow and messages according to your specific requirements and workflow policies.
