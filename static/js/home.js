// ====== Leaflet: 地図初期化 ======
const map = L.map("map").setView([35.68, 139.76], 13);
L.tileLayer("https://osm.gdl.jp/styles/osm-bright-ja/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors, GDL.jp",
}).addTo(map);

// ====== 状態 ======
let landmarkLayer = null;
let landmarksGeoJSON = null;
let userMarker = null;
let accuracyCircle = null;
let lastUserPos = null;

// ====== ユーティリティ ======
function popupHTML(feature) {
  const name = feature.properties?.name ?? "ランドマーク";
  let html = `<strong>${name}</strong>`;
  if (feature.properties?.created_at) {
    const createdAt = new Date(feature.properties.created_at);
    html += `<br><small>作成日: ${createdAt.toLocaleString()}</small>`;
  }
  return html;
}

// ====== ランドマーククリック時の処理 ======
function onLandmarkClick(feature) {
  const name = feature.properties?.name ?? "ランドマーク";
  const createdAtStr = feature.properties?.created_at ?? null;
  const createdAtText = createdAtStr ? new Date(createdAtStr).toLocaleString() : "作成日情報なし";

  // 情報表示
  const infoP = document.getElementById("landmark-info");
  if (infoP) infoP.textContent = `${name}（作成日: ${createdAtText}）`;

  // 下パネル表示
  const panel = document.getElementById("landmark-panel");
  if (panel) panel.classList.remove("hidden");

  // 「この場所の投稿を見る」リンクをページ遷移用にセット
  const readLink = document.getElementById("readLink");
  if (readLink) {
    readLink.href = `/others/others_post/${feature.id}`;
    readLink.style.display = "inline-block";
  }

  // 「この場所に投稿する」リンク（任意）
  const postLink = document.getElementById("postLink");
  if (postLink) postLink.href = `/photograph/post?landmark_id=${feature.id}`;
  if (postLink) postLink.style.display = "inline-block";
}

// ====== ユーザー位置マーカー更新 ======
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

// ====== CTA切替（青いボタン or メッセージ） ======
function setCTA(matches) {
  const linkEl = document.getElementById("cta-link");
  const nameEl = document.getElementById("cta-name");
  const msgEl = document.getElementById("cta-msg");

  if (!linkEl || !nameEl || !msgEl) return;

  if (matches.length > 0) {
    const f = matches[0];
    const name = f.properties?.name ?? "ランドマーク";
    nameEl.textContent = name;
    linkEl.href = `/photograph/post?landmark_id=${f.id}`;
    linkEl.style.display = "inline-block";
    msgEl.style.display = "none";
  } else {
    linkEl.style.display = "none";
    msgEl.style.display = "inline";
  }
}

// ====== ランドマーク内判定 ======
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

// ====== ランドマーク読み込み ======
async function loadLandmarks() {
  try {
    const res = await fetch("/api/landmarks");
    const geojson = await res.json();

    if (!geojson || geojson.type !== "FeatureCollection") return;
    landmarksGeoJSON = geojson;

    if (landmarkLayer) map.removeLayer(landmarkLayer);
    landmarkLayer = L.geoJSON(geojson, {
      style: { color: "#2563eb", weight: 2, fillOpacity: 0.15 },
      onEachFeature: (f, layer) => {
        layer.bindPopup(popupHTML(f));
        layer.on("click", () => onLandmarkClick(f));
      },
    }).addTo(map);

    const b = landmarkLayer.getBounds();
    if (b.isValid()) map.fitBounds(b.pad(0.2));

    if (lastUserPos) {
      const { lat, lon, acc } = lastUserPos;
      setCTA(checkInsideAny(lon, lat, acc));
    }
  } catch (e) {
    console.error("Failed to load landmarks:", e);
  }
}

// ====== Geolocation ======
function onGeoSuccess(pos) {
  const { latitude, longitude, accuracy } = pos.coords;
  updateUserMarker(latitude, longitude, accuracy);
  lastUserPos = { lat: latitude, lon: longitude, acc: accuracy };
  setCTA(checkInsideAny(longitude, latitude, accuracy));
}

function onGeoError(err) {
  const msgEl = document.getElementById("cta-msg");
  if (msgEl) msgEl.textContent = `位置情報が取得できません（${err.message}）`;
}

if (navigator.geolocation) {
  navigator.geolocation.watchPosition(onGeoSuccess, onGeoError, {
    enableHighAccuracy: true,
    maximumAge: 10_000,
    timeout: 10_000,
  });
} else {
  const msgEl = document.getElementById("cta-msg");
  if (msgEl) msgEl.textContent = "この端末は位置情報に未対応です";
}

// ====== 初期化 ======
loadLandmarks();
