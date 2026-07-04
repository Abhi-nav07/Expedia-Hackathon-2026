import Image from "next/image";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { RatingStars } from "@/components/travel/rating-stars";
import { WishlistButton } from "@/components/travel/wishlist-button";
import { cn } from "@/lib/utils/cn";

export interface HotelCardProps {
  id: string;
  name: string;
  location: string;
  imageUrl: string;
  starRating: number;
  reviewScore?: number;
  reviewCount?: number;
  amenities?: string[];
  pricePerNight: number;
  currency?: string;
  onSelect?: (id: string) => void;
  className?: string;
}

/** UI-only hotel card — no inventory, availability, or pricing logic. */
export function HotelCard({
  id,
  name,
  location,
  imageUrl,
  starRating,
  reviewScore,
  reviewCount,
  amenities = [],
  pricePerNight,
  currency = "USD",
  onSelect,
  className,
}: HotelCardProps) {
  const visibleAmenities = amenities.slice(0, 3);
  const extraCount = amenities.length - visibleAmenities.length;

  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="flex flex-col sm:flex-row">
        <div className="relative aspect-[4/3] w-full shrink-0 overflow-hidden bg-muted sm:w-48">
          <Image src={imageUrl} alt={name} fill sizes="192px" className="object-cover" />
          <WishlistButton itemType="hotel" itemId={id} size="sm" className="absolute right-2 top-2" />
        </div>

        <div className="flex flex-1 flex-col">
          <CardContent className="flex-1 space-y-2 p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold leading-tight">{name}</h3>
                <p className="text-sm text-muted-foreground">{location}</p>
              </div>
              <RatingStars value={starRating} size="sm" />
            </div>

            {reviewScore !== undefined && (
              <div className="flex items-center gap-2 text-sm">
                <Badge variant="secondary">{reviewScore.toFixed(1)}</Badge>
                {reviewCount !== undefined && (
                  <span className="text-muted-foreground">
                    {reviewCount.toLocaleString()} reviews
                  </span>
                )}
              </div>
            )}

            {visibleAmenities.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {visibleAmenities.map((amenity) => (
                  <Badge key={amenity} variant="outline" className="font-normal">
                    {amenity}
                  </Badge>
                ))}
                {extraCount > 0 && (
                  <Badge variant="outline" className="font-normal">
                    +{extraCount} more
                  </Badge>
                )}
              </div>
            )}
          </CardContent>

          <CardFooter className="flex items-center justify-between p-4 pt-0">
            <div>
              <span className="text-lg font-semibold">
                {new Intl.NumberFormat("en-US", { style: "currency", currency }).format(
                  pricePerNight
                )}
              </span>
              <span className="text-sm text-muted-foreground"> / night</span>
            </div>
            <Button size="sm" onClick={() => onSelect?.(id)}>
              View Details
            </Button>
          </CardFooter>
        </div>
      </div>
    </Card>
  );
}
