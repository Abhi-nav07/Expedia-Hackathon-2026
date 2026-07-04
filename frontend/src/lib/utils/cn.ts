import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges conditional class names and resolves Tailwind class conflicts
 * (e.g. cn("p-2", condition && "p-4") correctly keeps only "p-4").
 * Nearly every component in the library composes classes through this.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
