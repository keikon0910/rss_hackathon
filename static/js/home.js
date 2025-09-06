// ====== Leaflet: 地図初期化 ======
const map = L.map("map").setView([35.6809591, 139.7673068], 15);
L.tileLayer("https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors, GDL.jp",
}).addTo(map);
// ====== 状態 ======
let landmarkLayer = null;        // ランドマーク描画レイヤ
let landmarksGeoJSON = null;     // 判定用に保持
let userMarker = null;           // 自分の位置マーカー
let accuracyCircle = null;       // 誤差円
let lastUserPos = null;          // 直近の {lat, lon, acc}
// ====== ユーティリティ ======
function popupHTML(feature) {
  const id = feature.id;
  const name = feature.properties?.name ?? "ランドマーク";
  return `
    <div>
      <strong>${name}</strong><br/>
      <a href="/landmarks/${id}">詳細を見る</a><br/>
      <a href="/landmarks/${id}/post/new">この場所で投稿</a>
    </div>`;
}
function updateUserMarker(lat, lon, acc) {
  const latlng = [lat, lon];
  if (!userMarker) {
    userMarker = L.marker(latlng).addTo(map).bindPopup("あなたの位置");
  } else {
    userMarker.setLatLng(latlng);
  }
  if (!accuracyCircle) {
    accuracyCircle = L.circle(latlng, { radius: acc }).addTo(map);
  } else {
    accuracyCircle.setLatLng(latlng);
    accuracyCircle.setRadius(acc);
  }
}
function setCTA(matches) {
    const box = document.getElementById("post-cta");
    if (!box) return;
    // 既存が無ければ作る（href はサーバ側で解決されているヘッダーの「投稿」と同じにしたい場合は後で差し替え可）
    let link = document.getElementById("cta-link");
    let nameSpan = document.getElementById("cta-name");
    let msg = document.getElementById("cta-msg");
    if (!link || !nameSpan || !msg) {
      box.innerHTML = `
        <a id="cta-link" href="${(window.POST_URL || '#')}"
           style="display:none;padding:10px 14px;border-radius:8px;background:#2563eb;color:#fff;text-decoration:none;">
          この場所（<span id="cta-name">ランドマーク</span>）で投稿
        </a>
        <span id="cta-msg" style="color:#666;">近くのランドマーク内ではありません</span>
      `;
      link = document.getElementById("cta-link");
      nameSpan = document.getElementById("cta-name");
      msg = document.getElementById("cta-msg");
    }
    // マッチしたらボタン表示、しなければメッセージ
    if (matches && matches.length > 0) {
      const f = matches[0];
      const name = f?.properties?.name ?? "ランドマーク";
      nameSpan.textContent = name;
      // POST_URL が未設定なら # にしておく（必要なら window.POST_URL を home.html で埋めてね）
      if (window.POST_URL) link.setAttribute("href", window.POST_URL);
      link.style.display = "inline-block";
      msg.style.display = "none";
    } else {
      link.style.display = "none";
      msg.style.display = "";
    }
  }
// 点 ∈ ポリゴン（境界ブレ救済に微バッファ）
function checkInsideAny(lon, lat, accuracyMeters = 30) {
  if (!landmarksGeoJSON || !landmarksGeoJSON.features) return [];
  const pt = turf.point([lon, lat]);
  const bufferKm = Math.max(accuracyMeters, 30) / 1000;
  const hits = [];
  for (const f of landmarksGeoJSON.features) {
    let inside = false;
    try {
      inside = turf.booleanPointInPolygon(pt, f);
      if (!inside) {
        const buffered = turf.buffer(f, bufferKm, { units: "kilometers" });
        inside = turf.booleanPointInPolygon(pt, buffered);
      }
    } catch (_) {}
    if (inside) hits.push(f);
  }
  return hits;
}
// ====== ランドマークの取得・描画 ======
async function loadLandmarks() {
  const res = await fetch("/api/landmarks");
  const geojson = await res.json();
  // 形チェック & 破損Feature除外
  if (!geojson || geojson.type !== "FeatureCollection" || !Array.isArray(geojson.features)) {
    console.error("Invalid /api/landmarks payload:", geojson);
    return;
  }
  geojson.features = geojson.features.filter(f => {
    const g = f && f.geometry;
    return g && typeof g === "object" && Array.isArray(g.coordinates);
  });
  landmarksGeoJSON = geojson;
  // 描画
  if (landmarkLayer) map.removeLayer(landmarkLayer);
  try {
    landmarkLayer = L.geoJSON(geojson, {
      style: { weight: 2, fillOpacity: 0.15 },
      onEachFeature: (f, layer) => layer.bindPopup(popupHTML(f)),
    }).addTo(map);
    const b = landmarkLayer.getBounds();
    if (b.isValid()) map.fitBounds(b.pad(0.2));
  } catch (e) {
    console.error("Leaflet L.geoJSON failed:", e, geojson);
  }
  // ★ レースコンディション対策：ロード後に再判定
  if (lastUserPos) {
    const { lat, lon, acc } = lastUserPos;
    setCTA(checkInsideAny(lon, lat, acc));
  }
}
loadLandmarks();
// 手動リロード用に公開（任意）
window.loadLandmarks = loadLandmarks;
// ====== Geolocation（常時追随） ======
function onGeoSuccess(pos) {
  const { latitude, longitude, accuracy } = pos.coords;
  updateUserMarker(latitude, longitude, accuracy);
  lastUserPos = { lat: latitude, lon: longitude, acc: accuracy };
  setCTA(checkInsideAny(longitude, latitude, accuracy));
}
function onGeoError(err) {
  console.warn("Geolocation error:", err);
  const el = document.getElementById("post-cta");
  if (el) el.innerHTML = `<span style="color:#b91c1c;">位置情報が取得できません（${err.message}）</span>`;
}
if (navigator.geolocation) {
  navigator.geolocation.watchPosition(onGeoSuccess, onGeoError, {
    enableHighAccuracy: true,
    maximumAge: 10_000,
    timeout: 10_000,
  });
} else {
  const el = document.getElementById("post-cta");
  if (el) el.textContent = "この端末は位置情報に未対応です";
}
// // ====== 地図の初期化 ======
// const map = L.map("map").setView([35.6809591, 139.7673068], 15);
// L.tileLayer("https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png", {
//   attribution: "© OpenStreetMap contributors, GDL.jp",
// }).addTo(map);
// // ====== ランドマークの描画 ======
// let landmarkLayer = null;        // Leafletレイヤ
// let landmarksGeoJSON = null;     // Turf 判定用に保持
// function popupHTML(feature) {
//   const id = feature.id;
//   const name = feature.properties?.name ?? "ランドマーク";
//   return `
//     <div>
//       <strong>${name}</strong><br>
//       <a href="/landmarks/${id}">詳細を見る</a><br>
//       <a href="/landmarks/${id}/post/new">この場所で投稿</a>
//     </div>`;
// }
// async function loadLandmarks() {
//   const res = await fetch("/api/landmarks");
//   const geojson = await res.json();
//   landmarksGeoJSON = geojson;
//   if (landmarkLayer) map.removeLayer(landmarkLayer);
//   landmarkLayer = L.geoJSON(geojson, {
//     style: { weight: 2, fillOpacity: 0.15 },
//     onEachFeature: (f, layer) => layer.bindPopup(popupHTML(f)),
//   }).addTo(map);
//   try {
//     const b = landmarkLayer.getBounds();
//     if (b.isValid()) map.fitBounds(b.pad(0.2));
//   } catch {}
// }
// loadLandmarks();
// // ====== ユーザー位置の表示 & CTA（投稿ボタン） ======
// let userMarker = null;
// let accuracyCircle = null;
// function updateUserMarker(lat, lon, acc) {
//   const latlng = [lat, lon];
//   if (!userMarker) {
//     userMarker = L.marker(latlng).addTo(map).bindPopup("あなたの位置");
//   } else {
//     userMarker.setLatLng(latlng);
//   }
//   if (!accuracyCircle) {
//     accuracyCircle = L.circle(latlng, { radius: acc }).addTo(map);
//   } else {
//     accuracyCircle.setLatLng(latlng);
//     accuracyCircle.setRadius(acc);
//   }
// }
// // CTA（投稿）を表示/非表示
// function setCTA(matches) {
//   const el = document.getElementById("post-cta");
//   if (!el) return;
//   if (matches.length > 0) {
//     const f = matches[0]; // 複数一致時は先頭を採用（必要なら選択UIに拡張）
//     const name = f.properties?.name ?? "ランドマーク";
//     el.innerHTML = `
//       <a href="/landmarks/${f.id}/post/new"
//          style="display:inline-block;padding:10px 14px;border-radius:8px;background:#2563eb;color:#fff;text-decoration:none;">
//         この場所（${name}）で投稿
//       </a>`;
//   } else {
//     el.innerHTML = `<span style="color:#666;">近くのランドマーク内ではありません</span>`;
//   }
// }
// // Turf.js を使って「点 ∈ ポリゴン？」を判定
// function checkInsideAny(lon, lat, accuracyMeters = 30) {
//   if (!landmarksGeoJSON || !landmarksGeoJSON.features) return [];
//   const pt = turf.point([lon, lat]);
//   // GPSブレ救済：境界付近で落ちないように少しだけバッファ（accuracy と 30m の大きい方）
//   const bufferKm = Math.max(accuracyMeters, 30) / 1000;
//   const matches = [];
//   for (const f of landmarksGeoJSON.features) {
//     let inside = false;
//     try {
//       inside = turf.booleanPointInPolygon(pt, f);
//       if (!inside) {
//         const buffered = turf.buffer(f, bufferKm, { units: "kilometers" });
//         inside = turf.booleanPointInPolygon(pt, buffered);
//       }
//     } catch (e) {
//       // invalid geometry などはスキップ
//     }
//     if (inside) matches.push(f);
//   }
//   return matches;
// }
// // Geolocation: 位置を監視してマーカーとCTAを更新
// function onGeoSuccess(pos) {
//   const { latitude, longitude, accuracy } = pos.coords;
//   updateUserMarker(latitude, longitude, accuracy);
//   const inside = checkInsideAny(longitude, latitude, accuracy);
//   setCTA(inside);
// }
// function onGeoError(err) {
//   console.warn("Geolocation error:", err);
//   const el = document.getElementById("post-cta");
//   if (el) el.innerHTML = `<span style="color:#b91c1c;">位置情報が取得できません（${err.message}）</span>`;
// }
// // 位置情報の監視を開始
// if (navigator.geolocation) {
//   navigator.geolocation.watchPosition(onGeoSuccess, onGeoError, {
//     enableHighAccuracy: true,
//     maximumAge: 10_000,
//     timeout: 10_000,
//   });
// } else {
//   const el = document.getElementById("post-cta");
//   if (el) el.textContent = "この端末は位置情報に未対応です";
// }