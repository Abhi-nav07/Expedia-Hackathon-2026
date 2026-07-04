import type { Transition, Variants } from "framer-motion";

/**
 * Shared animation tokens. Every animated component in the future
 * Component Library module should import from here rather than
 * hand-rolling durations/easings, so motion feels consistent across
 * cards, modals, toasts, and page transitions.
 */
export const DURATION = {
  fast: 0.15,
  base: 0.25,
  slow: 0.4,
} as const;

export const EASE = {
  standard: [0.4, 0, 0.2, 1],
  decelerate: [0, 0, 0.2, 1],
  accelerate: [0.4, 0, 1, 1],
} as const;

export const springTransition: Transition = {
  type: "spring",
  stiffness: 300,
  damping: 30,
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: DURATION.base, ease: EASE.standard } },
  exit: { opacity: 0, transition: { duration: DURATION.fast, ease: EASE.accelerate } },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.base, ease: EASE.decelerate },
  },
  exit: {
    opacity: 0,
    y: 8,
    transition: { duration: DURATION.fast, ease: EASE.accelerate },
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: DURATION.fast, ease: EASE.decelerate },
  },
  exit: {
    opacity: 0,
    scale: 0.96,
    transition: { duration: DURATION.fast, ease: EASE.accelerate },
  },
};

/**
 * Stagger container: wrap a list of children with this as the parent's
 * `variants`, and give each child `slideUp` (or similar) — children
 * animate in sequence rather than all at once. Useful for card grids,
 * search results, dashboard widgets, etc.
 */
export const staggerContainer = (staggerDelay = 0.06): Variants => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren: staggerDelay,
    },
  },
});
