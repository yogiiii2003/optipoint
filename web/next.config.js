/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disabled due to react-leaflet 4.2.1 double-unmount bug in dev.
  // Strict Mode only affects development builds; production behavior is unchanged.
  reactStrictMode: false,
  output: "standalone",
};
module.exports = nextConfig;
