import { create } from "zustand";

/**
 * Generic wishlist state — deliberately NOT wired to any backend
 * endpoint. This is local/optimistic-only, matching the brief's
 * instruction to build reusable infrastructure without committing to
 * business logic that depends on the (currently unknown) challenge.
 *
 * When the real challenge is known, wiring persistence is a small,
 * contained change: call your wishlist API inside `toggle` (optimistic
 * update already happens locally; add a .catch that reverts on failure)
 * — nothing that *consumes* `useWishlistStore` or `<WishlistButton>`
 * needs to change.
 */
interface WishlistState {
  /** Set of "itemType:itemId" composite keys, e.g. "hotel:abc123". */
  items: Set<string>;
  isWishlisted: (itemType: string, itemId: string) => boolean;
  toggle: (itemType: string, itemId: string) => void;
}

function makeKey(itemType: string, itemId: string): string {
  return `${itemType}:${itemId}`;
}

export const useWishlistStore = create<WishlistState>((set, get) => ({
  items: new Set(),
  isWishlisted: (itemType, itemId) => get().items.has(makeKey(itemType, itemId)),
  toggle: (itemType, itemId) => {
    const key = makeKey(itemType, itemId);
    set((state) => {
      const next = new Set(state.items);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return { items: next };
    });
  },
}));
