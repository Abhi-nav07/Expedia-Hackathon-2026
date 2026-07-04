"use client";

import { MapPin } from "lucide-react";
import mapboxgl from "mapbox-gl";
import { useEffect, useRef } from "react";

import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/utils/cn";

import "mapbox-gl/dist/mapbox-gl.css";

export interface MapMarker {
  id: string;
  latitude: number;
  longitude: number;
  label?: string;
}

export interface MapContainerProps {
  markers: MapMarker[];
  /** Defaults to the average of all marker coordinates if not given. */
  center?: { latitude: number; longitude: number };
  zoom?: number;
  onMarkerClick?: (markerId: string) => void;
  className?: string;
}

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPS_API_KEY;

function computeCenter(markers: MapMarker[]): { latitude: number; longitude: number } {
  if (markers.length === 0) return { latitude: 0, longitude: 0 };
  const sum = markers.reduce(
    (acc, m) => ({ latitude: acc.latitude + m.latitude, longitude: acc.longitude + m.longitude }),
    { latitude: 0, longitude: 0 }
  );
  return { latitude: sum.latitude / markers.length, longitude: sum.longitude / markers.length };
}

/**
 * Generic Mapbox GL wrapper — knows nothing about what a marker
 * represents (hotel, destination, flight route waypoint, etc.). Reads
 * NEXT_PUBLIC_MAPS_API_KEY from env (set in .env, empty by default —
 * see Module 01's .env.example). When unset, renders a graceful
 * fallback instead of crashing, since most of the hackathon will likely
 * run without a Mapbox token configured until it's actually needed.
 */
export function MapContainer({
  markers,
  center,
  zoom = 11,
  onMarkerClick,
  className,
}: MapContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  useEffect(() => {
    if (!MAPBOX_TOKEN || !containerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;
    const resolvedCenter = center ?? computeCenter(markers);

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/streets-v12",
      center: [resolvedCenter.longitude, resolvedCenter.latitude],
      zoom,
    });
    map.addControl(new mapboxgl.NavigationControl(), "top-right");
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // Intentionally re-init only on token/zoom change, not on every
    // markers/center reference change — marker sync is handled below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zoom]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Clear previous markers before re-adding — avoids leaking DOM
    // nodes/listeners when the `markers` prop changes.
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    markers.forEach((markerData) => {
      const el = document.createElement("div");
      el.style.cursor = onMarkerClick ? "pointer" : "default";

      const marker = new mapboxgl.Marker({ color: "#0284c7" })
        .setLngLat([markerData.longitude, markerData.latitude])
        .addTo(map);

      if (markerData.label) {
        marker.setPopup(new mapboxgl.Popup({ offset: 24 }).setText(markerData.label));
      }

      if (onMarkerClick) {
        marker.getElement().addEventListener("click", () => onMarkerClick(markerData.id));
      }

      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
    };
  }, [markers, onMarkerClick]);

  if (!MAPBOX_TOKEN) {
    return (
      <div className={cn("flex min-h-[300px] items-center justify-center rounded-lg border border-border bg-muted/30", className)}>
        <EmptyState
          icon={MapPin}
          title="Map not configured"
          description="Set NEXT_PUBLIC_MAPS_API_KEY in .env to enable the map."
        />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("min-h-[300px] w-full overflow-hidden rounded-lg", className)}
      role="region"
      aria-label="Map"
    />
  );
}
