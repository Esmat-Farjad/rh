import { defineConfig } from "vite";
import { djangoVitePlugin } from "django-vite-plugin";

export default defineConfig({
  plugins: [
    djangoVitePlugin({
      input: [
        "styles/style.scss", 
        "js/app.js", 
        "js/utils/initSentry.js", 
        "../rh/static/rh/project_planning.js",

        // relative to the folder that vite.config is located
        // "../users/static/users/users.js",
      ],
      // pyArgs: ["--settings=core.settings.production"],
      root: "..",
    }),
  ],
});
