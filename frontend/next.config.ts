import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produit un serveur autonome et léger, idéal pour une image Docker.
  output: "standalone",
};

export default nextConfig;