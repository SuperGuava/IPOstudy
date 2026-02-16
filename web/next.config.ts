import type { NextConfig } from "next";

const defaultDistDir = process.env.NODE_ENV === "production" ? ".next-build" : ".next-dev";

const nextConfig: NextConfig = {
  distDir: process.env.NEXT_DIST_DIR || defaultDistDir,
};

export default nextConfig;
