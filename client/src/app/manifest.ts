import type { MetadataRoute } from "next";
export default function manifest(): MetadataRoute.Manifest {
  return { name: "CivicLens", short_name: "CivicLens", description: "Report and track civic issues",
    start_url: "/dashboard", scope: "/", display: "standalone", background_color: "#EDF0F4",
    theme_color: "#1B4F9C", icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
    ] };
}
