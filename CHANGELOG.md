# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Pagination support** for large dataset tools to prevent token limit issues
  - `get_player_games_by_month` now supports `page_size` and `cursor` parameters
  - `get_titled_players` now supports `page_size` and `cursor` parameters
  - `get_club_members` now supports `page_size` and `cursor` parameters
- Base64-encoded opaque cursors following MCP specification
- Configurable page sizes with sensible defaults and maximums
- Structured pagination metadata in responses (next_cursor, has_more, total_count, etc.)
- Comprehensive documentation for pagination usage

### Changed
- Tool responses now include pagination metadata for paginated tools
- Backward compatibility maintained (no pagination params = first page)

### Fixed
- **Token limit issues** when tools return large datasets (e.g., 100+ games per month)
- Models exceeding 128k token context limits with large Chess.com API responses

## [0.1.0] - 2025-03-27

### Added
- Initial release
- Chess.com API MCP server with player profile, stats, and games tools
- Resource endpoints for accessing Chess.com data
- Docker support
