// 地図
const map = L.map('map', { zoomControl: true }).setView([35.681236, 139.767125], 15);

L.tileLayer('https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors, GDL.jp"
}).addTo(map);

// ← 追加：サイドパネル更新関数（地図横に表示）
function showPanel(id, name) {
  const panel = document.getElementById('landmark-panel');
  if (!panel) return; // パネルが無い環境でも安全に

  panel.classList.remove('hidden');
  document.getElementById('lmName').textContent = name || 'この場所';
  document.getElementById('postLink').href = `/landmarks/${id}/new`;
  document.getElementById('readLink').href = `/landmarks/${id}`;
}

fetch('/api/landmarks')
  .then(r => r.json())
  .then(fc => {
    const landmarksLayer = L.geoJSON(fc, {
      style: { color: '#4f46e5', weight: 2, fillOpacity: 0.12 },
      onEachFeature: (feature, layer) => {
        const id   = feature.id;
        const name = feature.properties?.name ?? 'この場所';

        // ▼ ここだけ変更（ポップアップはやめてサイドパネルに出す）
        layer.on('click', () => {
          showPanel(id, name);

          // モバイルでサイドパネルが下に出る場合の視線移動用（任意）
          const panel = document.getElementById('landmark-panel');
          if (panel && window.matchMedia('(max-width: 1023px)').matches) {
            panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });

        // （必要なら従来のポップアップを残すなら下記をアンコメント）
        // const popupHtml = `
        //   <div class="space-y-2">
        //     <div class="font-semibold">${name}</div>
        //     <a class="inline-block px-3 py-1 bg-indigo-600 text-white rounded"
        //        href="/landmarks/${id}/new">この場所で投稿</a>
        //     <a class="inline-block px-3 py-1 bg-white border rounded ml-2"
        //        href="/landmarks/${id}">投稿を読む</a>
        //   </div>`;
        // layer.bindPopup(popupHtml);
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