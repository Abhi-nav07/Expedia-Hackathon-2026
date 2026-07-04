"use client";

import { Heart } from "lucide-react";
import type * as React from "react";

import { cn } from "@/lib/utils/cn";
import { useWishlistStore } from "@/store/wishlist-store";

export interface WishlistButtonProps {
  itemType: string;
  itemId: string;
  /** Called after the local toggle, with the new state — the extension
   * point for persisting to a real backend once the challenge defines
   * what "wishlist" means for it (e.g. POST /wishlist/{itemType}/{itemId}). */
  onToggle?: (wishlisted: boolean) => void;
  size?: "sm" | "default";
  className?: string;
}

export function WishlistButton({
  itemType,
  itemId,
  onToggle,
  size = "default",
  className,
}: WishlistButtonProps) {
  const isWishlisted = useWishlistStore((state) => state.isWishlisted(itemType, itemId));
  const toggle = useWishlistStore((state) => state.toggle);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggle(itemType, itemId);
    onToggle?.(!isWishlisted);
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-pressed={isWishlisted}
      aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
      className={cn(
        "inline-flex items-center justify-center rounded-full bg-background/80 backdrop-blur-sm transition-colors duration-fast",
        "hover:bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        size === "sm" ? "h-7 w-7" : "h-9 w-9",
        className
      )}
    >
      <Heart
        className={cn(
          size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4",
          "transition-colors duration-fast",
          isWishlisted ? "fill-destructive text-destructive" : "text-foreground/70"
        )}
      />
    </button>
  );
}
