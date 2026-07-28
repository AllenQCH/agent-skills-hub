# GitHub personal repository deletion with OpenCLI

Use this note when Allen explicitly asks to delete one of his own GitHub repositories and wants the fastest browser-based path.

## Operating contract

- A message containing an exact `AllenQCH/<repo>` name or GitHub URL plus an explicit delete instruction is authorization.
- Do not add backup plans, architecture proposals, token schemes, or repeated confirmations unless the repository identity is ambiguous or Allen explicitly requests them.
- Keep status messages short. Do not send Allen looking for a background tab or hidden prompt.

## Bind-first procedure

1. Enumerate Chrome tabs and select the exact existing GitHub tab.
2. Run `opencli browser <session> bind`; do not start with `open`.
3. Verify the bound page is signed in as `AllenQCH`.
4. Navigate through the normal repository UI: `Settings` → `Danger Zone` → `Delete this repository`.
5. Complete GitHub's current confirmation steps using semantic labels and the exact `AllenQCH/<repo>` value.
6. Verify deletion in the authenticated browser: the repository URL should show `Page not found`, and the repository should disappear from `https://github.com/AllenQCH?tab=repositories`.

## Important distinction

- A new Chrome window does not necessarily mean a separate profile: verify the main Chrome PID/profile and page login state.
- `opencli browser <session> open` may create or lease another tab/window. `bind` attaches to the user's selected real tab.
- An OpenCLI session name is only a lease; it does not prove the intended tab was selected.

## Confirm access / sudo mode

GitHub may require sudo-mode reauthentication for repository deletion even when the normal login cookie is valid. Do not claim this can be bypassed. Also do not make it Allen's problem without first testing the normal UI path in the bound tab.

- Do not jump directly to the internal `/settings/delete` route during normal operation; it can surface `Confirm access` earlier than the standard UI flow.
- If normal UI deletion reaches `Confirm access`, record it as a server-side authentication boundary.
- Never expose, extract, log, or ask Allen to send passwords, cookies, CSRF tokens, or device codes.
- Browser deletion cannot be guaranteed unattended when GitHub requires fresh sudo mode; test this behavior with a disposable empty repository before standardizing it.

## Disposable experiment

When Allen asks to test feasibility:

1. Create a clearly disposable empty repo such as `opencli-delete-test`.
2. Bind the already-open GitHub tab.
3. Delete through the normal UI without direct internal URLs.
4. Record whether GitHub required fresh sudo mode.
5. Verify authenticated 404 and absence from the repository list.
6. Capture only the reusable outcome; never retain credentials or transient tokens.

## Verified result (2026-07-18)

A disposable empty public repository named `opencli-delete-test-20260718-122334` was created and deleted entirely through the bound `AllenQCH` Chrome session.

Observed deletion sequence:

1. Open repository `Settings` and wait until `Danger Zone` is fully loaded.
2. Click `Delete this repository`.
3. Click `I want to delete this repository`.
4. Click `I have read and understand these effects`.
5. Fill the confirmation field with exact `AllenQCH/<repo>`.
6. Click final `Delete this repository`.
7. GitHub redirected to `https://github.com/AllenQCH?tab=repositories` with the success message.
8. Revisiting the repository URL returned authenticated `Page not found`.

No `Confirm access`, password, passkey, or verification-code prompt appeared in this normal UI flow. For Allen's current Chrome session, OpenCLI deletion is therefore usable unattended while GitHub's sudo-mode state remains valid. Prefer semantic button names over numeric refs, because refs change between dialog stages.
