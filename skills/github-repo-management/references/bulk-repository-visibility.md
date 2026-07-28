# Bulk repository visibility changes

Use this workflow when Allen asks to make every repository under his personal GitHub account public or private.

## Safety and intent

- An explicit instruction such as “把所有 repository 全部设置为 public/private” authorizes the bulk visibility change for repositories owned by Allen's personal account.
- If the user reverses the desired visibility while work is in progress, stop the old plan immediately. Treat the newest instruction as authoritative, re-enumerate current state, and converge every owned repository to the new desired state.
- Restrict the operation to repositories whose owner exactly matches the authenticated personal account. Do not silently include organization repositories merely because the user can administer them.
- Enumerate first and change only mismatches. This reduces side effects and makes verification precise.

## Preferred path: authenticated GitHub API

1. Verify the authenticated login.
2. Enumerate all owned repositories with pagination (`affiliation=owner`, `per_page=100`).
3. Record `full_name`, visibility, fork status, and archived status.
4. Change only repositories whose visibility differs from the requested target.
5. Re-enumerate all owned repositories and require zero mismatches before reporting success.

Example enumeration:

```bash
gh api --paginate 'user/repos?affiliation=owner&per_page=100' \
  --jq '.[] | [.full_name,.visibility,(.fork|tostring),(.archived|tostring)] | @tsv'
```

For each mismatch:

```bash
gh repo edit OWNER/REPO --visibility public
# or
# gh repo edit OWNER/REPO --visibility private
```

## Browser fallback: reuse an authenticated Chrome session

Use this when `gh` is installed but no reusable API authentication is available and GitHub is already signed in within Chrome.

1. Follow the bind-first rules in `opencli-browser-webapp-exploration`. If binding cannot attach to the intended existing GitHub tab, open the target URL in the same authenticated Chrome profile and verify `meta[name=user-login]` before changing anything.
2. Enumerate the user's repository pages with page-context `fetch()` and `credentials: 'include'`. Parse `#user-repositories-list li`, and accept only links matching `^/OWNER/[^/]+$`.
3. Determine visibility from each repository row (`Private` or `Public`). Continue pagination until there is no next page.
4. For each mismatch, open `https://github.com/OWNER/REPO/settings` and use the normal **Change visibility** flow.
5. GitHub's current public-conversion dialog uses three confirmations:
   - `I want to make this repository public`
   - `I have read and understand these effects`
   - `Make this repository public`
   The equivalent private-conversion flow should be followed using the text rendered by the current UI rather than hard-coding assumptions.
6. A final confirmation may trigger an immediate page reload, so a page-context script can lose its queried button after the click. Treat that only as an indeterminate submission state; verify from a fresh repository listing instead of repeating the click blindly.

## Verification

Re-fetch every owned repository after the changes and calculate:

- total repository count;
- count at requested visibility;
- list of remaining mismatches;
- list of unknown/unparsed visibility states.

Report success only when both mismatch and unknown lists are empty. A concise completion report should state the total count, requested visibility count, zero mismatches, and which repositories were actually changed.

## Important public-visibility note

When private repositories become public, briefly remind the user that code, commit history, and relevant Actions history may become visible. Recommend a secrets/privacy audit, but do not turn an already completed and verified operation into a long security lecture.