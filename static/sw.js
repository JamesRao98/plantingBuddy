const cacheName='v1';

const cacheAssets = [
    "/",
    "/about",
    "/static/title.png",
    "/static/logo.png",
    "/login",
    "/create",
]

self.addEventListener('install',e=>{
  console.log('Service Worker Installed');

  e.waitUntil(
    caches.open(cacheName).then(cache=>{
      console.log('Service Worker Caching Files');
      cache.addAll(cacheAssets);
    }).then(()=>self.skipWaiting())
  )
});

self.addEventListener('activate',e=>{
  console.log('Service Worker Activated')
  e.waitUntil(
    caches.keys().then(cacheNames =>{
      return Promise.all(
        cacheNames.map(cache=>{
          if(cache!=cacheName){
            console.log('Service Worker Clearing Old Cache');
            return caches.delete(cache);
          }
        })
      )
    })
  )
});

self.addEventListener('fetch',e=>{
  console.log('Service Worker Fetching')
  e.respondWith(
    fetch(e.request).catch(()=>caches.match(e.request))
  )
})

self.addEventListener('push', function(event) {
  console.log('Push Received.');

  const title = 'Planting Buddy';
  const options = {
    body: event.data.text(),
    icon: 'static/logo.png',
    vibrate: [50, 50, 50],
  };

  event.waitUntil(self.registration.showNotification(title, options));
});