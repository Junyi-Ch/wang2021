/* ---------- Initialize jsPsych ---------- */
const jsPsych = initJsPsych({
  on_finish: () => jsPsych.data.displayData()
});

// Create subject ID and filename
const subject_id = jsPsych.randomization.randomID(10);
const filename = `${subject_id}.csv`;


/* ---------- Word list (Chinese + English) ---------- */
const bilingual_words = [
  { zh: "蚂蚁", en: "ant" }, { zh: "脚踝", en: "ankle" },
  { zh: "愤怒", en: "anger" }, { zh: "协议", en: "agreement" },
  { zh: "猫", en: "cat" }, { zh: "胳膊", en: "arm" }, 
  { zh: "大象", en: "elephant" }, { zh: "耳朵", en: "ear" }, { zh: "床", en: "bed" },
  { zh: "冷漠", en: "apathy" }, { zh: "性质", en: "characteristic" },
  { zh: "眼睛", en: "eye" }, { zh: "扫帚", en: "broom" },
  { zh: "慈善", en: "charity" }, { zh: "概念", en: "concept" },
  { zh: "熊猫", en: "panda" }, { zh: "手指", en: "finger" }, { zh: "柜子", en: "cabinet" },

  { zh: "膝盖", en: "knee" }, { zh: "椅子", en: "chair" },
  { zh: "死亡", en: "death" }, { zh: "数据", en: "data" },
  { zh: "嘴唇", en: "lips" }, { zh: "筷子", en: "chopsticks" },
  { zh: "债务", en: "debt" },
  { zh: "麻雀", en: "sparrow" }, { zh: "鼠标", en: "computer mouse" },
  { zh: "沮丧", en: "depressed" },
  { zh: "老虎", en: "tiger" }, { zh: "锤子", en: "hammer" },
  { zh: "身份", en: "identity" },
  { zh: "乌龟", en: "tortoise" }, { zh: "钥匙", en: "key" },
  { zh: "方法", en: "method" },
  { zh: "错误", en: "error" }, { zh: "义务", en: "obligation" },
  { zh: "铅笔", en: "pencil" }, { zh: "兴奋", en: "excited" }, { zh: "现象", en: "phenomenon" },
  { zh: "冰箱", en: "refrigerator" }, { zh: "缘分", en: "fate" }, { zh: "原因", en: "reason" },
  { zh: "恐惧", en: "fear" }, { zh: "关系", en: "relationship" },
  { zh: "骗局", en: "fraud" },
  { zh: "桌子", en: "table" }, { zh: "社会", en: "society" },
  { zh: "电视", en: "television" }, { zh: "快乐", en: "happy" }, { zh: "地位", en: "status" },
  { zh: "牙刷", en: "toothbrush" }, { zh: "天堂", en: "heaven" }, { zh: "制度", en: "system" },
  { zh: "洗衣机", en: "washing machine" }, { zh: "敌意", en: "hostility" }, { zh: "团队", en: "team" },
  { zh: "爱心", en: "loving heart" }, { zh: "婚姻", en: "marriage" }, { zh: "奇迹", en: "miracle" }, { zh: "骄傲", en: "proud" },
  { zh: "光彩", en: "splendor" },
  { zh: "创伤", en: "trauma" }, { zh: "暴力", en: "violence" }
];

/* ---------- Helper functions ---------- */
function getWordsByLanguage(lang) {
  return bilingual_words.map(w => w[lang]);
}

function generateWordCircleHTML(words) {
  const dropZoneSize = 600;        // circle size
  const radius = 380;              // distance from center to words (just outside the 300px radius circle)
  const centerX = dropZoneSize / 2;
  const centerY = dropZoneSize / 2;

  // Wrap in container for centering
  // include minimal CSS for the drop zone and words so we can change the drop-zone style
  let html = `
  <style>
    #word-container { display:flex; justify-content:center; margin:20px 0; }
    #drop-zone { position: relative; width:${dropZoneSize}px; height:${dropZoneSize}px; border-radius:50%; border:5px solid #444; box-sizing:border-box; }
    /* active state when a draggable is over the circle */
    #drop-zone.drop-zone-active { border-color: #0a0; box-shadow: 0 0 0 10px rgba(0,150,0,0.15); }
    .word { position: absolute; transform: translate(-50%, -50%); cursor: grab; padding:6px 10px; background:#f2f2f2; border-radius:6px; user-select:none; }
    .word.dragging { opacity:0.6; }
  </style>
  <div id="word-container"><div id="drop-zone">`;

  words.forEach((word, i) => {
    const angle = (2 * Math.PI * i) / words.length;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);

    html += `<div class="word" draggable="true" style="left:${x}px; top:${y}px;">${word}</div>`;
  });

  // add a control area (we'll position it with CSS so it doesn't overlap the circle)
  html += '</div>' +
          '<div id="controls">' +
            '<button id="finish-btn" disabled>Finished arranging</button>' +
          '</div></div>';
  return html;
}

/* ---------- Trial: Choose Language ---------- */
const lang_choice = {
  type: jsPsychHtmlButtonResponse,
  stimulus: "<p style='font-size:20px;'>Choose your language:</p>",
  choices: ["中文", "English"],
  on_finish: data => {
    const lang = data.response === 0 ? "zh" : "en";
    jsPsych.data.addProperties({ language: lang });
    // prompt for participant number immediately after language selection
    let pnum = window.prompt('Enter participant number (e.g. 001):');
    if (pnum === null) pnum = 'unknown';
    pnum = String(pnum).trim();
    if (pnum.length === 0) pnum = 'unknown';
    window.participantNumber = pnum;
    // make it part of jsPsych data properties as well
    jsPsych.data.addProperties({ participant_number: pnum });
  }
};

/* ---------- Trial: Start / Instructions (centered) ---------- */
const start_screen = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
    <div style="display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif;">
      <div style="max-width:900px; margin:0 auto; text-align:center;">
        <h1 style= "font-size: 24px;">Welcome! Thank you for participating in the study.</h1>
        <p style= "font-size: 20px;">You will see several words on the screen along with a circle. Your task is to drag the words into the circle and arrange them to show how you think they are related in meaning.</p>
        <p style= "font-size: 20px;">The goal is for you to visually show how these 63 words are related to each other within the circle. Place words that you feel are similar in meaning closer together, and words that you feel are less related farther apart.</p>
        <p style= "font-size: 20px;">For example, if you think <em>red</em> and <em>blue</em> are closely related, but <em>red</em> and <em>sky</em> are not, you should place <em>red</em> and <em>blue</em> near each other and <em>red</em> and <em>sky</em> farther apart.</p>
        <p style="margin-top:18px; font-weight:bold; font-size: 24px;">Press the spacebar to start.</p>
      </div>
    </div>
  `,
  // accept common space key identifiers to maximize cross-browser support
  choices: [' ', 'Space', 'Spacebar']
};

/* ---------- Trial: Main word-arrangement task ---------- */
const circleTrial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: () => {
    const lang = jsPsych.data.get().last(1).values()[0].language;
    const words = getWordsByLanguage(lang);
    return generateWordCircleHTML(words);
  },
  choices: "NO_KEYS",
  on_load: () => {
    const words = document.querySelectorAll(".word");

    words.forEach(w => {
      // toggle selection on click
      w.addEventListener("click", () => {
        w.classList.toggle("selected");
      });

      // drag events
      w.addEventListener("dragstart", e => {
        e.dataTransfer.setData("text/plain", w.textContent);
        w.classList.add("dragging");
      });

      w.addEventListener("dragend", e => {
        w.classList.remove("dragging");
      });
    });

    const dropZone = document.getElementById("drop-zone");
      // Only highlight / accept drops when the cursor is inside the circular area
      function isInsideCircle(clientX, clientY, rect) {
        const offsetX = clientX - rect.left;
        const offsetY = clientY - rect.top;
        const cx = rect.width / 2;
        const cy = rect.height / 2;
        const dx = offsetX - cx;
        const dy = offsetY - cy;
        const dist = Math.sqrt(dx * dx + dy * dy);
        return dist <= rect.width / 2; // inside circle radius
      }

      dropZone.addEventListener("dragenter", e => {
        // compute whether the entry point is inside the circle
        const rect = dropZone.getBoundingClientRect();
        if (isInsideCircle(e.clientX, e.clientY, rect)) {
          e.preventDefault();
          dropZone.classList.add('drop-zone-active');
        }
      });

      dropZone.addEventListener("dragover", e => {
        const rect = dropZone.getBoundingClientRect();
        if (isInsideCircle(e.clientX, e.clientY, rect)) {
          e.preventDefault(); // allow drop only when inside circle
          dropZone.classList.add('drop-zone-active');
        } else {
          dropZone.classList.remove('drop-zone-active');
        }
      });

      dropZone.addEventListener("dragleave", e => {
        // remove active state when leaving
        dropZone.classList.remove('drop-zone-active');
      });

      dropZone.addEventListener("drop", e => {
        e.preventDefault();
        const rect = dropZone.getBoundingClientRect();
        // accept drop only if the cursor is within the circular area
        if (!isInsideCircle(e.clientX, e.clientY, rect)) {
          dropZone.classList.remove('drop-zone-active');
          return; // ignore drops outside the circle
        }
        dropZone.classList.remove('drop-zone-active');
        const dragging = document.querySelector(".dragging");
        if (dragging) {
          // coordinates relative to drop zone
          const offsetX = e.clientX - rect.left;
          const offsetY = e.clientY - rect.top;
          dragging.style.left = `${offsetX}px`;
          dragging.style.top = `${offsetY}px`;

          // append to drop zone so it stays inside
          dropZone.appendChild(dragging);
        }
      });

      // Finish button behavior: check whether all words are inside the circle
      const finishBtn = document.getElementById('finish-btn');
      if (finishBtn) {
        // function to test whether all words are inside the circular area
        function allWordsInside() {
          const wordsAll = Array.from(document.querySelectorAll('.word'));
          const rect = dropZone.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          const radius = rect.width / 2;
          return wordsAll.every(w => {
            const r = w.getBoundingClientRect();
            const wx = r.left + r.width / 2;
            const wy = r.top + r.height / 2;
            const dx = wx - cx;
            const dy = wy - cy;
            return Math.sqrt(dx * dx + dy * dy) <= radius;
          });
        }

        function updateFinishButton() {
          try {
            const ok = allWordsInside();
            finishBtn.disabled = !ok;
          } catch (err) {
            // if something goes wrong, keep button disabled
            finishBtn.disabled = true;
          }
        }

        // initial state
        updateFinishButton();

        // update button during relevant drag events
        // existing dragover and drop handlers already call class toggles; also update on dragend
        dropZone.addEventListener('dragover', e => {
          // update button based on cursor position inside/outside
          updateFinishButton();
        });
        dropZone.addEventListener('drop', e => {
          // after drop, update button (word may have moved inside)
          setTimeout(updateFinishButton, 10);
        });
        // update when a drag ends (in case word was dropped outside)
        document.addEventListener('dragend', e => setTimeout(updateFinishButton, 10));

        finishBtn.addEventListener('click', () => {
          // Button should be enabled only when all words are inside, but re-check defensively
          if (!allWordsInside()) return;

          // collect placements
          const placements = [];
          document.querySelectorAll('.word').forEach(w => {
            const parentRect = w.parentElement.getBoundingClientRect();
            const rectW = w.getBoundingClientRect();
            const x = rectW.left - parentRect.left;
            const y = rectW.top - parentRect.top;
            const cx = x + rectW.width / 2;
            const cy = y + rectW.height / 2;
            const cx_pct = cx / parentRect.width;
            const cy_pct = cy / parentRect.height;
            const dx = cx - parentRect.width / 2;
            const dy = cy - parentRect.height / 2;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const radius_pct = dist / (parentRect.width / 2);
            const angle_deg = Math.atan2(dy, dx) * 180 / Math.PI; // degrees, 0 = right
            placements.push({
              word: w.textContent,
              x: x, // top-left relative to parent (pixels)
              y: y,
              cx: cx, // center relative to parent (pixels)
              cy: cy,
              cx_pct: cx_pct,
              cy_pct: cy_pct,
              radius_pct: radius_pct,
              angle_deg: angle_deg,
              selected: w.classList.contains('selected')
            });
          });

          // show a blank overlay with final message
          const overlay = document.createElement('div');
          overlay.id = 'finish-overlay';
          overlay.innerHTML = `<div><h1>You are done! Thank you for your participating!</h1><button id="save-data">Save Data</button></div>`;
          document.body.appendChild(overlay);

          // save placements (POST to server, fallback to download) when Save Data clicked
          const saveBtn = document.getElementById('save-data');
          saveBtn.addEventListener('click', () => {
            const payload = { placements: placements, timestamp: new Date().toISOString(), participant_number: (window.participantNumber || 'unknown') };

            // Attempt to POST the placements to a server endpoint (/save_placement).
            // If the server isn't available, fall back to downloading a JSON file.
            const tryPostThenFinish = () => {
              // try localhost server by default; change this URL if your server runs elsewhere
              return fetch('http://localhost:5000/save_placement', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
              })
              .then(resp => {
                if (resp.ok) return resp.text();
                throw new Error('Server save failed');
              });
            };

            const finishLocally = () => {
              const dataStr = JSON.stringify(payload, null, 2);
              const blob = new Blob([dataStr], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              const p = (window.participantNumber || 'unknown');
              const filename = `P${p}_${(new Date()).toISOString().replace(/[:.]/g,'-')}.json`;
              // Note: browsers ignore paths; users will download to their Downloads folder.
              a.download = filename;
              document.body.appendChild(a);
              a.click();
              a.remove();
              URL.revokeObjectURL(url);
            };

            // Try server save, else fallback to download
            tryPostThenFinish()
              .catch(err => {
                console.warn('Server save failed, falling back to download:', err);
                finishLocally();
              })
              .finally(() => {
                overlay.remove();
                jsPsych.finishTrial(payload);
              });
          });
        });
      }
  },
  on_finish: () => {
    const placements = [];
    document.querySelectorAll(".word").forEach(w => {
      const parentRect = w.parentElement.getBoundingClientRect();
      const rect = w.getBoundingClientRect();
      const x = rect.left - parentRect.left;
      const y = rect.top - parentRect.top;
      const cx = x + rect.width / 2;
      const cy = y + rect.height / 2;
      const cx_pct = cx / parentRect.width;
      const cy_pct = cy / parentRect.height;
      const dx = cx - parentRect.width / 2;
      const dy = cy - parentRect.height / 2;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const radius_pct = dist / (parentRect.width / 2);
      const angle_deg = Math.atan2(dy, dx) * 180 / Math.PI;
      placements.push({
        word: w.textContent,
        x: x,
        y: y,
        cx: cx,
        cy: cy,
        cx_pct: cx_pct,
        cy_pct: cy_pct,
        radius_pct: radius_pct,
        angle_deg: angle_deg,
        selected: w.classList.contains("selected")
      });
    });
    jsPsych.data.addData({ placements });
  }
};

const save_data = {
  type: jsPsychPipe,
  action: "save",
  experiment_id: "dsYOUzAvTYUp",  // your experiment key
  filename: filename,
  data_string: () => jsPsych.data.get().csv()
};

timeline.push(save_data);


/* ---------- Run experiment ---------- */
jsPsych.run([lang_choice, start_screen, circleTrial]);