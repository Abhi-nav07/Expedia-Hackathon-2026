"use client";

import { ThumbsUp } from "lucide-react";
import { useState } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { RatingStars } from "@/components/travel/rating-stars";
import { cn } from "@/lib/utils/cn";

export interface ReviewCardProps {
  authorName: string;
  authorAvatarUrl?: string;
  rating: number;
  date: string; // ISO string
  content: string;
  helpfulCount?: number;
  /** Extension point for wiring a real "mark helpful" API call later. */
  onMarkHelpful?: () => void;
  className?: string;
}

const TRUNCATE_LENGTH = 280;

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] ?? "") + (parts.length > 1 ? parts[parts.length - 1]?.[0] ?? "" : "")).toUpperCase();
}

export function ReviewCard({
  authorName,
  authorAvatarUrl,
  rating,
  date,
  content,
  helpfulCount = 0,
  onMarkHelpful,
  className,
}: ReviewCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [marked, setMarked] = useState(false);
  const [localHelpfulCount, setLocalHelpfulCount] = useState(helpfulCount);

  const isLong = content.length > TRUNCATE_LENGTH;
  const displayText = expanded || !isLong ? content : `${content.slice(0, TRUNCATE_LENGTH)}…`;

  const handleMarkHelpful = () => {
    if (marked) return; // one mark per view, matches typical review UX
    setMarked(true);
    setLocalHelpfulCount((c) => c + 1);
    onMarkHelpful?.();
  };

  return (
    <Card className={cn("p-4", className)}>
      <CardContent className="space-y-3 p-0">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarImage src={authorAvatarUrl} alt={authorName} />
            <AvatarFallback>{getInitials(authorName)}</AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-medium">{authorName}</p>
            <p className="text-xs text-muted-foreground">
              {new Date(date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
          <RatingStars value={rating} size="sm" className="ml-auto" />
        </div>

        <p className="text-sm leading-relaxed text-foreground/90">
          {displayText}{" "}
          {isLong && (
            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              className="font-medium text-primary hover:underline"
            >
              {expanded ? "Show less" : "Read more"}
            </button>
          )}
        </p>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleMarkHelpful}
          className={cn("gap-1.5 text-muted-foreground", marked && "text-primary")}
        >
          <ThumbsUp className={cn("h-3.5 w-3.5", marked && "fill-current")} />
          Helpful {localHelpfulCount > 0 && `(${localHelpfulCount})`}
        </Button>
      </CardContent>
    </Card>
  );
}
