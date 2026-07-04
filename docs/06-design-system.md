# Design System — Theme, Typography, Spacing, Motion

This documents the tokens established in this module. Every future
component (Component Library, Dashboard Shell, Travel Foundation UI,
etc.) should consume these rather than inventing new colors, spacing, or
animation timings ad hoc.

## Color tokens

Defined as HSL CSS custom properties in `app/globals.css`, mapped into
Tailwind utility classes via `tailwind.config.ts`. Always use the
Tailwind class (`bg-primary`, `text-muted-foreground`, etc.) — never
hardcode a hex/HSL value in a component.

| Token | Usage |
|---|---|
| `background` / `foreground` | Page-level base colors |
| `card` / `card-foreground` | Elevated surfaces (cards, panels, modals) |
| `primary` / `primary-foreground` | Main brand actions (buttons, links, active states) |
| `secondary` / `secondary-foreground` | Lower-emphasis actions |
| `accent` / `accent-foreground` | Highlights, hover states, badges |
| `muted` / `muted-foreground` | De-emphasized text, disabled states |
| `destructive` / `destructive-foreground` | Errors, delete actions, validation failures |
| `success` / `success-foreground` | Confirmations, completed states |
| `warning` / `warning-foreground` | Caution states, non-blocking alerts |
| `border` / `input` / `ring` | Borders, form inputs, focus rings |

Both `:root` (light) and `.dark` blocks are defined — `next-themes`
toggles the `dark` class on `<html>`, and every token flips accordingly.
No component should ever check `theme === "dark"` and branch its own
colors; if a new visual state is needed, add a token instead.

## Typography

Font: Inter, loaded via `next/font/google` in `app/layout.tsx` and
exposed as the `--font-inter` CSS variable, wired into Tailwind's
`font-sans` in `tailwind.config.ts`. Use Tailwind's default type scale
(`text-sm`, `text-base`, `text-lg`, `text-2xl`, etc.) — it's already
sensible; we haven't overridden it, only the font family.

Suggested scale for consistency across pages:
- Page titles: `text-2xl font-semibold` (or `text-3xl` for landing/marketing)
- Section headings: `text-xl font-semibold`
- Card titles: `text-base font-medium`
- Body: `text-sm` or `text-base`
- Captions/meta: `text-xs text-muted-foreground`

## Spacing

Tailwind's default spacing scale (4px base unit) is used as-is —
deliberately not overridden, so `p-4`, `gap-2`, `space-y-6` etc. behave
exactly as documented in Tailwind's own docs. Consistency comes from
convention, not a custom scale:
- Card padding: `p-4` or `p-6`
- Section vertical rhythm: `space-y-6` or `space-y-8`
- Form field gaps: `gap-4`

## Motion

`lib/motion/variants.ts` is the single source of truth for animation
feel. Three duration tokens (`fast` 150ms, `base` 250ms, `slow` 400ms)
and matching easing curves are defined once and mirrored into
`tailwind.config.ts`'s `transitionDuration` — so a CSS-only
`transition-colors duration-fast` and a Framer Motion `fadeIn` variant
feel like the same design system, not two unrelated ones.

Reusable variants: `fadeIn`, `slideUp`, `scaleIn`, `staggerContainer()`.
Import these rather than writing new `transition={{ duration: ... }}`
objects per component.

## Dark mode mechanics

- `ThemeProvider` (`components/theme/theme-provider.tsx`) wraps the app
  in `app/providers.tsx`, using `next-themes` with `attribute="class"`
  and `defaultTheme="system"`.
- `ThemeToggle` (`components/theme/theme-toggle.tsx`) cycles
  light → dark → system, with `aria-label`/`title` reflecting the
  current state for accessibility.
- The theme preference is persisted to `localStorage` by `next-themes`.
  This is intentionally different from the auth token's storage
  strategy (see `store/auth-store.ts`, Module 05) — a UI preference
  carries no security risk in localStorage, whereas an access token
  does. Don't conflate the two "storage" decisions when extending this
  system.
- `suppressHydrationWarning` is already set on `<html>` in
  `app/layout.tsx` (added in Module 05, used here) since the server
  can't know the client's persisted theme before hydration — this is
  the standard, documented `next-themes` + Next.js App Router pattern,
  not a lint-suppression shortcut.

## What's intentionally NOT in this module

- Actual dashboard/page layouts — that's Dashboard Shell / Frontend Pages.
- Buttons, inputs, cards, etc. as components — that's Component Library.
  This module only provides the *tokens* those components will consume.
