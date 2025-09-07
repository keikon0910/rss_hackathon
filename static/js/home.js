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

// 投稿ページのベースURL（テンプレから受け取る）
const postBase = document.body.dataset.postBase || "/post";

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

// 文字列 → JSON 安全パーサ
function safeParseJSON(s) { try { return JSON.parse(s); } catch { return null; } }

// Feature 正規化（geometry が文字列なら JSON に、壊れてたら除外）
function normalizeFeatures(fc) {
  const out = [];
  for (const f of (fc.features || [])) {
    let g = f.geometry;
    if (typeof g === "string") g = safeParseJSON(g);
    if (!g || !g.type || !Array.isArray(g.coordinates)) continue;
    out.push({ ...f, geometry: g });
  }
  return { type: "FeatureCollection", features: out };
}

// ====== ランドマーククリック時 ======
function onLandmarkClick(feature) {
  const name = feature.properties?.name ?? "ランドマーク";
  const createdAtStr = feature.properties?.created_at ?? null;
  const createdAtText = createdAtStr ? new Date(createdAtStr).toLocaleString() : "作成日情報なし";

  const infoP = document.getElementById("landmark-info");
  if (infoP) infoP.textContent = `${name}（作成日: ${createdAtText}）`;

  const panel = document.getElementById("landmark-panel");
  if (panel) panel.classList.remove("hidden");

  const postLink = document.getElementById("postLink");
  if (postLink) {
    postLink.href = `${postBase}?landmark_id=${encodeURIComponent(feature.id)}`;
    postLink.classList.remove("hidden");
  }

  const readLink = document.getElementById("readLink");
  if (readLink) {
    readLink.dataset.href = `/others/others_post/${feature.id}`;
    readLink.href = "#";
    readLink.style.pointerEvents = "none";
    readLink.style.opacity = "0.5";
    readLink.classList.remove("hidden");
  }

  // ユーザーがそのランドマーク内にいる場合のみ投稿可
  if (lastUserPos) {
    const { lat, lon, acc } = lastUserPos;
    const inside = checkInsideAny(lon, lat, acc).some(f => f.id === feature.id);

    if (!inside && postLink) postLink.classList.add("hidden");

    if (inside && readLink) {
      readLink.style.pointerEvents = "auto";
      readLink.style.opacity = "1";
      readLink.href = readLink.dataset.href;
    }
  }
}

// ====== CTA切替（青いボタン or メッセージ） ======
function setCTA(matches) {
  const linkEl   = document.getElementById("cta-link");
  const nameEl   = document.getElementById("cta-name");
  const msgEl    = document.getElementById("cta-msg");
  const readLink = document.getElementById("readLink");

  if (!linkEl || !nameEl || !msgEl) return;

  if (matches.length > 0) {
    const f = matches[0];
    const name = f.properties?.name ?? "ランドマーク";
    nameEl.textContent = name;
    linkEl.href = `${postBase}?landmark_id=${encodeURIComponent(f.id)}`;
    linkEl.classList.remove("hidden");
    msgEl.classList.add("hidden");

    if (readLink) {
      readLink.style.pointerEvents = "auto";
      readLink.style.opacity = "1";
      readLink.href = readLink.dataset.href ?? "#";
    }
  } else {
    linkEl.classList.add("hidden");
    msgEl.classList.remove("hidden");

    if (readLink) {
      readLink.style.pointerEvents = "none";
      readLink.style.opacity = "0.5";
      readLink.href = "#";
    }
  }
}

// ====== ユーザー位置マーカー ======
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

// ====== 点がランドマーク内か判定 ======
function checkInsideAny(lon, lat, accuracyMeters = 30) {
  if (!landmarksGeoJSON || !landmarksGeoJSON.features) return [];
  const pt = turf.point([lon, lat]);
  const bufferKm = Math.max(accuracyMeters, 30) / 1000; // 最低30m緩衝

  const hits = [];
  for (const f of landmarksGeoJSON.features) {
    let inside = false;
    try {
      inside = turf.booleanPointInPolygon(pt, f);
      if (!inside) {
        const buffered = turf.buffer(f, bufferKm, { units: "kilometers" });
        inside = turf.booleanPointInPolygon(pt, buffered);
      }
    } catch (e) {
      console.warn("turf check failed on feature:", f?.id, e);
    }
    if (inside) hits.push(f);
  }
  return hits;
}

// ====== ランドマーク読み込み（重要：文字列geometryを正規化） ======
async function loadLandmarks() {
  try {
    const res = await fetch("/api/landmarks", { credentials: "same-origin" });
    if (!res.ok) {
      const text = await res.text();
      console.error("landmarks HTTP error:", res.status, text.slice(0, 300));
      return;
    }

    let raw;
    try {
      raw = await res.json();
    } catch {
      const bad = await res.clone().text().catch(() => "");
      console.error("landmarks JSON parse failed. head:", bad.slice(0, 300));
      return;
    }

    if (!raw || raw.type !== "FeatureCollection" || !Array.isArray(raw.features)) {
      console.error("Invalid GeoJSON:", raw);
      return;
    }

    const geojson = normalizeFeatures(raw);
    landmarksGeoJSON = geojson;

    // 描画
    if (landmarkLayer) map.removeLayer(landmarkLayer);
    landmarkLayer = L.geoJSON(geojson, {
      style: { color: "#2563eb", weight: 2, fillOpacity: 0.15 },
      onEachFeature: (f, layer) => {
        layer.bindPopup(popupHTML(f));
        layer.on("click", () => onLandmarkClick(f));
      },
    }).addTo(map);

    const b = landmarkLayer.getBounds();
    if (b && b.isValid()) map.fitBounds(b.pad(0.2));

    // 直前の位置で再評価
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