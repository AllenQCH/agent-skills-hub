# Urban-village rental scouting near a commute anchor

Use this when the user is not asking for restaurants/POIs, but for **residential micro-areas** such as 城中村 / 新村 / 老社区 near an office, station, or landmark.

## Workflow

1. **Geocode the commute anchor**
   - Example: `python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/maps/scripts/maps_client.py search "深圳北站"`
   - Use the best station/building result as the anchor point.

2. **Build candidate residential-area queries**
   - Try nearby area names the user or local map context suggests, especially suffixes like:
     - `村`
     - `新村`
     - known local片区 names
   - Example candidate set around 深圳北:
     - `白石龙村 深圳 龙华区`
     - `樟坑村 深圳 龙华区`
     - `横岭 深圳 龙华区`
     - `南源新村 深圳 龙华区`
     - `民乐新村 深圳 龙华区`
     - `牛栏前 深圳 龙华区`

3. **Geocode each candidate name directly**
   - For residential micro-areas, direct name search is often more useful than generic POI search.
   - Keep the closest plausible residential/hamlet result.

4. **Measure from anchor to each candidate**
   - Use `distance` from the anchor to each candidate with `--mode walking`.
   - Prefer reporting **distance in km/m** and **relative direction**.
   - Treat ETA as secondary if it looks implausibly low/high for dense-city routing.

5. **Rank in tiers instead of pretending precision**
   - First tier: nearest / strongest fit for commute
   - Second tier: still reasonable but farther
   - Third tier: budget-driven backups

6. **Present as rental-scouting advice, not map trivia**
   - Give a short prioritized list with comments like:
     - closest / best first look
     - likely better value but farther
     - backup if budget matters more than commute

## Good output shape

- Short conclusion first
- Table: area, direction, straight-line distance, route distance, recommendation
- Then a suggested viewing order

## Example: Shenzhen North / 北站壹号

A practical first-pass shortlist produced from map-based scouting:
- 白石龙村
- 樟坑片区
- 横岭
- 南源新村
- 民乐新村
- 牛栏前

Suggested viewing order:
`白石龙村 → 樟坑 → 横岭 → 南源新村 → 民乐新村 → 牛栏前`

## Pitfalls

- Do not rely only on `nearby` POI categories; residential micro-areas may be better found by direct place-name search.
- Do not oversell route time; if the returned ETA looks unrealistic, anchor on distance and describe it as an estimate.
- For Chinese urban rentals, users usually want **recommended areas to inspect**, not only raw coordinates or links.
