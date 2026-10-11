# Spark Notebook

Offline-first, illustrated learning app (science, engineering, electricity, electronics). No accounts, no server code. Everything (progress, quiz history, saved cards, downloaded topics) is stored on the device.

## Files
- `index.html` – the whole app
- `sw.js` – service worker: caches the app so it opens with no connection
- `packs/*.json` – one topic per file (lessons, cards with sketches, quizzes); `catalog.json` lists them
- `manifest.webmanifest`, icons – lets you install it to the home screen

## Run it (pick one)

**iPhone / Android – recommended.** Offline mode needs the app to be served over HTTPS once, then it's installed and runs without a connection.
1. Create a free GitHub repo, upload the contents of this folder, then Settings → Pages → Deploy from branch `main` / root.
2. Open `https://<you>.github.io/<repo>/` in Safari (or Chrome on Android).
3. Share → **Add to Home Screen**. Open it once online, download your topics in **Learn**, and from then on it works in flight mode.

**Homelab.** Any static web server behind your existing HTTPS reverse proxy works, e.g.
`docker run -d --name spark -p 8088:80 -v $PWD/spark:/usr/share/nginx/html:ro nginx:alpine`
(service workers require HTTPS, except on `localhost`).

**Laptop, quick test.** In this folder run `python3 -m http.server 8000` and open `http://localhost:8000`.

**No server at all.** Double-click `index.html` in Chrome, Edge or Firefox. It runs and remembers your history; packs are installed from the copy built into the file. (iPhone's Files preview does not run apps, so use one of the options above on a phone.)

## Adding your own topic packs
Copy any file in `packs/`, change `id`, `topic`, `title` and the ideas, then either:
- add it to `catalog.json` on your server so it appears in Library, or
- in the app, **Learn → Import topic file**.

Topic keys: `elec`, `tron`, `mech`, `sci`. Sketches are inline SVG; use the classes `s` (ink), `a` (blue pen), `r` (red pen), `y` (highlighter), `bgf` (paper fill) so they follow light and dark mode.

## Keeping your history safe
**You → Save backup file** writes everything to one JSON file; **Restore from file** brings it back on any device. Installing to the home screen also stops iOS from clearing site data after a week of no use.

## Using it on a flight
- **Phone (best):** install it once from your HTTPS host with **Add to Home Screen**, open it online, and download the topics in **Learn**. It then works fully in flight mode, including quizzes, favourites and history.
- **Google Drive:** Drive can store `spark-notebook.html`, but its preview won't run the app on a phone. Keep `spark-notebook-offline.pdf` in Drive and mark it **Available offline**: it has every lesson, sketch and quiz answer.
- **Laptop:** download `spark-notebook.html` from Drive before the flight and open it in Chrome, Edge, Firefox or Safari.

