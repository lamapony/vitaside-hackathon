# VitaSide Dashboard Design Guide

## Visual Theme
Calm clinical workspace, not a dense developer console. The interface should feel local, private, readable, and suitable for repeated review before a doctor visit.

## Layout Principles
- Prefer generous whitespace over dense dashboards.
- Keep primary content in a centered column with readable line lengths.
- Use cards for bounded tools and repeated clinical items only.
- Keep section rhythm consistent: header, air, content group, air.
- Avoid nested cards and decorative gradients.

## Color Roles
- Background: soft off-white clinical surface.
- Surface: white cards with subtle borders.
- Accent: restrained teal for actions, progress, and active states.
- Warning/error colors are reserved for actual status, not decoration.

## Typography Rules
- Use system sans-serif for UI and Georgia only for cited evidence excerpts.
- No negative letter spacing.
- Headings should be clear but not oversized inside cards.
- Body copy should preserve line height for long medical text.

## Components
- Buttons have stable minimum height and use icon + label when they trigger a clear action.
- Navigation items need enough height for label + hint.
- Cards use 16px radius, 28px padding, and a low clinical shadow.
- Evidence quotes use a left rule, serif italic, and extra vertical spacing.

## Responsive Behavior
- Sidebar becomes a top navigation surface below tablet width.
- Main content keeps 20px+ side padding on mobile.
- Grids collapse to one column before text gets cramped.
