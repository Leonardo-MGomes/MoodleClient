---
name: Service Implementation
about: Track the progress of adding or finishing a WebService or core client module.
title: 'Implement WebService functions for [Service Name]'
labels: feature, service
assignees: ''
---

## Description

A clear and concise description of what this service does and why these specific endpoints are missing.

## Current Status

- [ ] `core_module_function`
- [ ] `core_module_function`

## To-Do List

- [ ] Define the data models for the WebService functions.
- [ ] Implement the API request wrappers in the service layer.
- [ ] Add error handling for edge cases (e.g., empty data payloads, disabled service permissions).

## Definition of Done / Testing Criteria

- [ ] Response payloads successfully map to local object instances without data loss.
- [ ] Service handles basic failure states gracefully (network error, invalid parameters).
- [ ] Verified via (select one):
    - [ ] Unit Tests
    - [ ] Integration Tests
    - [ ] Manual Testing via Client Console.

## Additional Context

Add links to Moodle source files, database definitions (`services.php`), API endpoints, or other relevant
information/sources here.