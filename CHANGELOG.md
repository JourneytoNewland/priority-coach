# Changelog

All notable changes to the Priority Coach Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-03-03

### Added
- **Quick Start Guide** - 30-second onboarding for new users
- **TodoWrite Integration** - Automatic task list creation and sync across devices
- **Proactive Escape Pattern Detection** - Real-time warning when tasks trigger known avoidance patterns
- **Complete Usage Examples** - 8 real-world conversation scenarios (examples.md)
- **Daily Review Generation** - Automated daily analysis with optimization suggestions
- **Weekly Performance Reports** - Weekly achievement review and next week suggestions
- **Time Estimation Auto-Calibration** - Learns user's time estimation patterns over time

### Changed
- Improved SKILL.md with quick start section at the top
- Enhanced workflow with 4-step process (capture → align → plan → sync)
- Updated documentation to v1.2

### Fixed
- Optimized goal keywords (removed "big data" from keywords)
- Improved task categorization logic

## [1.1.0] - 2025-03-03

### Added
- Daily review generator (daily_review.py)
- Weekly report generator (generate_weekly_report.py)
- Time accuracy tracking system
- Goal progress calculation
- Escape pattern clustering analysis

### Changed
- Updated SKILL.md with new commands (今日总结, 本周总结)
- Enhanced value scoring algorithm

## [1.0.0] - 2025-03-03

### Added
- Initial release of Priority Coach Skill
- Three-step priority method (capture → align → plan)
- Goal management system
- Time protection mechanism (bio-rhythm matching + 20% buffer)
- P-persona specific features (rejection list, feedback loop)
- Eisenhower matrix integration
- Pomodoro technique support
- Value scoring algorithm (1-5 points)
- Reference documentation (4 guides)
- Core scripts (calculate_value_score.py, analyze_escape_patterns.py)

### Features
- Brain dump protocol for scattered thoughts
- Goal alignment based on long-term objectives
- Biological rhythm time matching
- 20% white space principle
- Rejection list for fake-busy tasks
- Feedback loop for continuous improvement
- Escape pattern learning (starts after 2-3 weeks)

---

## Version Naming Convention

- **Major version (X.0.0)**: Breaking changes, major features
- **Minor version (0.X.0)**: New features, improvements
- **Patch version (0.0.X)**: Bug fixes, small improvements

---

## Future Roadmap

### [1.3.0] - Planned
- [ ] Calendar system integration
- [ ] Pomodoro Timer integration
- [ ] Visual analytics dashboard
- [ ] Team collaboration task identification
- [ ] Mobile adaptation

### [2.0.0] - Future
- [ ] Multi-user support (team version)
- [ ] Web-based dashboard
- [ ] Advanced analytics and insights
- [ ] Integration with more productivity tools

---

## Contributors

- Created by Claude Code AI Assistant
- Designed for Perceving (P) personality types
- Focused on productivity and goal achievement

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
