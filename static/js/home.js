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

// 投稿ページのベースURL（/post になる想定。テンプレから受け取る）
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

  // 「この場所に投稿する」リンク
  const postLink = document.getElementById("postLink");
  if (postLink) {
    postLink.href = `${postBase}?landmark_id=${encodeURIComponent(feature.id)}`;
    postLink.style.display = "inline-block";
  }

  // 「この場所の投稿を見る」リンク初期設定（無効化）
  const readLink = document.getElementById("readLink");
  if (readLink) {
    readLink.dataset.href = `/others/others_post/${feature.id}`;
    readLink.href = "#";
    readLink.style.pointerEvents = "none";
    readLink.style.opacity = "0.5";
    readLink.style.display = "inline-block";
  }

  // ★ ユーザーがそのランドマーク内にいる場合のみ投稿可能にする
  if (lastUserPos) {
    const { lat, lon, acc } = lastUserPos;
    const inside = checkInsideAny(lon, lat, acc).some(f => f.id === feature.id);

    if (!inside && postLink) {
      // ランドマーク外 → 投稿ボタンを隠す
      postLink.style.display = "none";
    }

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

    // Tailwind で表示制御
    linkEl.classList.remove("hidden");
    msgEl.classList.add("hidden");

    if (readLink) {
      readLink.style.pointerEvents = "auto";
      readLink.style.opacity = "1";
      readLink.href = readLink.dataset.href ?? "#";
    }
  } else {
    // ランドマーク外なら投稿ボタンを隠す
    linkEl.classList.add("hidden");
    msgEl.classList.remove("hidden");

    if (readLink) {
      readLink.style.pointerEvents = "none";
      readLink.style.opacity = "0.5";
      readLink.href = "#";
    }
  }
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

// ====== ランドマーク内判定 ======
function checkInsideAny(lon, lat, accuracyMeters = 30) {
  if (!landmarksGeoJSON || !landmarksGeoJSON.features) return [];
  const pt = turf.point([lon, lat]);
  const bufferKm = Math.max(accuracyMeters, 30) / 1000; // 30mは最低緩衝

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
// ====== ランドマーク読み込み ======
async function loadLandmarks() {
  try {
    const res = await fetch("/api/landmarks", { credentials: "same-origin" });
    if (!res.ok) {
      const text = await res.text();
      console.error("landmarks HTTP error:", res.status, text.slice(0, 300));
      return;
    }

    // JSON 解析。失敗時は内容をログ
    let geojson;
    try {
      geojson = await res.json();
    } catch (e) {
      const bad = await res.clone().text().catch(() => "");
      console.error("landmarks JSON parse failed. head:", bad.slice(0, 300));
      return;
    }

    // 形チェック
    if (!geojson || geojson.type !== "FeatureCollection" || !Array.isArray(geojson.features)) {
      console.error("Invalid /api/landmarks payload:", geojson);
      return;
    }

    // --- ここが重要：geometry が文字列なら JSON.parse して正規化 ---
    const normalized = {
      ...geojson,
      features: geojson.features
        .map(f => {
          const g = (typeof f.geometry === "string") ? safeParseJSON(f.geometry) : f.geometry;
          if (!g || !g.type || !g.coordinates) return null; // 壊れた Feature は捨てる
          return { ...f, geometry: g };
        })
        .filter(Boolean)
    };

    // 0件でも地図を初期化だけはする
    if (landmarkLayer) map.removeLayer(landmarkLayer);
    landmarkLayer = L.geoJSON(normalized, {
      style: { color: "#2563eb", weight: 2, fillOpacity: 0.15 },
      onEachFeature: (f, layer) => {
        layer.bindPopup(popupHTML(f));
        layer.on("click", () => onLandmarkClick(f));
      },
    }).addTo(map);

    const b = landmarkLayer.getBounds();
    if (b && b.isValid()) map.fitBounds(b.pad(0.2));

    // 直前の位置情報があれば CTA 再評価
    if (lastUserPos) {
      const { lat, lon, acc } = lastUserPos;
      setCTA(checkInsideAny(lon, lat, acc));
    }
  } catch (e) {
    console.error("Failed to load landmarks:", e);
  }
}

function safeParseJSON(s) {
  try { return JSON.parse(s); } catch { return null; }
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