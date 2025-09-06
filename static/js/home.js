const map = L.map('map', { zoomControl: true }).setView([35.681236, 139.767125], 15);

L.tileLayer('https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors, GDL.jp"
}).addTo(map);

fetch('/api/landmarks')
  .then(r => r.json())
  .then(fc => {
    const landmarksLayer = L.geoJSON(fc, {
      style: { color: '#4f46e5', weight: 2, fillOpacity: 0.12 },
      onEachFeature: (feature, layer) => {
        const id = feature.id;
        const name = feature.properties?.name ?? 'この場所';
        const popupHtml = `
          <div class="space-y-2">
            <div class="font-semibold">${name}</div>
            <a class="inline-block px-3 py-1 bg-indigo-600 text-white rounded"
               href="/landmarks/${id}/new">この場所で投稿</a>
            <a class="inline-block px-3 py-1 bg-white border rounded ml-2"
               href="/landmarks/${id}">投稿を読む</a>
          </div>`;
        layer.bindPopup(popupHtml);
      }
    }).addTo(map);

    try {
      map.fitBounds(landmarksLayer.getBounds(), { padding: [20,20] });
    } catch(_) {}
  })
  .catch(err => {
    console.error(err);
    alert('ランドマークの取得に失敗しました');
  });
