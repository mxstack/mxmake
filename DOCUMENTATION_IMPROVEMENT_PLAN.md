# Documentation Improvement Plan

## Goals

1. **Fix outdated and incorrect content** - Remove obsolete information
2. **Fill documentation gaps** - Complete TODOs and missing sections
3. **Improve discoverability** - Better structure and cross-references
4. **Keep it concise** - No bloat, focus on value

## Current State Analysis

### Existing Documentation (~756 lines total)

- `index.md` - Table of contents (33 lines)
- `getting-started.md` - Installation and basic usage (79 lines) ✓ Recently updated for UV
- `topics.md` - Auto-generated topics/domains list (11 lines)
- `preseeds.md` - Configuration preseeds and examples (145 lines) ✓ Recently updated for UV
- `templates.md` - File generation (51 lines) - **Has TODOs**
- `extending.md` - Writing custom domains (189 lines) - Good
- `dependencies.md` - Auto-generated dependency graph (9 lines)
- `make.md` - Make primer (120 lines) - Good
- `contributing.md` - Source and contributors (17 lines) - **Minimal**
- `usage-old.rst` - Outdated RST format (112 lines) - **Should be removed**

### Gaps Identified

1. No migration guide for breaking changes
2. No troubleshooting/FAQ section
3. Templates documentation incomplete (TODOs present)
4. Contributing guide is minimal (no dev setup, no PR guidelines)
5. Old RST file still present

## Tasks

### Priority 1: Critical Fixes

#### Task 1.1: Remove obsolete usage-old.rst
- **File**: `docs/source/usage-old.rst`
- **Action**: Delete (marked as "mostly outdated")
- **Justification**: Confusing to have outdated docs, content is covered elsewhere
- **Lines saved**: -112

#### Task 1.2: Update index.md TOC
- **File**: `docs/source/index.md`
- **Action**: Remove `usage-old.rst` from TOC if present
- **Justification**: Cleanup after removal

### Priority 2: High-Value Additions

#### Task 2.1: Create migration guide
- **New file**: `docs/source/migration.md`
- **Content**:
  - Version-based breaking changes (start from 1.0+)
  - MXENV_UV_GLOBAL → auto-detection (v1.3.1)
  - Clear "before/after" examples
  - Keep concise: ~50-80 lines
- **Target**: 60 lines
- **Add to index.md TOC** after preseeds

#### Task 2.2: Add FAQ/Troubleshooting
- **File**: `docs/source/getting-started.md` (append as new section)
- **Content**:
  - 5-7 common issues with solutions
  - "UV not found" → install instructions
  - "Python version mismatch" → UV_PYTHON setting
  - "Tests not running" → check run-tests.sh generation
  - Keep each Q&A to 2-3 lines
- **Target**: +30-40 lines to getting-started.md

### Priority 3: Fill Documentation Gaps

#### Task 3.1: Complete templates.md TODOs
- **File**: `docs/source/templates.md`
- **Current state**: Has 2 TODO sections for custom templates
- **Action**:
  - Section: "Templates defined via mx.ini with Jinja2"
    - Show mx.ini configuration format
    - 1-2 concrete examples
    - ~20 lines
  - Section: "Templates based on Python code"
    - Reference extending.md for domain writing
    - Show template registration with @template decorator
    - 1 minimal example
    - ~15 lines
- **Target**: +35 lines

#### Task 3.2: Enhance contributing.md
- **File**: `docs/source/contributing.md`
- **Current state**: Only lists copyright and contributors (17 lines)
- **Action**:
  - Add "Development Setup" section
    - Clone, `make install`, `make test` workflow
    - ~10 lines
  - Add "Pull Request Guidelines" section
    - Keep commits concise (max 3 lines)
    - Never mention AI/Claude in commits
    - Run tests before PR
    - ~15 lines
  - Add "Running Documentation" section
    - `make docs`, `make docs-linkcheck`
    - ~8 lines
- **Target**: +33 lines (total ~50 lines)

### Priority 4: Optional Enhancements

#### Task 4.1: Add workflow diagram
- **File**: `docs/source/getting-started.md` or new `docs/source/workflow.md`
- **Content**: Mermaid diagram showing mxmake init → edit settings → make install flow
- **Status**: Optional, if requested
- **Target**: +15-20 lines

#### Task 4.2: Expand examples in preseeds.md
- **File**: `docs/source/preseeds.md`
- **Content**: Add 1-2 more real-world examples (Django, Flask, etc.)
- **Status**: Optional, if requested
- **Target**: +30-40 lines per example

## Timeline and Dependencies

### Phase 1: After UV refactoring PR merges
- Task 1.1: Remove usage-old.rst
- Task 1.2: Update index TOC
- Task 2.1: Create migration guide (document UV changes)

### Phase 2: Core improvements
- Task 2.2: Add FAQ section
- Task 3.1: Complete templates.md
- Task 3.2: Enhance contributing.md

### Phase 3: Optional (if time permits)
- Task 4.1: Workflow diagram
- Task 4.2: More examples

## Expected Outcome

### Line Count Projection
- **Current total**: ~756 lines
- **Removed**: -112 (usage-old.rst)
- **Added**: ~158 lines (migration guide + FAQ + templates + contributing)
- **New total**: ~802 lines
- **Net change**: +46 lines (~6% increase)

### Success Criteria
1. ✓ No outdated files (usage-old.rst removed)
2. ✓ No TODOs in documentation
3. ✓ Migration guide helps users upgrade
4. ✓ Contributing guide helps new contributors
5. ✓ FAQ answers common questions
6. ✓ Total documentation stays under 900 lines

## Additional Improvements to Consider

### Documentation Structure Enhancements

#### Add Glossary
- **New file**: `docs/source/glossary.md`
- **Content**: Define key terms (domain, topic, sentinel, preseed, mxdev, FQN, etc.)
- **Value**: Helps newcomers understand terminology
- **Effort**: Low (~40 lines)
- **Priority**: Medium

#### Add "Why mxmake" / Comparison Section
- **Location**: New section in `index.md` or `getting-started.md`
- **Content**:
  - Benefits over plain pip/poetry/tox
  - When to use mxmake vs alternatives
  - Key differentiators (extensibility, mxdev integration, make-based)
- **Value**: Helps users decide if mxmake is right for them
- **Effort**: Medium (~30-50 lines)
- **Priority**: Medium

#### Add Conceptual Overview
- **New file**: `docs/source/concepts.md` or section in index
- **Content**:
  - How mxmake works (init → settings → make)
  - Topic → Domain → Target → Sentinel flow
  - Dependency resolution
  - Template system overview
- **Value**: Better understanding for advanced usage
- **Effort**: Medium (~60-80 lines)
- **Priority**: Medium-High

#### Quick Reference / Cheat Sheet
- **New file**: `docs/source/quickref.md`
- **Content**:
  - Common commands table
  - Important settings by use case
  - Common domain combinations
- **Value**: Quick lookup for experienced users
- **Effort**: Low (~40-50 lines)
- **Priority**: Low-Medium

### Content Enhancements

#### More Use Case Examples
- **Location**: Expand `preseeds.md` or new `docs/source/examples.md`
- **Content**:
  - Django project setup
  - FastAPI/modern web framework
  - Data science/Jupyter notebook project
  - Library/package development
- **Value**: Shows versatility, helps users get started faster
- **Effort**: Medium (~40 lines per example)
- **Priority**: Low-Medium (can be added incrementally)

#### CI/CD Integration Guide
- **New file**: `docs/source/cicd.md`
- **Content**:
  - Using mxmake in GitHub Actions
  - GitLab CI integration
  - Using pre-generated gh-actions templates
  - Docker multi-stage builds with mxmake
- **Value**: Production deployment guidance
- **Effort**: Medium (~80-100 lines)
- **Priority**: Medium

#### Best Practices Guide
- **New file**: `docs/source/best-practices.md`
- **Content**:
  - Recommended settings for different project types
  - Common patterns (versioning, dependency pinning)
  - Anti-patterns to avoid
  - Performance tips for large projects
- **Value**: Helps users avoid common mistakes
- **Effort**: Medium (~60-80 lines)
- **Priority**: Medium

#### Advanced Troubleshooting
- **New file**: `docs/source/troubleshooting.md` or expand FAQ
- **Content**:
  - Detailed debugging steps
  - Common error messages explained
  - Platform-specific issues (Windows, macOS, Linux)
  - Version compatibility problems
- **Value**: Reduces support burden
- **Effort**: Medium (~80-100 lines, grows over time)
- **Priority**: Medium

### Documentation Quality Improvements

#### Add Cross-References
- **Action**: Review all docs and add MyST cross-references
- **Content**:
  - Link between related sections
  - Link from examples to domain documentation
  - Link settings mentions to topics.md
- **Value**: Better navigation
- **Effort**: Low (during other edits)
- **Priority**: Ongoing

#### Add Visual Diagrams
- **Location**: Various files
- **Content**:
  - Workflow diagram (mxmake init → make install flow)
  - Architecture diagram (topics/domains/targets relationship)
  - Dependency graph enhancement
- **Tool**: Mermaid diagrams (MyST supports them)
- **Value**: Visual learners, complex concepts clearer
- **Effort**: Medium (~5-10 lines per diagram)
- **Priority**: Low-Medium

#### Integrate CHANGES.md
- **Location**: `index.md` or new `docs/source/changelog.md`
- **Content**: Link to or include recent changes from CHANGES.md
- **Value**: Users see what's new
- **Effort**: Low (if just linking), Medium (if integrating)
- **Priority**: Low

## Open Questions

1. **Migration guide scope**: Include all versions or just recent (1.0+)?
   - Recommendation: Start from 1.0, or last 2-3 major versions

2. **FAQ location**: Separate file or in getting-started.md?
   - Recommendation: Append to getting-started.md (easier to discover)

3. **Templates examples**: Generic or specific real-world use cases?
   - Recommendation: Start generic, can add specific later

4. **Workflow diagram**: Worth the maintenance overhead?
   - Recommendation: YES - Mermaid diagrams are easy to maintain

5. **How comprehensive should use case examples be?**
   - Recommendation: Start with 2-3 good examples, add more based on user feedback

6. **Should we create a separate "Advanced Topics" section?**
   - Could include: CI/CD, Docker, best practices, troubleshooting
   - Recommendation: Create if we add 3+ advanced guides

7. **Glossary as separate file or inline in concepts doc?**
   - Recommendation: Separate file for easy reference

## Recommended Implementation Phases

### Phase 1: Essential Fixes (Must Do)
**Target: After UV refactoring PR merges**
- Remove usage-old.rst
- Create migration guide
- Add FAQ section
- Complete templates.md TODOs
- Enhance contributing.md

**Effort**: ~4-6 hours
**Line count**: +158 lines total

### Phase 2: Structure & Navigation (Should Do)
**Target: Within 1-2 weeks**
- Add glossary
- Add conceptual overview
- Add workflow diagram (Mermaid)
- Improve cross-references

**Effort**: ~3-4 hours
**Line count**: +100-140 lines

### Phase 3: Advanced Content (Nice to Have)
**Target: As needed / based on user feedback**
- CI/CD integration guide
- Best practices guide
- Advanced troubleshooting
- Quick reference sheet
- "Why mxmake" section

**Effort**: ~6-8 hours
**Line count**: +250-350 lines

### Phase 4: Examples Expansion (Optional)
**Target**: Community contributions / as requested
- More use case examples (Django, FastAPI, etc.)
- Platform-specific guides
- Integration examples

**Effort**: ~2 hours per example
**Line count**: +40 lines per example

## Summary: Projected Documentation Growth

| Phase | Files Changed/Added | Lines Added | Total Lines |
|-------|---------------------|-------------|-------------|
| Current | 9 files | 756 | 756 |
| Phase 1 | +1 file, edit 4 | +158 | ~902 |
| Phase 2 | +2 files, edit several | +120 | ~1,022 |
| Phase 3 | +4 files | +300 | ~1,322 |
| Phase 4 | Varies | +40 each | Variable |

**Recommendation**: Execute Phase 1 immediately, Phase 2 soon after, Phase 3-4 based on user feedback and priorities.

## Notes

- This plan assumes the UV refactoring PR (#56) is merged first
- Documentation changes already made on refactoring branch:
  - getting-started.md: Added UV auto-detection section
  - preseeds.md: Updated examples, added UV_PYTHON warnings
  - These changes will be in main after merge
- All new work will be done on this `docs/improvement-plan` branch
- Each task can be done incrementally with focused commits
- Keep total documentation under 1,500 lines for maintainability
- Quality over quantity - concise, accurate, helpful
