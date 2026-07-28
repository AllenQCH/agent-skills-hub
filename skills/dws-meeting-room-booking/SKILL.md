---
name: dws-meeting-room-booking
description: Use when Allen wants to use dws to find, book, change, or cancel DingTalk meeting rooms. Covers required inputs, room availability search, event creation, room add, verification, and safe rollback/error handling. Do not use for non-Lark/Feishu/DingTalk/OpenClaw-import workflows or tasks covered by a narrower platform skill.
license: MIT
metadata:
  hermes:
    tags:
    - dws
    - dingtalk
    - calendar
    - meeting-room
    - booking
    related_skills:
    - dws
---

# DWS Meeting Room Booking

## Overview

Use this skill when the user asks to book a DingTalk meeting room with `dws`, e.g. “帮我订会议室”, “找个会议室”, “约会议室”, “取消会议室”, or “改会议室/改时间”.

The safe booking path is always:

1. Normalize the requested time to ISO-8601 with timezone.
2. Search available rooms for that time.
3. Create or locate the calendar event.
4. Add the selected room to the event.
5. Read back the event/room state and report concrete evidence.

Always use `dws` for DingTalk operations and always request JSON output with `--format json`.

## When to Use

Use this skill when:

- The user wants to reserve a DingTalk meeting room.
- The user wants available meeting-room options for a specific time.
- The user wants to add a meeting room to an existing event.
- The user wants to change or cancel a room booking.
- The user asks for a day’s free slots for one or more rooms.

Do not use this skill for:

- Feishu/Lark calendar rooms — use the Lark calendar workflow instead.
- Non-calendar room/resource booking systems.
- Generic meeting notes or meeting summaries.

## Required Inputs

Before creating a real booking, make sure these are known:

| Input | Required? | Notes |
|---|---:|---|
| Date | Yes | If relative, resolve using the live date/time via `date`; default timezone is `Asia/Shanghai` / `+08:00`. |
| Start/end time or duration | Yes | If only start time is given, ask for duration unless there is a clear user/default convention in context. |
| Meeting title | Preferred | If missing and the user explicitly asks to book immediately, use `会议`; otherwise ask. |
| Room preference | Preferred | Building/floor/capacity/name. If absent, search all or root group, then offer options unless user says “随便/自动找一个”. |
| Attendees | Optional | If names are given, resolve to user IDs via `dws contact user search`. |
| Existing event ID | Optional | Needed when adding a room to an existing event instead of creating a new event. |

## Command Rules

- Every `dws` command must include `--format json` unless the command is pure `--help`.
- For boolean flags, pass explicit values where supported: `--available true`, not a bare `--available`.
- Do not invent `eventId`, `roomId`, `groupId`, or `userId`. Extract them from command results.
- If a command fails, retry once with `--verbose --format json`. If stderr contains `RECOVERY_EVENT_ID=...`, follow the `dws` recovery workflow.
- Creating an event and adding a room is allowed when the user explicitly asked to book and all required inputs are present.
- Deleting an event or removing a room is destructive/high-impact: summarize the operation and get explicit user confirmation before running delete commands with `--yes`.

## Quick Commands

### Auth check

```bash
dws auth status --format json
```

### Search room groups

Use this when room search is too broad, returns too many rooms, or the user specifies a campus/building/floor.

```bash
dws calendar room list-groups --format json
```

Then choose `groupId` from the returned groups.

### Search available rooms

```bash
dws calendar room search \
  --start "2026-07-21T14:00:00+08:00" \
  --end "2026-07-21T15:00:00+08:00" \
  --available true \
  --format json
```

With group:

```bash
dws calendar room search \
  --start "2026-07-21T14:00:00+08:00" \
  --end "2026-07-21T15:00:00+08:00" \
  --group-id "95" \
  --available true \
  --format json
```

### Resolve attendees by name

```bash
dws contact user search --query "张三" --format json
```

Extract the correct `userId`; if multiple people match and the identity is ambiguous, ask the user to choose.

### Create an event

```bash
dws calendar event create \
  --title "项目同步会" \
  --start "2026-07-21T14:00:00+08:00" \
  --end "2026-07-21T15:00:00+08:00" \
  --timezone "Asia/Shanghai" \
  --desc "由 Hermes 通过 dws 创建" \
  --format json
```

If attendees are known, pass them at creation time if supported by the current `dws` version:

```bash
dws calendar event create \
  --title "项目同步会" \
  --start "2026-07-21T14:00:00+08:00" \
  --end "2026-07-21T15:00:00+08:00" \
  --timezone "Asia/Shanghai" \
  --attendees "userId1,userId2" \
  --format json
```

If attendee creation fails or is unsupported, create the event first, then add participants:

```bash
dws calendar participant add \
  --event "<EVENT_ID>" \
  --users "userId1,userId2" \
  --format json
```

### Add the room to the event

```bash
dws calendar room add \
  --event "<EVENT_ID>" \
  --rooms "<ROOM_ID>" \
  --format json
```

### Verify booking

```bash
dws calendar event get --id "<EVENT_ID>" --format json
dws calendar room search \
  --start "2026-07-21T14:00:00+08:00" \
  --end "2026-07-21T15:00:00+08:00" \
  --group-id "<GROUP_ID>" \
  --available true \
  --format json
```

The booked room should no longer appear in the available-room result for the same time window, or the event detail should show the room/resource association depending on API output shape.

## Default Booking Workflow

### 1. Normalize the request

- Convert “今天/明天/下周三/下午两点” to an exact `YYYY-MM-DDTHH:MM:SS+08:00` time.
- Use the live system date for relative dates:

```bash
date '+%Y-%m-%d %H:%M:%S %Z %z'
```

- If the end time is missing, ask the user for duration unless a clear convention was provided.

### 2. Discover room scope

If the user names a location/floor, run:

```bash
dws calendar room list-groups --format json
```

Find the closest group by name. Do not hard-code group IDs, even if a previous session observed one.

### 3. Search availability

Run `room search` with `--available true`. If the root search errors due to too many rooms, fall back to group discovery and query one or more likely groups.

Filter candidates by:

1. Exact room name if specified.
2. Building/campus/floor/group preference.
3. Capacity, if available in the response.
4. User preference such as “近一点 / 随便 / 大一点 / 有电视”.

### 4. Choose room safely

| Situation | Behavior |
|---|---|
| User specified exact room and it is available | Book it. |
| User said “随便/自动找一个/帮我挑” | Pick the best matching available room and book it. |
| Multiple plausible rooms, no auto-pick instruction | Present 2-5 options and ask the user to choose. |
| No room is available | Report no availability and offer adjacent time slots or nearby groups. |

### 5. Create event, then add room

Creating a DingTalk calendar event does not automatically reserve a room. Always add the room explicitly with `dws calendar room add` after the event exists.

Extract `eventId` from `event create`; extract `roomId` from `room search`; then call `room add`.

### 6. Verify and report

After adding the room, verify with `event get` and/or a repeated availability search. Final response should include:

| Field | Value |
|---|---|
| 状态 | 已预定 / 未预定 / 需要选择 |
| 时间 | Exact start-end with timezone |
| 会议室 | Name + roomId if available |
| 日程 | Title + eventId |
| 参会人 | Added / not added / ambiguous |
| 验证 | Which command/result confirmed it |

## Existing Event Workflow

If the user gives an existing event ID or says “给这个会加个会议室”:

1. Fetch the event:
   ```bash
   dws calendar event get --id "<EVENT_ID>" --format json
   ```
2. Extract event start/end time.
3. Search available rooms for that exact window.
4. Add the selected room:
   ```bash
   dws calendar room add --event "<EVENT_ID>" --rooms "<ROOM_ID>" --format json
   ```
5. Verify with `event get`.

## Release / Cancel Meeting Rooms

Releasing a room means removing that room from an existing event while keeping the event and any other rooms.

When Allen explicitly says to release/cancel booked rooms for a date (for example “把我订的今天的会议室全部释放掉”), treat that as authorization for the room-release operation. Do not stop for a second confirmation unless the operation would delete the calendar event itself or remove participants.

1. Normalize the target date and list that day’s events:
   ```bash
   dws calendar event list \
     --start "YYYY-MM-DDT00:00:00+08:00" \
     --end "YYYY-MM-DDT23:59:59+08:00" \
     --format json
   ```
2. For each candidate event, read detail and inspect `meetingRooms`:
   ```bash
   dws calendar event get --id "<EVENT_ID>" --format json
   ```
3. If `meetingRooms` contains room IDs, remove those rooms only:
   ```bash
   dws calendar room delete \
     --event "<EVENT_ID>" \
     --rooms "<ROOM_ID[,ROOM_ID2]>" \
     --yes \
     --format json
   ```
4. If `meetingRooms` is already empty but the event title/description clearly records a room from a previous booking attempt, and you have a trustworthy `roomId` from the same session or prior booking evidence, it is safe to call `room delete` with that `roomId` as an idempotent release attempt. Still verify afterward; do not claim a room was occupied unless the read-back showed it.
5. Verify by reading the event again:
   ```bash
   dws calendar event get --id "<EVENT_ID>" --format json
   ```
6. Success means `result.meetingRooms` is empty or the removed rooms are absent, while the event itself remains present.

For multiple rooms, pass comma-separated room IDs to `--rooms`, but still keep the batch under 30 IDs. Deleting the event is a separate destructive action; only do it when Allen explicitly asks to delete/cancel the calendar event, not merely release the room.

## Change, Release, or Delete Room/Event

Changing room/time can affect attendees and room reservations.

- For changing time: update the event first, then re-search room availability and add/re-add the room.
- For changing room: add the new room first if API permits; then remove the old room only after explicit confirmation if removal is required.
- **Allen-specific wording convention:** when Allen says “删除会议室”, interpret it as deleting the corresponding calendar event, not merely removing the room resource. When he says “释放会议室 / 不用这个会议室”, treat the likely intent as canceling the related room booking by deleting the related event unless he explicitly says “只移除会议室，保留日程”.
- Before destructive execution, first identify the exact event(s) and room(s) from live calendar data. If the target is ambiguous, ask for the minimum disambiguation. If the current message already gives an exact target or the conversation context uniquely identifies the event, proceed with the appropriate delete and verify by reading the event/list state back.
- For removing only the room resource or deleting the whole event, use:

```bash
# Only remove the room from an event; use only when Allen explicitly wants to keep the calendar event.
dws calendar room delete --event "<EVENT_ID>" --rooms "<ROOM_ID>" --yes --format json

# Delete the whole event; default for Allen's “删除会议室” wording.
dws calendar event delete --id "<EVENT_ID>" --yes --format json
```

## Booking Horizon / How Far Ahead Rooms Can Be Booked

When the user asks “会议室最远可以订到哪天/周几”, use read-only probes; do not create throwaway bookings unless the user explicitly authorizes test events.

Recommended probe:

1. Use the live date/time:
   ```bash
   date '+%Y-%m-%d %H:%M:%S %Z %z'
   ```
2. Query a known group and representative one-hour windows day by day:
   ```bash
   dws calendar room search \
     --start "YYYY-MM-DDT19:00:00+08:00" \
     --end "YYYY-MM-DDT20:00:00+08:00" \
     --group-id "<GROUP_ID>" \
     --available true \
     --format json
   ```
3. Treat a normal result containing `roomName`/`roomId` as an actionable bookable window. Treat `result: [{"labels": null}]` as a placeholder/no actionable room result.
4. Confirm the boundary by probing several times on the last good date and first bad date, including late-night slots around midnight.

Observed for 喜茶前海新总部 (`groupId=95`) on 2026-07-21 18:20 CST: usable room-search results existed through 2026-07-27 Monday 22:00-23:00, while 2026-07-27 23:00-24:00 and all tested 2026-07-28 Tuesday slots returned only the placeholder `[{"labels": null}]`. So the practical booking horizon appeared to be through the following Monday. Re-probe live before relying on this because org policy or current time can change.

## Full-Day Room Availability

When the user asks “某个会议室今天/明天哪些时间空”, do not query one long window and treat that as the answer. Long windows can produce placeholder structures.

Use 30-minute slot scanning:

1. Determine the target date, group, and target room names.
2. Loop over 30-minute intervals, for example 09:00-20:00.
3. For each slot, call:
   ```bash
   dws calendar room search \
     --start "2026-07-21T09:00:00+08:00" \
     --end "2026-07-21T09:30:00+08:00" \
     --group-id "<GROUP_ID>" \
     --available true \
     --format json
   ```
4. A room is free in that slot if its `roomName` appears in the available-room response.
5. Merge continuous 30-minute slots into readable ranges.

## Error Handling

| Symptom | Likely Cause | Action |
|---|---|---|
| `not_authenticated`, token errors | dws auth expired or wrong config context | Run `dws auth status --format json`; if invalid, tell user to login or run `dws auth login` if interactive auth is possible. |
| More than 100 rooms / search too broad | Need group-scoped search | Run `room list-groups`, choose likely group, retry with `--group-id`. |
| Room not found | Wrong group or room name mismatch | Search groups and broaden query; present candidates. |
| Room add fails after event create | Room became unavailable, `room search` was stale/ambiguous, or permission issue | Do not claim success. Preserve the created `eventId`, report the failed room(s), re-check alternatives, and ask whether to delete the now roomless event before running `event delete --yes`. |
| `room search` returns `[{"labels": null}]` | No usable rooms returned or output shape is placeholder | Treat as no actionable available-room result; do not extract IDs from it. Try a narrower group/time, known room IDs, or ask for a different slot. |
| Ambiguous attendee name | Multiple user matches | Ask user to disambiguate before inviting. |
| `RECOVERY_EVENT_ID=...` in stderr | dws recovery snapshot available | Follow the dws recovery commands before giving up. |

## Common Pitfalls

1. **Creating only the event and forgetting the room.** Event creation is not room reservation; always call `calendar room add`.
2. **Using bare `--available`.** Current help exposes it as a string flag; use `--available true`.
3. **Guessing IDs.** `groupId`, `roomId`, `eventId`, and `userId` must come from JSON output.
4. **Assuming root room search is complete.** Large orgs often require group-scoped search.
5. **Skipping verification.** Always read back event detail or re-run availability search after booking.
6. **Trusting room search more than booking.** `room search` can return stale/placeholder results; `room add` plus `event get.meetingRooms` is the authoritative success check.
7. **Confusing room release with event deletion.** “释放会议室/取消会议室” means `calendar room delete` and keep the calendar event unless Allen explicitly asks to delete the event.
8. **Assuming an empty `meetingRooms` means no release action is needed.** If the event description/title records a room and you have the exact historical `roomId`, an idempotent `room delete --yes` followed by `event get` is an acceptable cleanup/verification step.
9. **Leaving orphan events after a failed room add.** If an event was created but no room was added, report the event ID and ask before deleting it.
10. **Deleting without confirmation.** `event delete`, participant removal, and ambiguous destructive changes require explicit confirmation; explicit “release today’s meeting rooms” is sufficient authorization for room release only.

## Verification Checklist

- [ ] Loaded the `dws` skill or followed its global rules.
- [ ] Used `--format json` for every dws operation.
- [ ] Time is exact ISO-8601 with `+08:00` or timezone supplied.
- [ ] Room availability was checked before booking.
- [ ] Event was created or existing event was fetched.
- [ ] Room was added with a real `roomId` and `eventId`.
- [ ] Booking was verified with `event get` and/or repeated availability search.
- [ ] Final response includes event ID, room name, time, and verification evidence.
