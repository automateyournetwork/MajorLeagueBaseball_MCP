import logging
import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MLBMCPServer")

# HTTP Client setup
@asynccontextmanager
async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

# Global variables
MLB_BASE = "https://statsapi.mlb.com/api/v1"
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# --- FastMCP Server ---
mcp = FastMCP("MLB Server")

# HTTP client instance
http_client = httpx.AsyncClient()

# ------------------------------- Tool Input Schemas -------------------------------

class TeamsForYearInput(BaseModel):
    year: int

class TeamRosterInput(BaseModel):
    team_id: str
    year: int

class PlayerStatsInput(BaseModel):
    player_id: str
    year: int
    position: str  # 'P' or any other

class ScheduleByDateInput(BaseModel):
    date: str  # Format: YYYY-MM-DD

class BoxscoreInput(BaseModel):
    game_pk: int
    year: int
    team_id: str
    game_date: str  # Format: YYYY-MM-DD

class StandingsInput(BaseModel):
    season: int
    league_id: int  # e.g., 103 = AL, 104 = NL

class PlayerBioInput(BaseModel):
    player_id: str

class TeamScheduleInput(BaseModel):
    team_id: str
    season: int

class GameContentInput(BaseModel):
    game_pk: int

class LeagueLeadersInput(BaseModel):
    category: str  # e.g., "homeRuns", "strikeOuts"
    season: int

class AwardsInput(BaseModel):
    season: int

class VenuesInput(BaseModel):
    season: int

class AttendanceInput(BaseModel):
    season: Optional[int] = Field(None, description="MLB season year (e.g., 2023)")
    teamId: Optional[int] = Field(None, description="Team ID to filter attendance by team")
    date: Optional[str] = Field(None, description="Specific date (YYYY-MM-DD)")

class AwardWinnersInput(BaseModel):
    award_id: str  # e.g., "mlb-mvp"
    season: int     # e.g., 2023

class DivisionsInput(BaseModel):
    season: Optional[int] = Field(None, description="Filter divisions by MLB season (e.g., 2023)")

class DraftInput(BaseModel):
    year: Optional[int] = Field(None, description="MLB Draft year (e.g., 2023)")
    round: Optional[int] = Field(None, description="Draft round number")
    name: Optional[str] = Field(None, description="Player name to filter by")
    school: Optional[str] = Field(None, description="School name filter")
    state: Optional[str] = Field(None, description="U.S. state filter")
    country: Optional[str] = Field(None, description="Country filter")
    position: Optional[str] = Field(None, description="Player position filter")
    teamId: Optional[int] = Field(None, description="MLB team ID")
    playerId: Optional[int] = Field(None, description="MLB player ID")
    bisPlayerId: Optional[int] = Field(None, description="BIS player ID")
    latest: Optional[bool] = Field(False, description="Return latest draft data (no filters allowed)")
    prospects: Optional[bool] = Field(False, description="Show top draft prospects")

class GameChangesInput(BaseModel):
    updatedSince: str = Field(..., description="ISO 8601 timestamp to check for updates (e.g., 2024-08-01T00:00:00Z)")
    sportId: Optional[int] = Field(1, description="Sport ID (default is 1 for MLB)")
    gameType: Optional[str] = Field(None, description="Game type code (e.g., 'R' for regular season)")
    season: Optional[int] = Field(None, description="MLB season year")
    fields: Optional[str] = Field(None, description="Comma-separated list of fields to include")

class GameContextMetricsInput(BaseModel):
    gamePk: int = Field(..., description="The unique game ID (gamePk) to retrieve context metrics for.")
    timecode: Optional[str] = Field(None, description="Optional timecode for filtering metrics (e.g., 2023-06-01T19:30:00Z).")

class GameLinescoreInput(BaseModel):
    gamePk: str = Field(..., description="The gamePk identifier for the MLB game.")
    timecode: Optional[str] = Field(None, description="Optional ISO timestamp to filter linescore entries.")

class GameUniformsInput(BaseModel):
    gamePks: str = Field(..., description="Comma-separated list of gamePks to retrieve uniform information for.")
    fields: Optional[str] = Field(None, description="Optional comma-separated list of fields to include in the response.")

class GamePaceInput(BaseModel):
    season: str = Field(..., description="Season year (e.g., 2023)")
    teamIds: Optional[str] = Field(None, description="Comma-separated team IDs (e.g., 141,147)")
    leagueIds: Optional[str] = Field(None, description="Comma-separated league IDs (e.g., 103,104)")
    leagueListId: Optional[str] = Field(None, description="League list ID (e.g., mlb)")
    gameType: Optional[str] = Field(None, description="Game type code (R=Regular, P=Postseason, etc.)")
    startDate: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    endDate: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    venueIds: Optional[str] = Field(None, description="Comma-separated venue IDs")
    orgType: Optional[str] = Field(None, description="Org type filter")
    includeChildren: Optional[bool] = Field(None, description="Include child orgs")
    fields: Optional[str] = Field(None, description="Fields to include in the response")

class HighLowPlayerInput(BaseModel):
    sortStat: str = Field(..., description="Stat to sort by, e.g. homeRuns, era")
    season: str = Field(..., description="Season year, e.g. 2023")
    statGroup: Optional[str] = Field("hitting", description="Stat group: hitting, pitching, or fielding")
    gameType: Optional[str] = Field(None, description="Game type code, e.g. R for regular season")
    leagueId: Optional[int] = Field(None, description="League ID to filter by")
    sportIds: Optional[str] = Field("1", description="Comma-separated list of sport IDs (1 for MLB)")
    teamId: Optional[int] = Field(None, description="Filter to a specific team ID")
    limit: Optional[int] = Field(5, description="Number of results to return")

class HighLowTeamInput(HighLowPlayerInput):
    pass  # Same fields reused

class AllStarBallotInput(BaseModel):
    leagueId: str = Field(..., description="League ID (e.g., 103 for AL, 104 for NL)")
    season: str = Field(..., description="Season year (e.g., 2023)")

class AllStarWriteInsInput(AllStarBallotInput):
    pass # Reusing the same fields

class AllStarFinalVoteInput(AllStarBallotInput):
    pass # Reusing the same fields

class PeopleFreeAgentsInput(BaseModel):
    leagueId: str = Field(..., description="League ID (e.g., 103 for AL, 104 for NL)")
    order: Optional[str] = Field(None, description="Sort order like 'name.asc' or 'position.desc'")
    hydrate: Optional[str] = Field(None, description="Optional hydration parameter to include related data")
    fields: Optional[str] = Field(None, description="Optional fields filter to reduce payload size")
    season: str = Field(..., description="Season year (e.g., 2023)")

class JobsUmpiresInput(BaseModel):
    sportId: Optional[str] = Field("1", description="Sport ID (default is 1 for baseball)")
    date: Optional[str] = Field(None, description="Game date in YYYY-MM-DD format")
    fields: Optional[str] = Field(None, description="Optional fields filter")

class JobsDatacastersInput(JobsUmpiresInput):
    pass  # Reusing the same fields

class JobsOfficialScorersInput(BaseModel):
    timecode: Optional[str] = Field(None, description="Optional timecode to filter scorers (format unknown; possibly timestamp or string)")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to include in the response")

class ScheduleTiedGamesInput(BaseModel):
    season: str = Field(..., description="Season year, e.g., '2023'")
    gameTypes: Optional[str] = Field(None, description="Optional comma-separated game types (e.g., 'R', 'S')")
    hydrate: Optional[str] = Field(None, description="Optional hydrate fields for expanded data")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to include in the response")

class SchedulePostseasonInput(BaseModel):
    gameTypes: Optional[str] = Field(None, description="Comma-separated list of game types (e.g., 'D', 'F', 'L', 'W')")
    seriesNumber: Optional[str] = Field(None, description="Optional series number filter (e.g., '1', '2')")
    teamId: Optional[int] = Field(None, description="Team ID to filter postseason games by team")
    sportId: Optional[int] = Field(None, description="Sport ID (1 for baseball)")
    season: Optional[str] = Field(None, description="Season year, e.g., '2023'")
    hydrate: Optional[str] = Field(None, description="Optional hydrate fields for expanded data")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to include in the response")

class SchedulePostseasonSeriesInput(BaseModel):
    gameTypes: Optional[str] = Field(None, description="Comma-separated game types (e.g., 'D', 'F', 'L', 'W')")
    seriesNumber: Optional[str] = Field(None, description="Series number (e.g., '1', '2') to filter by round")
    teamId: Optional[int] = Field(None, description="Team ID to filter postseason series for a specific team")
    sportId: Optional[int] = Field(None, description="Sport ID (1 for baseball)")
    season: Optional[str] = Field(None, description="Season year, e.g., '2023'")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to limit the response")

class SeasonsInput(BaseModel):
    season: Optional[str] = Field(None, description="Year to filter by (e.g., '2023')")
    all: Optional[bool] = Field(False, description="Set to True to return all seasons (defaults to False)")
    leagueId: Optional[int] = Field(None, description="Optional League ID (103 = NL, 104 = AL)")
    divisionId: Optional[int] = Field(None, description="Optional Division ID")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to include in the response")

class SeasonByIdInput(BaseModel):
    seasonId: str = Field(..., description="The ID of the season (e.g., '2023')")
    fields: str | None = Field(None, description="Optional comma-separated fields to include in the response")

class MLBStatsInput(BaseModel):
    stats: str = Field(..., description="Stat type (e.g., 'season', 'career', 'game', 'yearByYear')")
    group: str = Field(..., description="Stat group (e.g., 'hitting', 'pitching', 'fielding')")
    playerPool: Optional[str] = Field(None, description="Player pool to filter by (e.g., 'all', 'qualified')")
    position: Optional[str] = Field(None, description="Player position to filter by (e.g., '1B', 'P')")
    teamId: Optional[int] = Field(None, description="Team ID to filter by")
    leagueId: Optional[int] = Field(None, description="League ID (103 = AL, 104 = NL)")
    sportIds: Optional[str] = Field("1", description="Sport ID(s), default is '1' for MLB")
    gameType: Optional[str] = Field(None, description="Game type (e.g., 'R' for regular, 'P' for postseason)")
    season: Optional[str] = Field(None, description="Season year (e.g., '2023')")
    sortStat: Optional[str] = Field(None, description="Stat field to sort by")
    order: Optional[str] = Field(None, description="'asc' or 'desc' for sorting")
    limit: Optional[int] = Field(50, description="Limit number of results (default 50)")
    offset: Optional[int] = Field(0, description="Offset for pagination")
    hydrate: Optional[str] = Field(None, description="Optional hydration fields")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to return")
    personId: Optional[str] = Field(None, description="Specific player ID or IDs")
    metrics: Optional[str] = Field(None, description="Advanced metrics to include")
    startDate: Optional[str] = Field(None, description="Start date filter (YYYY-MM-DD)")
    endDate: Optional[str] = Field(None, description="End date filter (YYYY-MM-DD)")

class TeamHistoryInput(BaseModel):
    teamIds: str = Field(..., description="Comma-separated list of team IDs (e.g., '121', '147')")
    startSeason: Optional[str] = Field(None, description="Start season year (e.g., '2000')")
    endSeason: Optional[str] = Field(None, description="End season year (e.g., '2023')")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to include")

class TeamStatsInput(BaseModel):
    season: str = Field(..., description="Season year (e.g., '2023')")
    group: str = Field(..., description="Stat group (e.g., 'hitting', 'pitching', 'fielding')")
    stats: str = Field(..., description="Stat type (e.g., 'season', 'vsTeam', 'homeAndAway')")
    gameType: Optional[str] = Field(None, description="Game type (e.g., 'R' for regular, 'P' for postseason)")
    order: Optional[str] = Field(None, description="'asc' or 'desc' sort order")
    sortStat: Optional[str] = Field(None, description="Stat to sort by (e.g., 'homeRuns', 'era')")
    fields: Optional[str] = Field(None, description="Comma-separated fields to include")
    startDate: Optional[str] = Field(None, description="Start date filter (YYYY-MM-DD)")
    endDate: Optional[str] = Field(None, description="End date filter (YYYY-MM-DD)")

class TeamAffiliatesInput(BaseModel):
    teamIds: str = Field(..., description="Comma-separated list of MLB team IDs (e.g., '121')")
    season: Optional[str] = Field(None, description="Season year to get historical affiliations")
    hydrate: Optional[str] = Field(None, description="Hydration options")
    fields: Optional[str] = Field(None, description="Comma-separated response fields")

class TeamAlumniInput(BaseModel):
    teamId: str = Field(..., description="Team ID (e.g., '147' for Yankees)")
    season: str = Field(..., description="Season year to fetch alumni stats for (e.g., '2023')")
    group: str = Field(..., description="Stat group (e.g., 'hitting', 'pitching')")
    hydrate: Optional[str] = Field(None, description="Optional hydration fields")
    fields: Optional[str] = Field(None, description="Comma-separated list of fields to return")

class TeamCoachesInput(BaseModel):
    teamId: str = Field(..., description="MLB team ID (e.g., '147' for Yankees)")
    season: Optional[str] = Field(None, description="Season year (e.g., '2023')")
    date: Optional[str] = Field(None, description="Specific date (YYYY-MM-DD)")
    fields: Optional[str] = Field(None, description="Comma-separated list of response fields to include")

class TeamPersonnelInput(TeamCoachesInput):
    pass  # Reusing the same fields

class TeamLeadersInput(BaseModel):
    teamId: str = Field(..., description="MLB team ID (e.g., '147' for Yankees)")
    leaderCategories: str = Field(..., description="Comma-separated stat categories (e.g., 'homeRuns,battingAverage')")
    season: str = Field(..., description="Season year (e.g., '2023')")
    leaderGameTypes: Optional[str] = Field(None, description="Game types to include (e.g., 'R', 'P')")
    hydrate: Optional[str] = Field(None, description="Hydration options")
    limit: Optional[int] = Field(None, description="Limit number of results per category")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields")

class TeamStatsByIdInput(BaseModel):
    teamId: str = Field(..., description="Team ID (e.g., '147')")
    season: str = Field(..., description="Season year (e.g., '2023')")
    group: str = Field(..., description="Stat group (e.g., 'hitting', 'pitching')")
    stats: Optional[str] = Field(None, description="Stat type (e.g., 'season', 'statSplits')")
    gameType: Optional[str] = Field(None, description="Game type filter (e.g., 'R', 'P')")
    sportIds: Optional[str] = Field("1", description="Sport ID (MLB is 1)")
    sitCodes: Optional[str] = Field(None, description="Situational codes (e.g., 'vsLeft', 'home')")
    fields: Optional[str] = Field(None, description="Comma-separated fields to return")

class TeamUniformsInput(BaseModel):
    teamIds: str = Field(..., description="Comma-separated list of team IDs (e.g., '121')")
    season: Optional[str] = Field(None, description="Optional season year to filter uniforms (e.g., '2023')")
    fields: Optional[str] = Field(None, description="Optional comma-separated fields to limit the response")

class TransactionsInput(BaseModel):
    teamId: Optional[str] = Field(None, description="Team ID (e.g., '121')")
    playerId: Optional[str] = Field(None, description="Player ID to track")
    date: Optional[str] = Field(None, description="Exact date (YYYY-MM-DD)")
    startDate: Optional[str] = Field(None, description="Start of date range (YYYY-MM-DD)")
    endDate: Optional[str] = Field(None, description="End of date range (YYYY-MM-DD)")
    fields: Optional[str] = Field(None, description="Comma-separated fields to include in the response")

# ------------------------------- Tool Implementations -------------------------------

@mcp.tool(description="Get all MLB teams for a given season.")
async def mlb_get_all_teams(params: TeamsForYearInput) -> Dict[str, Any]:
    query_params = {"sportId": 1, "season": params.year}
    res = await http_client.get(f"{MLB_BASE}/teams", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get the team roster for a given season.")
async def mlb_get_team_roster(params: TeamRosterInput) -> Dict[str, Any]:
    query_params = {"season": params.year}
    res = await http_client.get(f"{MLB_BASE}/teams/{params.team_id}/roster", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get player stats for a season by position.")
async def mlb_get_player_stats(params: PlayerStatsInput) -> Dict[str, Any]:
    stat_group = "pitching" if params.position.upper() == "P" else "hitting"
    query_params = {"stats": "season", "group": stat_group, "season": params.year}
    res = await http_client.get(f"{MLB_BASE}/people/{params.player_id}/stats", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all MLB games scheduled on a specific date (YYYY-MM-DD).")
async def mlb_get_schedule_by_date(params: ScheduleByDateInput) -> Dict[str, Any]:
    query_params = {"sportId": 1, "date": params.date}
    res = await http_client.get(f"{MLB_BASE}/schedule", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Fetch boxscore statistics for a specific game using gamePk.")
async def mlb_get_boxscore(params: BoxscoreInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/game/{params.game_pk}/boxscore", headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get MLB standings by season and league ID (103 = AL, 104 = NL).")
async def mlb_get_standings(params: StandingsInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/standings", params=params.model_dump(), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get biographical information for a player using player ID.")
async def mlb_get_player_bio(params: PlayerBioInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/people/{params.player_id}", headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all scheduled games for a team in a given season.")
async def mlb_get_team_schedule(params: TeamScheduleInput) -> Dict[str, Any]:
    query_params = {"sportId": 1, "teamId": params.team_id, "season": params.season}
    res = await http_client.get(f"{MLB_BASE}/schedule", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Fetch game content (e.g., highlights, media) for a game using gamePk.")
async def mlb_get_game_content(params: GameContentInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/game/{params.game_pk}/content", headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get league leaders by stat category and season (e.g., homeRuns, strikeOuts).")
async def mlb_get_league_leaders(params: LeagueLeadersInput) -> Dict[str, Any]:
    query_params = {"leaderCategories": params.category, "season": params.season, "sportId": 1}
    res = await http_client.get(f"{MLB_BASE}/stats/leaders", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all MLB awards for a given season.")
async def mlb_get_awards(params: AwardsInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/awards", params=params.model_dump(), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all MLB venues (stadiums), past and present.")
async def mlb_get_venues(params: VenuesInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/venues", params=params.model_dump(), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get attendance data for teams or leagues by season or date.")
async def mlb_get_attendance(params: AttendanceInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["leagueListId"] = "mlb"
    res = await http_client.get(f"{MLB_BASE}/attendance", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get award winners for a specific award ID and season.")
async def mlb_get_award_winners(params: AwardWinnersInput) -> Dict[str, Any]:
    query_params = {"season": params.season, "sportId": 1}
    res = await http_client.get(f"{MLB_BASE}/awards/{params.award_id}/recipients", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get a list of all MLB divisions, optionally filtered by season.")
async def mlb_get_divisions(params: DivisionsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportId"] = 1
    res = await http_client.get(f"{MLB_BASE}/divisions", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get MLB Draft data, including player information and team selections.")
async def mlb_get_draft(params: DraftInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'year'})
    res = await http_client.get(f"{MLB_BASE}/draft/{params.year}", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Retrieve games that have changed status or details since a specific timestamp.")
async def mlb_get_game_changes(params: GameChangesInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    res = await http_client.get(f"{MLB_BASE}/game/changes", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get context metrics for a specific game using gamePk.")
async def mlb_get_game_context_metrics(params: GameContextMetricsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'gamePk'})
    res = await http_client.get(f"{MLB_BASE}/game/{params.gamePk}/contextMetrics", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get the linescore for a specific game using gamePk.")
async def mlb_get_game_linescore(params: GameLinescoreInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'gamePk'})
    res = await http_client.get(f"{MLB_BASE}/game/{params.gamePk}/linescore", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get uniform information for a specific game using gamePks.")
async def mlb_get_game_uniforms(params: GameUniformsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    res = await http_client.get(f"{MLB_BASE}/uniforms/game", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get game pace data for a specific season and optional filters.")
async def mlb_get_game_pace(params: GamePaceInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportId"] = 1
    res = await http_client.get(f"{MLB_BASE}/gamePace", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get high/low player stats for a specific season and stat group.")
async def mlb_get_highlow_players(params: HighLowPlayerInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportIds"] = 1
    res = await http_client.get(f"{MLB_BASE}/highLow/player", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get high/low team stats for a specific season and stat group.")
async def mlb_get_highlow_teams(params: HighLowTeamInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportIds"] = 1
    res = await http_client.get(f"{MLB_BASE}/highLow/team", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get All-Star ballot information for a specific league and season.")
async def mlb_get_all_star_ballot(params: AllStarBallotInput) -> Dict[str, Any]:
    query_params = {"season": params.season}
    res = await http_client.get(f"{MLB_BASE}/league/{params.leagueId}/allStarBallot", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get All-Star write-in information for a specific league and season.")
async def mlb_get_all_star_write_ins(params: AllStarWriteInsInput) -> Dict[str, Any]:
    query_params = {"season": params.season}
    res = await http_client.get(f"{MLB_BASE}/league/{params.leagueId}/allStarWriteIns", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get All-Star final vote information for a specific league and season.")
async def mlb_get_all_star_final_vote(params: AllStarFinalVoteInput) -> Dict[str, Any]:
    query_params = {"season": params.season}
    res = await http_client.get(f"{MLB_BASE}/league/{params.leagueId}/allStarFinalVote", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get free agent information for a specific league.")
async def mlb_get_people_free_agents(params: PeopleFreeAgentsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    res = await http_client.get(f"{MLB_BASE}/people/freeAgents", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get umpire job information for a specific date.")
async def mlb_get_jobs_umpires(params: JobsUmpiresInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/jobs/umpires", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all datacaster assignments. Filter by date or sportId.")
async def mlb_get_jobs_datacasters(params: JobsDatacastersInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/jobs/datacasters", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get official scorer assignments for a specific timecode.")
async def mlb_get_jobs_official_scorers(params: JobsOfficialScorersInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/jobs/officialScorers", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all tied games for a specific season.")
async def mlb_get_schedule_tied_games(params: ScheduleTiedGamesInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/schedule/games/tied", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get postseason schedule for a specific season.")
async def mlb_get_schedule_postseason(params: SchedulePostseasonInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/schedule/postseason", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get postseason series information for a specific season.")
async def mlb_get_schedule_postseason_series(params: SchedulePostseasonInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/schedule/postseason/series", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get all MLB seasons, optionally filtered by league ID and division ID.")
async def mlb_get_seasons(params: SeasonsInput) -> Dict[str, Any]:
    base_path = "/seasons/all" if params.all else "/seasons"
    query_params = params.model_dump(exclude_none=True, exclude={'all'})
    res = await http_client.get(f"{MLB_BASE}{base_path}", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get information for a specific MLB season by season ID.")
async def mlb_get_season_by_id(params: SeasonByIdInput) -> Dict[str, Any]:
    query_params = {"sportId": 1}
    res = await http_client.get(f"{MLB_BASE}/seasons/{params.seasonId}", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get advanced stats for players or teams, with various filters.")
async def mlb_get_stats(params: MLBStatsInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/stats", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get historical data for one or more MLB teams.")
async def mlb_get_team_history(params: TeamHistoryInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/teams/history", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get team stats for a specific season and stat group.")
async def mlb_get_team_stats(params: TeamStatsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportIds"] = 1
    res = await http_client.get(f"{MLB_BASE}/teams/stats", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get team affiliates for a specific season.")
async def mlb_get_team_affiliates(params: TeamAffiliatesInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportId"] = 1
    res = await http_client.get(f"{MLB_BASE}/teams/affiliates", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get alumni stats for a specific team and season.")
async def mlb_get_team_alumni(params: TeamAlumniInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'teamId'})
    res = await http_client.get(f"{MLB_BASE}/teams/{params.teamId}/alumni", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get coaching staff for a specific team.")
async def mlb_get_team_coaches(params: TeamCoachesInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'teamId'})
    res = await http_client.get(f"{MLB_BASE}/teams/{params.teamId}/coaches", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get personnel for a specific team.")
async def mlb_get_team_personnel(params: TeamCoachesInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'teamId'})
    res = await http_client.get(f"{MLB_BASE}/teams/{params.teamId}/personnel", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get team leaders for a specific team and season.")
async def mlb_get_team_leaders(params: TeamLeadersInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'teamId'})
    res = await http_client.get(f"{MLB_BASE}/teams/{params.teamId}/leaders", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get team stats for a specific team by team ID.")
async def mlb_get_team_stats_by_id(params: TeamStatsByIdInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True, exclude={'teamId'})
    query_params["sportIds"] = 1
    res = await http_client.get(f"{MLB_BASE}/teams/{params.teamId}/stats", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get uniforms for one or more MLB teams.")
async def mlb_get_team_uniforms(params: TeamUniformsInput) -> Dict[str, Any]:
    res = await http_client.get(f"{MLB_BASE}/uniforms/team", params=params.model_dump(exclude_none=True), headers=HEADERS)
    res.raise_for_status()
    return res.json()

@mcp.tool(description="Get transactions for a specific team or player.")
async def mlb_get_transactions(params: TransactionsInput) -> Dict[str, Any]:
    query_params = params.model_dump(exclude_none=True)
    query_params["sportId"] = 1
    res = await http_client.get(f"{MLB_BASE}/transactions", params=query_params, headers=HEADERS)
    res.raise_for_status()
    return res.json()


# ------------------------------- Entry Point -------------------------------

if __name__ == "__main__":
    logger.info("🚀 Starting MLB FastMCP Server...")
    mcp.run()