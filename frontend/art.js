// Reading Buddy illustration set: hand-built SVG in one sticker style (navy outline, flat colour).
// Every function returns an SVG string. No external images.
"use strict";

const Art = (() => {
  const O = "#2B2A5E"; // outline ink
  const SKY = "#CDEBFF";

  const svg = (vb, inner, cls = "", label = "") =>
    `<svg class="${cls}" viewBox="${vb}" xmlns="http://www.w3.org/2000/svg" ${label ? `role="img" aria-label="${label}"` : 'aria-hidden="true"'}>${inner}</svg>`;

  const starPath = (cx, cy, r, inner = 0.48, rot = -90) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const rr = i % 2 ? r * inner : r;
      const a = ((rot + i * 36) * Math.PI) / 180;
      pts.push(`${(cx + rr * Math.cos(a)).toFixed(1)} ${(cy + rr * Math.sin(a)).toFixed(1)}`);
    }
    return `M${pts.join(" L")} Z`;
  };
  const star = (cx, cy, r, fill = "#FFC93C", stroke = O, sw = 2.5) =>
    `<path d="${starPath(cx, cy, r)}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;

  const cloud = (x, y, s = 1, fill = "#fff", op = 1) =>
    `<path transform="translate(${x} ${y}) scale(${s})" opacity="${op}" fill="${fill}" d="M12 34 C0 34 0 16 14 16 C16 4 34 0 40 12 C46 2 66 6 64 22 C76 22 76 34 66 34 Z"/>`;

  const sun = (cx, cy, r, face = true) => {
    let rays = "";
    for (let i = 0; i < 12; i++) {
      const a = i * 30;
      rays += `<rect x="${cx - r * 0.09}" y="${cy - r * 1.55}" width="${r * 0.18}" height="${r * 0.42}" rx="${r * 0.09}" fill="#FFB627" transform="rotate(${a} ${cx} ${cy})"/>`;
    }
    const f = face
      ? `<ellipse cx="${cx - r * 0.33}" cy="${cy - r * 0.08}" rx="${r * 0.09}" ry="${r * 0.13}" fill="${O}"/>
         <ellipse cx="${cx + r * 0.33}" cy="${cy - r * 0.08}" rx="${r * 0.09}" ry="${r * 0.13}" fill="${O}"/>
         <circle cx="${cx - r * 0.55}" cy="${cy + r * 0.22}" r="${r * 0.14}" fill="#FF8FA3" opacity=".8"/>
         <circle cx="${cx + r * 0.55}" cy="${cy + r * 0.22}" r="${r * 0.14}" fill="#FF8FA3" opacity=".8"/>
         <path d="M${cx - r * 0.28} ${cy + r * 0.2} Q${cx} ${cy + r * 0.52} ${cx + r * 0.28} ${cy + r * 0.2}" fill="none" stroke="${O}" stroke-width="${Math.max(2, r * 0.08)}" stroke-linecap="round"/>`
      : "";
    return `<g><g class="art-sun">${rays}</g><circle cx="${cx}" cy="${cy}" r="${r}" fill="#FFD84D" stroke="${O}" stroke-width="${Math.max(2, r * 0.07)}"/>${f}</g>`;
  };

  const ground = (a = "#8FDB6E", b = "#6CCB5A", w = 240, h = 150) =>
    `<path d="M0 ${h - 32} C${w * 0.25} ${h - 46} ${w * 0.5} ${h - 22} ${w} ${h - 40} L${w} ${h} L0 ${h} Z" fill="${a}"/>
     <path d="M0 ${h - 18} C${w * 0.3} ${h - 30} ${w * 0.62} ${h - 10} ${w} ${h - 24} L${w} ${h} L0 ${h} Z" fill="${b}"/>`;

  const flower = (x, y, c = "#FF5C7A", s = 1) =>
    `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 0 V16" stroke="#3E9E4F" stroke-width="2.5" stroke-linecap="round"/>
     ${[0, 72, 144, 216, 288].map((a) => `<circle cx="${(6 * Math.cos((a * Math.PI) / 180)).toFixed(1)}" cy="${(6 * Math.sin((a * Math.PI) / 180)).toFixed(1)}" r="4.5" fill="${c}"/>`).join("")}
     <circle r="3.5" fill="#FFD84D"/></g>`;

  // ---------------------------------------------------------------- Owl mascot ("Buddy")
  const owl = (cls = "") =>
    svg("0 0 200 210", `
      <ellipse cx="100" cy="203" rx="56" ry="6" fill="#000" opacity=".1"/>
      <g class="owl-bob">
        <path d="M48 56 L38 16 L78 42 Z M152 56 L162 16 L122 42 Z" fill="#8C5534" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
        <g class="owl-wing owl-wing-l"><path d="M36 104 C8 122 12 164 42 180 C52 162 56 132 48 108 Z" fill="#8C5534" stroke="${O}" stroke-width="3" stroke-linejoin="round"/></g>
        <g class="owl-wing owl-wing-r"><path d="M164 104 C192 122 188 164 158 180 C148 162 144 132 152 108 Z" fill="#8C5534" stroke="${O}" stroke-width="3" stroke-linejoin="round"/></g>
        <path d="M100 30 C150 30 172 70 170 120 C168 168 140 196 100 196 C60 196 32 168 30 120 C28 70 50 30 100 30 Z" fill="#A86B43" stroke="${O}" stroke-width="3"/>
        <path d="M100 108 C134 108 146 142 142 166 C138 188 118 194 100 194 C82 194 62 188 58 166 C54 142 66 108 100 108 Z" fill="#F7E4C4"/>
        <path d="M76 134 q6 7 12 0 M94 134 q6 7 12 0 M112 134 q6 7 12 0 M84 152 q6 7 12 0 M102 152 q6 7 12 0 M92 170 q6 7 12 0" fill="none" stroke="#D9B48A" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="72" cy="86" r="33" fill="#F7E4C4"/><circle cx="128" cy="86" r="33" fill="#F7E4C4"/>
        <path d="M56 60 Q74 46 92 58 M108 58 Q126 46 144 60" fill="none" stroke="#8C5534" stroke-width="6" stroke-linecap="round"/>
        <g class="owl-eyes">
          <circle cx="74" cy="88" r="20" fill="#fff" stroke="${O}" stroke-width="3"/>
          <circle cx="126" cy="88" r="20" fill="#fff" stroke="${O}" stroke-width="3"/>
          <g class="owl-pupils">
            <circle cx="77" cy="90" r="10.5" fill="${O}"/><circle cx="123" cy="90" r="10.5" fill="${O}"/>
            <circle cx="81" cy="85" r="4" fill="#fff"/><circle cx="127" cy="85" r="4" fill="#fff"/>
            <circle cx="74" cy="94" r="1.8" fill="#fff"/><circle cx="120" cy="94" r="1.8" fill="#fff"/>
          </g>
          <g class="owl-lids"><circle cx="74" cy="88" r="20" fill="#A86B43" stroke="${O}" stroke-width="3"/><circle cx="126" cy="88" r="20" fill="#A86B43" stroke="${O}" stroke-width="3"/></g>
        </g>
        <g class="owl-happy"><path d="M58 92 Q74 72 90 92 M110 92 Q126 72 142 92" fill="none" stroke="${O}" stroke-width="5" stroke-linecap="round"/></g>
        <ellipse cx="54" cy="112" rx="9" ry="5.5" fill="#FF8FA3" opacity=".75"/><ellipse cx="146" cy="112" rx="9" ry="5.5" fill="#FF8FA3" opacity=".75"/>
        <g class="owl-beak"><path d="M91 104 L109 104 L100 120 Z" fill="#FF9F2E" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/></g>
        <g fill="#FF9F2E" stroke="${O}" stroke-width="2.2"><circle cx="72" cy="196" r="6"/><circle cx="84" cy="197" r="6"/><circle cx="116" cy="197" r="6"/><circle cx="128" cy="196" r="6"/></g>
      </g>`, `owl ${cls}`, "Buddy the owl");

  // ---------------------------------------------------------------- Children
  const limb = (x1, y1, x2, y2, fill) =>
    `<path d="M${x1} ${y1} L${x2} ${y2}" stroke="${O}" stroke-width="23" stroke-linecap="round"/>
     <path d="M${x1} ${y1} L${x2} ${y2}" stroke="${fill}" stroke-width="16" stroke-linecap="round"/>`;

  const kid = ({ hair = "girl", shirt = "#FF8A3D", skin = "#F3C29B", hairColor = "#3A2316", pose = "read", book = "#8E6CFF", bow = "#FF5C9A", cls = "" } = {}) => {
    const backHair = hair === "girl"
      ? `<path d="M48 96 C38 46 70 26 100 26 C130 26 162 46 152 96 C158 122 160 142 152 164 L122 152 L78 152 L48 164 C40 142 42 120 48 96 Z" fill="${hairColor}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>`
      : "";
    const armsBehind = pose === "cheer"
      ? limb(64, 160, 30, 92, skin) + limb(136, 160, 170, 92, skin) +
        `<circle cx="28" cy="88" r="12" fill="${skin}" stroke="${O}" stroke-width="3"/><circle cx="172" cy="88" r="12" fill="${skin}" stroke="${O}" stroke-width="3"/>`
      : pose === "wave"
        ? limb(136, 160, 172, 100, skin) + `<circle cx="174" cy="95" r="12" fill="${skin}" stroke="${O}" stroke-width="3"/>`
        : "";
    const sleeves = pose === "cheer"
      ? `<path d="M50 168 L60 146 L78 156 Z M150 168 L140 146 L122 156 Z" fill="${shirt}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>`
      : "";
    const frontHair = hair === "girl"
      ? `<path d="M55 86 C55 50 78 36 100 36 C124 36 146 50 145 86 C136 70 120 60 104 62 C96 72 76 78 55 86 Z" fill="${hairColor}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
         <g transform="translate(138 48) rotate(20)"><path d="M0 0 L-14 -9 L-14 9 Z M0 0 L14 -9 L14 9 Z" fill="${bow}" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/><circle r="4.5" fill="${bow}" stroke="${O}" stroke-width="2.5"/></g>`
      : `<path d="M94 36 C88 22 100 12 114 16 C106 18 104 26 108 34 Z" fill="${hairColor}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
         <path d="M54 92 C46 52 70 30 102 30 C132 30 156 50 147 92 C142 78 134 68 122 64 C116 72 104 76 92 70 C82 76 66 82 54 92 Z" fill="${hairColor}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>`;
    const face = `
      <path d="M76 75 q8 -5 14 0 M110 75 q8 -5 14 0" fill="none" stroke="${hairColor}" stroke-width="3" stroke-linecap="round"/>
      <g class="kid-eyes"><ellipse cx="83" cy="91" rx="6.5" ry="8.5" fill="${O}"/><ellipse cx="117" cy="91" rx="6.5" ry="8.5" fill="${O}"/>
      <circle cx="85.5" cy="87.5" r="2.4" fill="#fff"/><circle cx="119.5" cy="87.5" r="2.4" fill="#fff"/></g>
      <ellipse cx="69" cy="105" rx="8" ry="5" fill="#FF8FA3" opacity=".8"/><ellipse cx="131" cy="105" rx="8" ry="5" fill="#FF8FA3" opacity=".8"/>
      <path d="M99 97 q2.5 3 0 5" fill="none" stroke="#C98366" stroke-width="2" stroke-linecap="round"/>
      <path d="M87 107 Q100 124 113 107 Q100 112 87 107 Z" fill="#C93D57" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>`;
    const front = pose === "read"
      ? `<path d="M100 182 L50 170 L48 222 L100 232 L152 222 L150 170 Z" fill="${book}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
         <path d="M100 180 L57 170 L56 215 L100 224 Z M100 180 L143 170 L144 215 L100 224 Z" fill="#fff" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
         <path d="M66 184 L92 190 M66 194 L92 200 M66 204 L88 209 M108 190 L134 184 M108 200 L134 194 M112 209 L134 204" stroke="#C9C3F0" stroke-width="2.5" stroke-linecap="round"/>
         <circle cx="52" cy="194" r="11" fill="${skin}" stroke="${O}" stroke-width="3"/><circle cx="148" cy="194" r="11" fill="${skin}" stroke="${O}" stroke-width="3"/>`
      : "";
    return svg("0 0 200 240", `
      ${backHair}${armsBehind}
      <rect x="89" y="122" width="22" height="22" fill="${skin}" stroke="${O}" stroke-width="3"/>
      <path d="M50 170 C54 146 76 138 100 138 C124 138 146 146 150 170 L158 242 L42 242 Z" fill="${shirt}" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
      <path d="M84 140 Q100 158 116 140 Z" fill="#fff" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      ${sleeves}
      <circle cx="55" cy="92" r="9" fill="${skin}" stroke="${O}" stroke-width="3"/><circle cx="145" cy="92" r="9" fill="${skin}" stroke="${O}" stroke-width="3"/>
      <circle cx="100" cy="86" r="46" fill="${skin}" stroke="${O}" stroke-width="3"/>
      ${frontHair}${face}${front}`, `kid ${cls}`);
  };

  // ---------------------------------------------------------------- Story scenes (240 x 150)
  const frame = (bg, inner, label) => svg("0 0 240 150", `<rect width="240" height="150" fill="${bg}"/>${inner}`, "scene", label);

  const scenes = {
    kite: () => frame(SKY, `
      ${sun(38, 36, 16)}${cloud(150, 92, 0.7)}${cloud(70, 60, 0.55, "#fff", 0.9)}
      <path d="M152 84 Q110 104 64 150" fill="none" stroke="${O}" stroke-width="1.6" stroke-dasharray="3 3"/>
      <g class="float-a"><path d="M152 12 L180 46 L152 84 L124 46 Z" fill="#FF5C7A"/>
      <path d="M152 12 L180 46 L152 46 Z M124 46 L152 46 L152 84 Z" fill="#FFC93C"/>
      <path d="M152 12 L180 46 L152 84 L124 46 Z M152 12 V84 M124 46 H180" fill="none" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M152 84 C142 98 162 108 150 124" fill="none" stroke="${O}" stroke-width="2"/>
      <path d="M146 96 l-8 -4 l0 8 z M156 108 l8 -4 l0 8 z" fill="#3D8BFF" stroke="${O}" stroke-width="1.6" stroke-linejoin="round"/></g>
      ${ground()}${flower(30, 122, "#FF5C9A")}${flower(206, 118, "#A98BFF")}`, "A kite in the sky"),

    rain: () => frame("#D9E8F8", `
      <g class="float-b">${cloud(58, 4, 1.65, "#A9BFE0")}
      <path transform="translate(58 4) scale(1.65)" fill="none" stroke="${O}" stroke-width="1.6" d="M12 34 C0 34 0 16 14 16 C16 4 34 0 40 12 C46 2 66 6 64 22 C76 22 76 34 66 34 Z"/>
      <ellipse cx="104" cy="40" rx="2.6" ry="3.4" fill="${O}"/><ellipse cx="126" cy="40" rx="2.6" ry="3.4" fill="${O}"/>
      <path d="M108 48 Q115 53 122 48" fill="none" stroke="${O}" stroke-width="2.2" stroke-linecap="round"/></g>
      <g class="rain-drops" fill="#3D8BFF">${[[70, 74], [96, 86], [122, 72], [148, 88], [174, 74], [84, 104], [160, 102]].map(([x, y]) => `<path d="M${x} ${y} q-5 9 0 11 q5 -2 0 -11 z"/>`).join("")}</g>
      ${ground("#A7E08A", "#7FCF6A")}
      <ellipse cx="178" cy="128" rx="40" ry="8" fill="#8FC8FF" stroke="${O}" stroke-width="2"/>
      <g class="float-a"><path d="M160 122 L196 122 L190 130 L166 130 Z" fill="#fff" stroke="${O}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="M178 102 L178 122 L192 120 Z" fill="#FFC93C" stroke="${O}" stroke-width="2.2" stroke-linejoin="round"/></g>
      <g transform="translate(60 112)"><ellipse cx="0" cy="10" rx="25" ry="15" fill="#5CCB6E" stroke="${O}" stroke-width="2.5"/>
      <circle cx="-10" cy="-6" r="8" fill="#5CCB6E" stroke="${O}" stroke-width="2.5"/><circle cx="10" cy="-6" r="8" fill="#5CCB6E" stroke="${O}" stroke-width="2.5"/>
      <circle cx="-10" cy="-6" r="4.6" fill="#fff"/><circle cx="10" cy="-6" r="4.6" fill="#fff"/><circle cx="-9" cy="-5" r="2.4" fill="${O}"/><circle cx="11" cy="-5" r="2.4" fill="${O}"/>
      <path d="M-11 8 Q0 16 11 8" fill="none" stroke="${O}" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="-16" cy="6" r="3" fill="#FF8FA3" opacity=".8"/><circle cx="16" cy="6" r="3" fill="#FF8FA3" opacity=".8"/></g>`, "Rain, a frog and a paper boat"),

    mango: () => frame("#FFF1C9", `
      ${sun(206, 30, 14)}
      <path d="M112 146 L118 92 L128 92 L134 146 Z" fill="#9A5B34" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M122 16 C152 6 190 28 186 56 C200 80 176 102 150 96 C136 110 104 110 92 96 C62 102 46 76 60 56 C54 32 88 10 122 16 Z" fill="#4CBF6B" stroke="${O}" stroke-width="2.5"/>
      <path d="M90 40 q10 -8 20 0 M136 32 q10 -8 20 0 M150 66 q10 -8 20 0" fill="none" stroke="#2F9A4E" stroke-width="2.5" stroke-linecap="round"/>
      ${[[96, 64], [122, 50], [150, 78], [112, 84], [168, 52]].map(([x, y]) => `<g class="mango"><ellipse cx="${x}" cy="${y}" rx="7" ry="9" fill="#FFB627" stroke="${O}" stroke-width="2"/><path d="M${x} ${y - 9} q5 -5 9 -2" fill="#4CBF6B" stroke="${O}" stroke-width="1.5"/></g>`).join("")}
      ${ground("#B6E388", "#93D46E")}
      <path d="M46 118 L82 118 L78 140 L50 140 Z" fill="#D9934E" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <circle cx="56" cy="114" r="7" fill="#FFB627" stroke="${O}" stroke-width="2"/><circle cx="70" cy="113" r="7" fill="#FF9F2E" stroke="${O}" stroke-width="2"/>
      <path d="M46 126 H82 M48 133 H80" stroke="#B5743A" stroke-width="2"/>`, "A mango tree full of mangoes"),

    ant: () => frame("#E8F6D9", `
      ${sun(32, 28, 13)}${cloud(150, 16, 0.6)}${ground("#C9E99A", "#A8DB7C")}
      <g class="float-b"><ellipse cx="126" cy="70" rx="32" ry="15" fill="#fff" stroke="${O}" stroke-width="2.5" transform="rotate(-12 126 70)"/>
      <path d="M108 70 q8 -6 18 -4" fill="none" stroke="#E6E1D3" stroke-width="3" stroke-linecap="round"/></g>
      <g fill="none" stroke="${O}" stroke-width="2.5" stroke-linecap="round">
        <path d="M96 108 l-8 16 M110 110 l-2 16 M124 108 l8 16 M140 106 l10 14 M150 104 l14 10 M88 104 l-14 12"/></g>
      <ellipse cx="142" cy="100" rx="18" ry="13" fill="#9A4F2D" stroke="${O}" stroke-width="2.5"/>
      <ellipse cx="116" cy="102" rx="11" ry="9" fill="#9A4F2D" stroke="${O}" stroke-width="2.5"/>
      <circle cx="92" cy="92" r="16" fill="#9A4F2D" stroke="${O}" stroke-width="2.5"/>
      <path d="M86 78 Q78 60 68 62 M98 77 Q102 58 112 58" fill="none" stroke="${O}" stroke-width="2.2" stroke-linecap="round"/>
      <circle cx="68" cy="62" r="3.2" fill="#FF5C7A" stroke="${O}" stroke-width="1.5"/><circle cx="112" cy="58" r="3.2" fill="#FF5C7A" stroke="${O}" stroke-width="1.5"/>
      <circle cx="86" cy="90" r="5" fill="#fff"/><circle cx="99" cy="90" r="5" fill="#fff"/><circle cx="87" cy="91" r="2.6" fill="${O}"/><circle cx="100" cy="91" r="2.6" fill="${O}"/>
      <path d="M86 99 Q92 104 98 99" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
      <ellipse cx="40" cy="128" rx="10" ry="5" fill="#B8B29F" stroke="${O}" stroke-width="2"/><ellipse cx="200" cy="132" rx="8" ry="4" fill="#B8B29F" stroke="${O}" stroke-width="2"/>`, "An ant carrying a grain of rice"),

    doll: () => frame("#FFE0EC", `
      <g class="float-a" fill="#A98BFF" stroke="${O}" stroke-width="1.8">
        <path d="M44 40 v-18 l14 -4 v18"/><circle cx="41" cy="40" r="5"/><circle cx="55" cy="36" r="5"/>
        <path d="M192 54 v-20 l10 4"/><circle cx="189" cy="55" r="5.5"/></g>
      ${ground("#FFC2D9", "#FFAACB")}
      <path d="M120 70 L84 134 L156 134 Z" fill="#FF4F6E" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M90 124 H150" stroke="#FFC93C" stroke-width="4" stroke-dasharray="2 5" stroke-linecap="round"/>
      <path d="M100 82 L84 108 M140 82 L156 108" stroke="${O}" stroke-width="12" stroke-linecap="round"/><path d="M100 82 L84 108 M140 82 L156 108" stroke="#F3C29B" stroke-width="7" stroke-linecap="round"/>
      <circle cx="120" cy="54" r="22" fill="#F3C29B" stroke="${O}" stroke-width="2.5"/>
      <path d="M98 54 C96 24 144 24 142 54 C136 42 124 38 120 40 C114 38 104 42 98 54 Z" fill="#2B1A12" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M94 60 C90 22 150 22 146 60 L156 96 C148 80 144 70 140 64 C142 40 98 40 100 64 C96 70 92 80 84 96 Z" fill="#E8344F" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <circle cx="112" cy="56" r="2.8" fill="${O}"/><circle cx="128" cy="56" r="2.8" fill="${O}"/>
      <circle cx="107" cy="63" r="3.5" fill="#FF8FA3" opacity=".8"/><circle cx="133" cy="63" r="3.5" fill="#FF8FA3" opacity=".8"/>
      <path d="M114 64 Q120 70 126 64" fill="none" stroke="${O}" stroke-width="2" stroke-linecap="round"/>
      ${star(30, 96, 7, "#FFC93C", O, 1.8)}${star(206, 100, 6, "#FFC93C", O, 1.8)}`, "A doll in a red veil, singing"),

    nest: () => frame("#DDF3FF", `
      ${cloud(160, 14, 0.7)}${sun(34, 30, 12)}
      <path d="M0 88 C50 84 110 92 240 78" stroke="#8A5232" stroke-width="10" stroke-linecap="round" fill="none"/>
      <path d="M0 88 C50 84 110 92 240 78" stroke="${O}" stroke-width="2" fill="none" opacity=".35"/>
      ${[[40, 76, -30], [186, 68, 30], [210, 88, 160]].map(([x, y, r]) => `<path transform="translate(${x} ${y}) rotate(${r})" d="M0 0 C6 -14 22 -14 26 0 C22 10 6 10 0 0 Z" fill="#5BC46F" stroke="${O}" stroke-width="2"/>`).join("")}
      <ellipse cx="100" cy="66" rx="10" ry="12" fill="#BFE3FF" stroke="${O}" stroke-width="2"/><ellipse cx="116" cy="64" rx="10" ry="12" fill="#D6EDFF" stroke="${O}" stroke-width="2"/><ellipse cx="132" cy="67" rx="10" ry="12" fill="#BFE3FF" stroke="${O}" stroke-width="2"/>
      <path d="M80 70 C82 96 150 98 152 70 Z" fill="#B97A47" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M86 76 L146 80 M88 84 L142 74 M96 90 L138 86" stroke="#8A5232" stroke-width="2" stroke-linecap="round"/>
      <g class="float-b" transform="translate(178 42)"><ellipse cx="0" cy="0" rx="17" ry="14" fill="#C98B5A" stroke="${O}" stroke-width="2.5"/>
      <ellipse cx="-2" cy="5" rx="10" ry="7" fill="#F2D3AE"/>
      <path d="M6 -2 C16 -2 22 8 12 12 C8 10 4 6 6 -2 Z" fill="#8A5232" stroke="${O}" stroke-width="2"/>
      <path d="M-16 -4 L-26 -1 L-16 3 Z" fill="#FF9F2E" stroke="${O}" stroke-width="1.8" stroke-linejoin="round"/>
      <circle cx="-8" cy="-5" r="2.6" fill="${O}"/><path d="M14 4 L26 0 L24 8 Z" fill="#8A5232" stroke="${O}" stroke-width="1.8" stroke-linejoin="round"/></g>
      ${ground("#A8E08B", "#86D06E")}
      <g fill="#FFC93C" stroke="${O}" stroke-width="1.2">${[[60, 132], [70, 136], [80, 131], [150, 134], [162, 130]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="3" ry="2"/>`).join("")}</g>`, "A sparrow, a nest and three eggs"),

    garden: () => frame("#E3F7E8", `
      ${sun(200, 30, 14)}${cloud(40, 14, 0.6)}${ground("#9EDC7A", "#7BCB61")}
      ${[[34, "#FF5C7A"], [62, "#FFC93C"], [90, "#FF5C7A"], [196, "#FFC93C"], [222, "#FF5C7A"]].map(([x, c], i) => `<g class="${i % 2 ? "sway-a" : "sway-b"}">${flower(x, 96 + (i % 2) * 6, c, 1.8)}</g>`).join("")}
      <g class="float-b" transform="translate(138 74)"><path d="M0 0 L30 0 L26 34 L4 34 Z" fill="#3D8BFF" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M30 6 C42 6 42 26 28 26" fill="none" stroke="${O}" stroke-width="3"/>
      <path d="M2 8 L-22 -10" stroke="${O}" stroke-width="7" stroke-linecap="round"/><path d="M2 8 L-22 -10" stroke="#3D8BFF" stroke-width="3.5" stroke-linecap="round"/>
      <circle cx="-26" cy="-14" r="5" fill="#3D8BFF" stroke="${O}" stroke-width="2"/>
      <g fill="#7CC4FF"><path d="M-30 -2 q-3 6 0 7 q3 -1 0 -7 z"/><path d="M-38 6 q-3 6 0 7 q3 -1 0 -7 z"/><path d="M-26 12 q-3 6 0 7 q3 -1 0 -7 z"/></g></g>`, "Red and yellow flowers and a watering can"),

    school: () => frame("#DCEBFF", `
      ${sun(32, 30, 13)}${cloud(170, 12, 0.7)}${ground()}
      <path d="M60 64 L120 30 L180 64 Z" fill="#FF5C5C" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <rect x="66" y="62" width="108" height="64" fill="#FFB36B" stroke="${O}" stroke-width="2.5"/>
      <circle cx="120" cy="50" r="8" fill="#fff" stroke="${O}" stroke-width="2"/><path d="M120 45 V50 H124" stroke="${O}" stroke-width="1.8" fill="none" stroke-linecap="round"/>
      <path d="M120 30 V12" stroke="${O}" stroke-width="2.2"/><path class="flag" d="M120 12 L140 17 L120 22 Z" fill="#3CCB9A" stroke="${O}" stroke-width="2" stroke-linejoin="round"/>
      ${[76, 98, 132, 154].map((x) => `<rect x="${x}" y="72" width="14" height="14" rx="2" fill="#BFE3FF" stroke="${O}" stroke-width="2"/>`).join("")}
      ${[76, 154].map((x) => `<rect x="${x}" y="96" width="14" height="14" rx="2" fill="#BFE3FF" stroke="${O}" stroke-width="2"/>`).join("")}
      <path d="M108 126 V102 Q120 92 132 102 V126 Z" fill="#7B5CFF" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <circle cx="30" cy="104" r="14" fill="#4CBF6B" stroke="${O}" stroke-width="2.2"/><rect x="28" y="116" width="4" height="10" fill="#8A5232"/>
      <circle cx="212" cy="102" r="16" fill="#4CBF6B" stroke="${O}" stroke-width="2.2"/><rect x="210" y="116" width="4" height="10" fill="#8A5232"/>`, "A school with a flag"),

    book: () => frame("#EFE6FF", `${sun(40, 32, 13)}${ground("#C9B8FF", "#B29CFF")}
      <path d="M120 50 L70 40 L68 112 L120 122 L172 112 L170 40 Z" fill="#8E6CFF" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M120 48 L76 38 L75 104 L120 114 Z M120 48 L164 38 L165 104 L120 114 Z" fill="#fff" stroke="${O}" stroke-width="2.5" stroke-linejoin="round"/>
      ${star(190, 40, 9)}${star(56, 100, 7, "#FF8FA3")}`, "An open book"),
  };

  // ---------------------------------------------------------------- Language card headers (260 x 150)
  const langArt = {
    "gu-IN": () => svg("0 0 260 150", `<rect width="260" height="150" fill="#FFE1BF"/>
      ${sun(214, 34, 15)}
      <path d="M20 150 V92 H34 V74 L46 52 L58 74 V92 H72 V150 Z" fill="#FFC48A"/>
      <path d="M190 150 V100 H200 V84 L212 64 L224 84 V100 H234 V150 Z" fill="#FFC48A"/>
      <g class="float-a"><path d="M60 14 L76 32 L60 52 L44 32 Z" fill="#FF5C7A" stroke="${O}" stroke-width="2"/><path d="M60 14 L76 32 L60 32 Z M44 32 L60 32 L60 52 Z" fill="#FFC93C"/><path d="M60 14 L76 32 L60 52 L44 32 Z M60 14 V52 M44 32 H76" fill="none" stroke="${O}" stroke-width="2"/>
      <path d="M60 52 C54 60 66 66 58 74" fill="none" stroke="${O}" stroke-width="1.6"/></g>
      <g transform="translate(56 16) scale(.74)">${kidInner({ hair: "boy", shirt: "#FF7A3D", book: "#8E6CFF" })}</g>`, "lang-art"),
    "en-IN": () => svg("0 0 260 150", `<rect width="260" height="150" fill="#D5E7FF"/>
      ${cloud(20, 18, 0.7)}${cloud(196, 30, 0.5)}
      <path d="M200 150 V64 H206 V44 L216 26 L226 44 V64 H232 V150 Z" fill="#AFCBFF"/><circle cx="216" cy="78" r="7" fill="#D5E7FF"/>
      <path d="M22 150 V96 H60 V150 Z M30 96 V84 H52 V96" fill="#AFCBFF"/>
      <g class="float-b">${["#FF5C7A", "#FFC93C", "#3CCB9A"].map((c, i) => `<g transform="translate(${18 + i * 26} ${118 - (i === 1 ? 24 : 0)})"><rect width="24" height="24" rx="4" fill="${c}" stroke="${O}" stroke-width="2"/><text x="12" y="18" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="16" fill="#fff" stroke="${O}" stroke-width=".8">${"ABC"[i]}</text></g>`).join("")}</g>
      <g transform="translate(56 16) scale(.74)">${kidInner({ hair: "girl", shirt: "#3D8BFF", book: "#FFC93C", bow: "#FF5C9A" })}</g>`, "lang-art"),
    "hi-IN": () => svg("0 0 260 150", `<rect width="260" height="150" fill="#FFDCEB"/>
      ${sun(40, 32, 13)}
      <path d="M176 150 V62 H244 V150 H226 V96 Q210 78 194 96 V150 Z M170 62 H250 V52 H170 Z M184 52 V44 H236 V52 Z" fill="#FFB3D0"/>
      <g class="float-a" transform="translate(30 104)"><path d="M0 14 C-14 6 -10 -8 0 -12 C10 -8 14 6 0 14 Z" fill="#FF5C9A" stroke="${O}" stroke-width="2"/>
      <path d="M0 14 C-18 12 -22 0 -16 -4 C-8 0 -4 8 0 14 Z M0 14 C18 12 22 0 16 -4 C8 0 4 8 0 14 Z" fill="#FF8FBF" stroke="${O}" stroke-width="2"/></g>
      <g transform="translate(56 16) scale(.74)">${kidInner({ hair: "boy", shirt: "#E8344F", skin: "#E8B48C", book: "#3CCB9A" })}</g>`, "lang-art"),
  };

  // kid() without the outer <svg>, for composing into bigger pictures
  function kidInner(opts) {
    return kid(opts).replace(/^<svg[^>]*>/, "").replace(/<\/svg>$/, "");
  }
  function owlInner() {
    return owl().replace(/^<svg[^>]*>/, "").replace(/<\/svg>$/, "");
  }

  // ---------------------------------------------------------------- Hero
  const hero = () => svg("0 0 560 440", `
    <defs><clipPath id="heroClip"><rect width="560" height="440" rx="40"/></clipPath></defs>
    <g clip-path="url(#heroClip)">
    <rect width="560" height="440" fill="#C9ECFF"/>
    <circle cx="420" cy="90" r="150" fill="#E3F6FF"/>
    ${cloud(30, 46, 1.2)}${cloud(220, 18, 0.85, "#fff", 0.9)}${cloud(330, 150, 0.6, "#fff", 0.8)}
    <g class="hero-sun">${sun(420, 82, 44)}</g>
    <path d="M0 330 C140 290 320 330 560 290 L560 440 L0 440 Z" fill="#8FDB6E"/>
    <path d="M0 380 C170 350 380 390 560 356 L560 440 L0 440 Z" fill="#6CCB5A"/>
    <circle cx="36" cy="330" r="34" fill="#5BC46F"/><circle cx="70" cy="344" r="26" fill="#4AB35F"/>
    <g class="signpost">
      <rect x="492" y="176" width="16" height="200" rx="4" fill="#9A5B34" stroke="${O}" stroke-width="3"/>
      ${[["Read", 196, -3], ["Learn", 242, 2], ["Grow", 288, -2]].map(([t, y, r]) => `<g transform="rotate(${r} 500 ${y + 17})"><path d="M446 ${y} H540 L552 ${y + 17} L540 ${y + 34} H446 Z" fill="#D9934E" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
        <text x="496" y="${y + 25}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="21" fill="#fff" stroke="${O}" stroke-width=".9">${t}</text></g>`).join("")}
      <g class="hop" transform="translate(500 156)"><ellipse cx="0" cy="0" rx="16" ry="13" fill="#3D8BFF" stroke="${O}" stroke-width="2.5"/>
      <path d="M-4 2 C4 -2 12 2 10 10 C2 10 -4 8 -4 2 Z" fill="#2B6FD6" stroke="${O}" stroke-width="2"/>
      <path d="M14 -4 L24 -1 L14 3 Z" fill="#FF9F2E" stroke="${O}" stroke-width="2" stroke-linejoin="round"/><circle cx="7" cy="-5" r="2.4" fill="${O}"/>
      <path d="M-4 13 v6 M4 13 v6" stroke="${O}" stroke-width="2" stroke-linecap="round"/></g>
    </g>
    <g transform="translate(300 330)"><rect x="-6" y="42" width="140" height="26" rx="7" fill="#3D8BFF" stroke="${O}" stroke-width="3"/>
      <rect x="6" y="18" width="122" height="26" rx="7" fill="#FF7A59" stroke="${O}" stroke-width="3"/>
      <rect x="18" y="-4" width="100" height="24" rx="7" fill="#2FC48F" stroke="${O}" stroke-width="3"/>
      <path d="M28 8 H106 M16 31 H118 M4 55 H124" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".7"/></g>
    <g class="hero-owl owl" transform="translate(296 186) scale(.74)">${owlInner()}</g>
    <g class="hero-kid" transform="translate(40 150) scale(1.22)">${kidInner({ hair: "girl", shirt: "#FF8A3D", book: "#8E6CFF" })}</g>
    ${flower(300, 420, "#FF5C9A", 1.6)}${flower(470, 410, "#FFC93C", 1.4)}${flower(540, 424, "#A98BFF", 1.3)}
    ${star(250, 120, 10)}${star(70, 120, 8, "#FF8FA3")}${star(290, 250, 7, "#A98BFF")}
    </g>`, "hero-art", "A girl reading a book with Buddy the owl");

  return { owl, kid, scenes, langArt, hero, sun, star, starPath, cloud };
})();
