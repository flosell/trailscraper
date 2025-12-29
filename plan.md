# Trailscraper Modernization Plan: Migration to `uv` and `pyproject.toml`

## Overview
This plan outlines the migration from the legacy `setup.py` + `requirements.txt` + custom bash scripting approach to a modern `uv`-based workflow with `pyproject.toml`.

## Goals
- ✅ Migrate to `pyproject.toml` for all project configuration
- ✅ Use `uv` for dependency management with lockfile support
- ✅ Use `uv`'s built-in venv management
- ✅ Use `uv build` for package building
- ✅ Update Dockerfile to use `uv`
- ✅ Maintain backward compatibility of `./go` script interface
- ✅ Migrate version management to `uv`-compatible approach
- ✅ Keep Docker-based multi-version testing approach

## Current State Analysis

### Existing Files to Migrate/Replace
- `setup.py` - Package definition (to be replaced by `pyproject.toml`)
- `requirements.txt` - Runtime dependencies (to be migrated to `pyproject.toml`)
- `requirements-dev.txt` - Dev dependencies (to be migrated to `pyproject.toml`)
- `setup.cfg` - Contains bumpversion config (to be migrated)
- `./go` - Custom build script (internals to be updated)
- `Dockerfile` - Uses pip/setup.py (to be updated to use `uv`)

### Existing Workflows to Preserve
- `./go setup` - Sets up development environment
- `./go test` - Runs tests
- `./go check` - Runs linting
- `./go test-setuptools` - Tests installation in clean environment
- `./go test-docker-build` - Tests Docker build
- `./go release` - Full release process
- `./go bump_version` - Version bumping
- `./go in-version` / `./go in-all-versions` - Multi-version testing
- All other utility goals

### GitHub Actions Dependencies
- `.github/workflows/check.yml` - Calls `./go setup`, `./go check`, `./go test`
- `.github/workflows/check.yml` - Calls `./go test-setuptools`, `./go test-docker-build`

## Migration Steps

### Phase 1: Create `pyproject.toml`

#### 1.1 Project Metadata
- Migrate all metadata from `setup.py`:
  - Name, version, description, author, license, URL
  - Python version requirements (`>=3.9`)
  - Classifiers
  - Keywords

#### 1.2 Dependencies
- Migrate `requirements.txt` → `[project] dependencies`
- Migrate `requirements-dev.txt` → `[dependency-groups] dev`
- Ensure all version pins are preserved

#### 1.3 Build System
- Configure `[build-system]` to use `hatchling`
- Set `requires = ["hatchling"]`

#### 1.4 Package Configuration
- Configure `[tool.hatchling.build]` or `[tool.setuptools]`:
  - Package discovery (`find: {packages = ["trailscraper"]}`)
  - Package data (`known-iam-actions.txt`)
  - Entry points (`trailscraper=trailscraper.cli:root_group`)

#### 1.5 Version Management
- Store version in `pyproject.toml` under `[project] version`
- Update `bumpversion` config in `pyproject.toml` to update:
  - `pyproject.toml` version field
  - `trailscraper/__init__.py` `__version__`
  - Keep `CHANGELOG.md` update (if applicable)

#### 1.6 Development Tools Configuration
- Move `pytest.ini` settings to `[tool.pytest.ini_options]` in `pyproject.toml` (optional, can keep separate file)
- Configure any other tool settings (pylint, etc.) in `pyproject.toml` if desired

### Phase 2: Update `./go` Script

#### 2.1 Environment Setup
- **`goal_setup()`**: 
  - Replace `python3 -m venv` with `uv venv`
  - Replace `pip3 install -r requirements-dev.txt` with `uv pip install -e ".[dev]"`
  - Remove `python3 setup.py develop` (handled by `-e` flag)
  - Update `VENV_DIR` to use `uv`'s default venv location or keep custom location

#### 2.2 Virtual Environment Activation
- **`activate_venv()`**: 
  - Update to work with `uv`'s venv structure
  - Ensure `source "${VENV_DIR}/bin/activate"` still works (uv creates standard venvs)

#### 2.3 Build and Release
- **`goal_release()`**: 
  - Replace `python3 setup.py sdist bdist_wheel` with `uv build`
  - Update version check to include `pyproject.toml` instead of `setup.py` and `setup.cfg`
  - Keep `twine upload` for PyPI (or use `uv publish` if preferred)

#### 2.4 Testing
- **`goal_test()`**: 
  - Use `uv run pytest` or activate venv and run pytest normally
  - Keep all environment variable setup (BOTO_CONFIG, AWS_*)

#### 2.5 Cleanup
- **`goal_clean()`**: 
  - Remove `uv`-specific artifacts if any
  - Keep existing cleanup logic for build artifacts
  - Update to remove `uv.lock` if regenerating (or keep it)

#### 2.6 Version Bumping
- **`goal_bump_version()`**: 
  - Ensure `bumpversion` works with new `pyproject.toml` configuration
  - Test that version updates in both `pyproject.toml` and `__init__.py`

#### 2.7 Test Setuptools
- **`goal_test-setuptools()`**: 
  - Update Docker command to use `uv`:
    - `uv pip install .` or `uv pip install -e .`
    - Test that `trailscraper` command works

#### 2.8 Other Goals
- **`goal_trailscraper()`**: Keep as-is (just activates venv and runs)
- **`goal_check()`**: Keep as-is (just activates venv and runs pylint)
- **`goal_generate-rst()`**: Keep as-is
- **`goal_in-version()` / `goal_in-all-versions()`**: Keep Docker approach, but ensure Docker containers have `uv` installed

### Phase 3: Update Dockerfile

#### 3.1 Base Image
- Install `uv` in the builder stage
- Can use `python:3.11-alpine` or consider `ghcr.io/astral-sh/uv:python3.11-alpine` if available

#### 3.2 Build Stage
- Replace `pip install --prefix=/install -r requirements.txt` with `uv pip install --prefix=/install -r requirements.txt` or better: `uv pip install --prefix=/install .`
- Replace `python3 setup.py sdist bdist_wheel` with `uv build`
- Replace `pip install --prefix=/install dist/trailscraper*.tar.gz` with `uv pip install --prefix=/install dist/trailscraper*.whl` (or use the built wheel)

#### 3.3 Final Stage
- Copy installed package from builder
- Keep entrypoint as-is

### Phase 4: Version Management Migration

#### 4.1 Update `setup.cfg` → `pyproject.toml`
- Move bumpversion configuration to `pyproject.toml`:
  ```toml
  [tool.bumpversion]
  current_version = "0.9.2"
  commit = true
  tag = false
  
  [tool.bumpversion.file:pyproject.toml]
  search = 'version = "{current_version}"'
  replace = 'version = "{new_version}"'
  
  [tool.bumpversion.file:trailscraper/__init__.py]
  search = '__version__ = "{current_version}"'
  replace = '__version__ = "{new_version}"'
  ```

#### 4.2 Update Version Sources
- Update `goal_release()` version check to read from `pyproject.toml` instead of `setup.cfg` and `setup.py`
- Keep `CHANGELOG.md` and `trailscraper/__init__.py` in version check

### Phase 5: Lockfile Management

#### 5.1 Generate Lockfile
- Run `uv lock` to generate `uv.lock`
- Commit `uv.lock` to repository for reproducible builds

#### 5.2 Update Workflows
- Ensure `./go setup` uses `uv sync` or `uv pip install` with lockfile
- Update Docker builds to use lockfile when available

### Phase 6: Testing and Validation

#### 6.1 Local Testing
- Test `./go setup` creates venv and installs dependencies
- Test `./go test` runs successfully
- Test `./go check` runs successfully
- Test `./go test-setuptools` works in Docker
- Test `./go test-docker-build` works
- Test `./go trailscraper` executes correctly
- Test `./go bump_version` updates versions correctly

#### 6.2 GitHub Actions Validation
- Ensure `.github/workflows/check.yml` continues to work
- All matrix Python versions should pass
- `test-setuptools` and `test-docker-build` jobs should pass

#### 6.3 Release Process Testing
- Test `./go release` workflow (dry-run if possible)
- Verify version checking works
- Verify build produces correct artifacts
- Verify Docker build works

### Phase 7: Cleanup (After Successful Migration)

#### 7.1 Remove Legacy Files (Optional)
- Consider removing `setup.py` (but may want to keep for transition period)
- Consider removing `requirements.txt` and `requirements-dev.txt` (but may want to keep for reference)
- Consider removing `setup.cfg` (after bumpversion migration confirmed)

#### 7.2 Documentation Updates
- Update `README.md` if installation instructions need changes
- Update `CONTRIBUTING.md` if development setup changed
- Update any other docs referencing old setup

## Implementation Order

1. **Create `pyproject.toml`** with all metadata and dependencies
2. **Generate `uv.lock`** file
3. **Update `./go setup`** to use `uv`
4. **Test local development workflow** (`./go setup`, `./go test`, `./go check`)
5. **Update `./go release`** to use `uv build`
6. **Update Dockerfile** to use `uv`
7. **Update version management** (bumpversion config)
8. **Update `./go test-setuptools`** and `./go test-docker-build`**
9. **Test GitHub Actions** workflow
10. **Test full release process** (dry-run)
11. **Clean up legacy files** (optional, after confirmation)

## Key Considerations

### Backward Compatibility
- All `./go` commands must continue to work with the same interface
- GitHub Actions should not require changes (they call `./go` commands)
- External users installing via pip should not be affected

### Version Management
- `bumpversion` needs to be updated to work with `pyproject.toml`
- Version must be kept in sync between:
  - `pyproject.toml`
  - `trailscraper/__init__.py`
  - `CHANGELOG.md` (if applicable)

### Lockfile Strategy
- Commit `uv.lock` to repository for reproducible builds
- Regenerate lockfile when dependencies change
- Use lockfile in CI/CD and Docker builds

### Virtual Environment Location
- `uv` by default creates `.venv` in project root
- Can specify custom location: `uv venv /path/to/venv`
- Current script uses `venvs/trailscraper-venv${VENV_POSTFIX}`
- Decision: Keep custom location or migrate to `.venv`?
  - **Recommendation**: Keep custom location for now to avoid breaking existing workflows

### Docker Multi-Version Testing
- `goal_in-version` and `goal_in-all-versions` use Docker
- Need to ensure Docker images have `uv` installed
- Can install `uv` in Dockerfile or install on-the-fly in the goal

## Risks and Mitigations

### Risk 1: Bumpversion compatibility with pyproject.toml
- **Mitigation**: Test bumpversion thoroughly, may need to update bumpversion or use alternative tool

### Risk 2: GitHub Actions breakage
- **Mitigation**: Test all GitHub Actions workflows before merging
- Keep old files until migration is confirmed working

### Risk 3: Release process breakage
- **Mitigation**: Test release process in a test environment first
- Have rollback plan (keep old files in git history)

### Risk 4: Docker build issues
- **Mitigation**: Test Docker build locally and in CI
- Ensure multi-stage build works correctly with `uv`

## Success Criteria

- ✅ `./go setup` creates venv and installs all dependencies using `uv`
- ✅ `./go test` runs all tests successfully
- ✅ `./go check` runs linting successfully
- ✅ `./go test-setuptools` works in clean Docker environment
- ✅ `./go test-docker-build` builds and runs Docker image
- ✅ `./go release` builds packages using `uv build` and completes successfully
- ✅ `./go bump_version` updates version in `pyproject.toml` and `__init__.py`
- ✅ GitHub Actions pipeline passes for all Python versions
- ✅ Docker image builds and runs correctly
- ✅ All existing functionality preserved

## Notes

- `uv` is fast and provides excellent dependency resolution
- Lockfile ensures reproducible builds across environments
- `pyproject.toml` is the modern Python packaging standard
- Migration can be done incrementally, testing at each step
- Old files can be kept during transition for safety

