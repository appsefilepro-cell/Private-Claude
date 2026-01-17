# Getting Started with Vercel Speed Insights

This guide will help you get started with using Vercel Speed Insights on your Agent X5.0 project, showing you how to enable it, add the package to your project, deploy your app to Vercel, and view your data in the dashboard.

To view instructions on using Vercel Speed Insights in your project for your framework, use the **Choose a framework** dropdown on the right (at the bottom in mobile view).

## Prerequisites

- A Vercel account. If you don't have one, you can [sign up for free](https://vercel.com/signup).
- A Vercel project. If you don't have one, you can [create a new project](https://vercel.com/new).
- The Vercel CLI installed. If you don't have it, you can install it using the following command:

```bash
# Using npm
npm i -g vercel

# Using yarn
yarn global add vercel

# Using pnpm
pnpm i -g vercel

# Using bun
bun add -g vercel
```

## Setup Instructions

### Enable Speed Insights in Vercel

On the [Vercel dashboard](/dashboard), select your Project followed by the **Speed Insights** tab. You can also select the button below to be taken there. Then, select **Enable** from the dialog.

> **💡 Note:** Enabling Speed Insights will add new routes (scoped at `/_vercel/speed-insights/*`) after your next deployment.

### Add `@vercel/speed-insights` to your project (For Frontend/Static Sites)

If your project includes a frontend application, use the package manager of your choice to add the `@vercel/speed-insights` package to your project:

```bash
# Using pnpm
pnpm i @vercel/speed-insights

# Using yarn
yarn add @vercel/speed-insights

# Using npm
npm install @vercel/speed-insights

# Using bun
bun add @vercel/speed-insights
```

> **💡 Note:** When using the HTML implementation without any package manager, there is no need to install the `@vercel/speed-insights` package.

### Framework-Specific Integration

#### For Next.js Projects

The `SpeedInsights` component is a wrapper around the tracking script, offering seamless integration with Next.js.

**For Next.js 13.5+:**

Add the following component to your main app file:

```tsx
// pages/_app.tsx
import type { AppProps } from 'next/app';
import { SpeedInsights } from '@vercel/speed-insights/next';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <SpeedInsights />
    </>
  );
}

export default MyApp;
```

```jsx
// pages/_app.jsx
import { SpeedInsights } from "@vercel/speed-insights/next";

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <SpeedInsights />
    </>
  );
}

export default MyApp;
```

**For Next.js App Router (13.5+):**

Add the following component to the root layout:

```tsx
// app/layout.tsx
import { SpeedInsights } from "@vercel/speed-insights/next";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>Next.js</title>
      </head>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

```jsx
// app/layout.jsx
import { SpeedInsights } from "@vercel/speed-insights/next";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>Next.js</title>
      </head>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

**For versions of Next.js older than 13.5:**

Import the `<SpeedInsights>` component from `@vercel/speed-insights/react`. Then pass it the pathname of the route:

```tsx
// pages/example-component.tsx
import { SpeedInsights } from "@vercel/speed-insights/react";
import { useRouter } from "next/router";

export default function Layout() {
  const router = useRouter();
  return <SpeedInsights route={router.pathname} />;
}
```

```jsx
// pages/example-component.jsx
import { SpeedInsights } from "@vercel/speed-insights/react";
import { useRouter } from "next/router";

export default function Layout() {
  const router = useRouter();
  return <SpeedInsights route={router.pathname} />;
}
```

#### For React Applications (Create React App, Vite, etc.)

The `SpeedInsights` component is a wrapper around the tracking script, offering seamless integration with React.

Add the following component to the main app file:

```tsx
// App.tsx
import { SpeedInsights } from '@vercel/speed-insights/react';

export default function App() {
  return (
    <div>
      {/* ... */}
      <SpeedInsights />
    </div>
  );
}
```

```jsx
// App.jsx
import { SpeedInsights } from "@vercel/speed-insights/react";

export default function App() {
  return (
    <div>
      {/* ... */}
      <SpeedInsights />
    </div>
  );
}
```

#### For Remix Projects

The `SpeedInsights` component is a wrapper around the tracking script, offering seamless integration with Remix.

Add the following component to your root file:

```tsx
// app/root.tsx
import { SpeedInsights } from '@vercel/speed-insights/remix';

export default function App() {
  return (
    <html lang="en">
      <body>
        {/* ... */}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

```jsx
// app/root.jsx
import { SpeedInsights } from "@vercel/speed-insights/remix";

export default function App() {
  return (
    <html lang="en">
      <body>
        {/* ... */}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

#### For SvelteKit Projects

Call the `injectSpeedInsights` function in your app:

```ts
// src/routes/+layout.ts
import { injectSpeedInsights } from "@vercel/speed-insights/sveltekit";

injectSpeedInsights();
```

```js
// src/routes/+layout.js
import { injectSpeedInsights } from "@vercel/speed-insights/sveltekit";

injectSpeedInsights();
```

#### For Vue/Nuxt Projects

The `SpeedInsights` component is a wrapper around the tracking script, offering seamless integration with Vue and Nuxt.

**For Vue:**

Add the following component to the main app template:

```ts
<!-- src/App.vue -->
<script setup lang="ts">
import { SpeedInsights } from '@vercel/speed-insights/vue';
</script>

<template>
  <SpeedInsights />
</template>
```

```js
<!-- src/App.vue -->
<script setup>
import { SpeedInsights } from '@vercel/speed-insights/vue';
</script>

<template>
  <SpeedInsights />
</template>
```

**For Nuxt:**

Add the following component to the default layout:

```ts
<!-- layouts/default.vue -->
<script setup lang="ts">
import { SpeedInsights } from '@vercel/speed-insights/vue';
</script>

<template>
  <SpeedInsights />
</template>
```

```js
<!-- layouts/default.vue -->
<script setup>
import { SpeedInsights } from '@vercel/speed-insights/vue';
</script>

<template>
  <SpeedInsights />
</template>
```

#### For Astro Projects

Speed Insights is available for both static and SSR Astro apps.

To enable this feature, declare the `<SpeedInsights />` component from `@vercel/speed-insights/astro` near the bottom of one of your layout components, such as `BaseHead.astro`:

```astro
<!-- BaseHead.astro -->
---
import SpeedInsights from '@vercel/speed-insights/astro';
const { title, description } = Astro.props;
---
<title>{title}</title>
<meta name="title" content={title} />
<meta name="description" content={description} />

<SpeedInsights />
```

**Optional: Remove sensitive information from URLs**

You can remove sensitive information from the URL by adding a `speedInsightsBeforeSend` function to the global `window` object. The `<SpeedInsights />` component will call this method before sending any data to Vercel:

```astro
<!-- BaseHead.astro -->
---
import SpeedInsights from '@vercel/speed-insights/astro';
const { title, description } = Astro.props;
---
<title>{title}</title>
<meta name="title" content={title} />
<meta name="description" content={description} />

<script is:inline>
  function speedInsightsBeforeSend(data){
    console.log("Speed Insights before send", data)
    return data;
  }
</script>
<SpeedInsights />
```

#### For Plain HTML

Add the following scripts before the closing tag of the `<body>`:

```html
<!-- index.html -->
<script>
  window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
```

#### For Other Frameworks

Import the `injectSpeedInsights` function from the package, which will add the tracking script to your app. **This should only be called once in your app, and must run in the client**.

Add the following code to your main app file:

```ts
// main.ts
import { injectSpeedInsights } from "@vercel/speed-insights";

injectSpeedInsights();
```

```js
// main.js
import { injectSpeedInsights } from "@vercel/speed-insights";

injectSpeedInsights();
```

### Deploy Your App to Vercel

You can deploy your app to Vercel's global [CDN](/docs/cdn) by running the following command from your terminal:

```bash
vercel deploy
```

Alternatively, you can [connect your project's git repository](/docs/git#deploying-a-git-repository), which will enable Vercel to deploy your latest pushes and merges to main.

Once your app is deployed, it's ready to begin tracking performance metrics.

> **💡 Note:** If everything is set up correctly, you should be able to find the `/_vercel/speed-insights/script.js` script inside the body tag of your page.

### View Your Data in the Dashboard

Once your app is deployed, and users have visited your site, you can view the data in the dashboard.

To do so, go to your [dashboard](/dashboard), select your project, and click the **Speed Insights** tab.

After a few days of visitors, you'll be able to start exploring your metrics. For more information on how to use Speed Insights, see the [Using Speed Insights](/docs/speed-insights/using-speed-insights) documentation.

## For FastAPI Backends

If your Agent X5.0 system includes a FastAPI backend for frontend dashboards or API operations, Speed Insights will track the performance of any frontend served from Vercel. The FastAPI backend itself should implement its own performance monitoring using tools like:

- **OpenTelemetry** - Distributed tracing
- **Prometheus** - Metrics collection (already configured in this project)
- **Grafana** - Metrics visualization (already configured in this project)

See the [Deployment Guide](./DEPLOYMENT_GUIDE.md) for more information on monitoring the FastAPI backend.

## Privacy and Compliance

Learn more about how Vercel supports [privacy and data compliance standards](/docs/speed-insights/privacy-policy) with Vercel Speed Insights.

## Next Steps

Now that you have Vercel Speed Insights set up, you can explore the following topics to learn more:

- [Learn how to use the `@vercel/speed-insights` package](/docs/speed-insights/package)
- [Learn about metrics](/docs/speed-insights/metrics)
- [Read about privacy and compliance](/docs/speed-insights/privacy-policy)
- [Explore pricing](/docs/speed-insights/limits-and-pricing)
- [Troubleshooting](/docs/speed-insights/troubleshooting)

## Additional Resources

For more information on monitoring and performance optimization for the Agent X5.0 system:

- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - System deployment instructions
- [Main README](../README.md) - Agent X5.0 overview and capabilities
