# About
This file contains notes from what could be further improved while modernising the stack. They are not investigated in default, just things I noticed while making changes and didn't want to do right away to stay focused

# Collection of Notes

- deprecation warnings during tests
- is bumpversion still the way to go?
- bumpversion config in setup.cfg and elsewhere
- venv handling - can uv do this natively?
- ./go trailscraper maybe could be built with uv itself, no need for the venv stuff? 
- use uv base images? 
- use uvs own build system instead of hatchling?
- restructure build and publish
  - on publish:
    - uv publish