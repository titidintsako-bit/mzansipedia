const SW_VERSION = '2.3.1';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener("fetch", (event) => {
  const filename = new URL(event.request.url).pathname.split("/").at(-1);
  if (filename == "clearHtml")
    return event.respondWith((async () => {
      await caches.delete("html");
      return new Response("cleared", {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      });
    })());
  if (filename == "swVer")
    return event.respondWith((()=>new Response(SW_VERSION, {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      }))());
  if (!["", "index.html", "app.webmanifest", "favicon.ico", "favicon-48.png", "favicon-256.png", "smoldata.json"].includes(filename))
    return;
  event.respondWith((async () => {
    const request = event.request;
    const cachedResponse = await caches.match(request);
    if (cachedResponse)
      return cachedResponse;
    const isSmolData = filename == "smoldata.json";
    if (isSmolData)
      await caches.delete("smoldata");
    const cache = await caches.open(isSmolData ? "smoldata" : "html");
    try {
      const networkResponse = await fetch(request);
      if (isSmolData)
        progressMonitor(event.clientId, networkResponse.clone());
      event.waitUntil(cache.put(request, networkResponse.clone()).catch(() => {}));
      return networkResponse;
    } catch (error) {
      return new Response("Network error happened", {
        status: 408,
        headers: { "Content-Type": "text/plain" },
      });
    }
  })());
});


// based on https://github.com/anthumchris/fetch-progress-indicators/blob/master/sw-basic/sw-simple.js
function progressMonitor(clientId, response) {
  if (!response.body) {
    return response;
  }
  if (!response.ok) {
    // HTTP error code response
    return response;
  }

  let loaded = 0;
  const reader = response.body.getReader();

  return new Response(
    new ReadableStream({
      start(controller) {        
        // get client to post message. Awaiting resolution first read() progress
        // is sent for progress indicator accuracy
        let client;
        clients.get(clientId).then(c => {
          client = c;
          read();
        });

        function read() {
          reader.read().then(({done, value}) => {
            if (done) {
              controller.close();
              return;
            }

            controller.enqueue(value);
            loaded += value.byteLength;
            if (client)
              client.postMessage({event:"downloadProgress",data:loaded})
            read();
          })
          .catch(error => {
            controller.error(error);
          });
        }
      },

      cancel() {}
    })
  )
}
