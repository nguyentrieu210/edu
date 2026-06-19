// vite.config.js
import { defineConfig } from "file:///C:/ike/apps/education_erp/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///C:/ike/apps/education_erp/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import frappeui from "file:///C:/ike/apps/education_erp/frontend/node_modules/frappe-ui/vite/index.js";
import path from "path";
var __vite_injected_original_dirname = "C:\\ike\\apps\\education_erp\\frontend";
var vite_config_default = defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: "../education_erp/www/education_app.html",
        emptyOutDir: true,
        sourcemap: false
      }
    }),
    vue()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "src")
    }
  },
  server: {
    fs: {
      allow: [path.resolve(__vite_injected_original_dirname, "..")]
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxpa2VcXFxcYXBwc1xcXFxlZHVjYXRpb25fZXJwXFxcXGZyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxpa2VcXFxcYXBwc1xcXFxlZHVjYXRpb25fZXJwXFxcXGZyb250ZW5kXFxcXHZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9pa2UvYXBwcy9lZHVjYXRpb25fZXJwL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IGZyYXBwZXVpIGZyb20gJ2ZyYXBwZS11aS92aXRlJ1xuaW1wb3J0IHBhdGggZnJvbSAncGF0aCdcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW1xuICAgIGZyYXBwZXVpKHtcbiAgICAgIGZyYXBwZVByb3h5OiB0cnVlLFxuICAgICAgbHVjaWRlSWNvbnM6IHRydWUsXG4gICAgICBqaW5qYUJvb3REYXRhOiB0cnVlLFxuICAgICAgYnVpbGRDb25maWc6IHtcbiAgICAgICAgaW5kZXhIdG1sUGF0aDogJy4uL2VkdWNhdGlvbl9lcnAvd3d3L2VkdWNhdGlvbl9hcHAuaHRtbCcsXG4gICAgICAgIGVtcHR5T3V0RGlyOiB0cnVlLFxuICAgICAgICBzb3VyY2VtYXA6IGZhbHNlLFxuICAgICAgfSxcbiAgICB9KSxcbiAgICB2dWUoKSxcbiAgXSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7XG4gICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMnKSxcbiAgICB9LFxuICB9LFxuICBzZXJ2ZXI6IHtcbiAgICBmczoge1xuICAgICAgYWxsb3c6IFtwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi4nKV0sXG4gICAgfSxcbiAgfSxcbn0pXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQWtTLFNBQVMsb0JBQW9CO0FBQy9ULE9BQU8sU0FBUztBQUNoQixPQUFPLGNBQWM7QUFDckIsT0FBTyxVQUFVO0FBSGpCLElBQU0sbUNBQW1DO0FBS3pDLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVM7QUFBQSxJQUNQLFNBQVM7QUFBQSxNQUNQLGFBQWE7QUFBQSxNQUNiLGFBQWE7QUFBQSxNQUNiLGVBQWU7QUFBQSxNQUNmLGFBQWE7QUFBQSxRQUNYLGVBQWU7QUFBQSxRQUNmLGFBQWE7QUFBQSxRQUNiLFdBQVc7QUFBQSxNQUNiO0FBQUEsSUFDRixDQUFDO0FBQUEsSUFDRCxJQUFJO0FBQUEsRUFDTjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsS0FBSztBQUFBLElBQ3BDO0FBQUEsRUFDRjtBQUFBLEVBQ0EsUUFBUTtBQUFBLElBQ04sSUFBSTtBQUFBLE1BQ0YsT0FBTyxDQUFDLEtBQUssUUFBUSxrQ0FBVyxJQUFJLENBQUM7QUFBQSxJQUN2QztBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
