import Image from "next/image";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { RatingStars } from "@/components/travel/rating-stars";
import { WishlistButton } from "@/components/travel/wishlist-button";
import { cn } from "@/lib/utils/cn";

export interface DestinationCardProps {
  id: string;
  name: string;
  location: string;
  imageUrl: string;
  rating?: number;
  priceFrom?: number;
  currency?: string;
  badge?: string;
  onClick?: () => void;
  className?: string;
}

/**
 * Generic destination browsing card — deliberately has no booking or
 * search-result-ranking logic. `onClick`/`priceFrom` are plain props;
 * how a "destination" is actually fetched or what "priceFrom" means
 * for the eventual challenge is left entirely to the caller.
 *
 * Note: next/image requires the image host to be listed in
 * next.config.mjs's images.remotePatterns (Module 01 pre-configures
 * images.unsplash.com and *.googleusercontent.com) — add any other
 * image CDN the challenge ends up using there.
 */
export function DestinationCard({
  id,
  name,
  location,
  imageUrl,
  rating,
  priceFrom,
  currency = "USD",
  badge,
  onClick,
  className,
}: DestinationCardProps) {
  return (
    <Card
      className={cn(
        "group cursor-pointer overflow-hidden transition-shadow duration-base hover:shadow-md",
        className
      )}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="(max-width: 768px) 100vw, 33vw"
          className="object-cover transition-transform duration-slow group-hover:scale-105"
        />
        {badge && (
          <Badge className="absolute left-3 top-3" variant="default">
            {badge}
          </Badge>
        )}
        <WishlistButton itemType="destination" itemId={id} className="absolute right-3 top-3" />
      </div>
      <CardContent className="space-y-1 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="line-clamp-1 font-semibold">{name}</h3>
          {rating !== undefined && <RatingStars value={rating} size="sm" showValue />}
        </div>
        <p className="line-clamp-1 text-sm text-muted-foreground">{location}</p>
        {priceFrom !== undefined && (
          <p className="pt-1 text-sm">
            <span className="text-muted-foreground">From </span>
            <span className="font-semibold">
              {new Intl.NumberFormat("en-US", { style: "currency", currency }).format(priceFrom)}
            </span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}
