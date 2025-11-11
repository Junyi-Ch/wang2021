/* ---------- Initialize jsPsych ---------- */
const jsPsych = initJsPsych({
  on_finish: () => {
    // do not display raw data to the participant
    // final debrief and saving handled in timeline
  }
});


// Create timeline array
const timeline = [];

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

/* ---------- Trial: Informed Consent Form (NEW) ---------- */
const consent_form = {
  type: jsPsychHtmlButtonResponse,
  stimulus: `
    <div style="max-width:800px; margin:0 auto; text-align:left; font-size: 16px; padding: 10px 0;">
      <h1>Informed Consent Form</h1>
      <p>You are being invited to participate in a research study titled <strong>“Reproducibility of Psychological Science and Instruction.”</strong> This study is being done by Dr. Bria Long from UC San Diego and associated graduate students in the Experimental Methods course. You were selected to participate in this study because you are an adult in the U.S. and have been a represented population in previous psychology studies.</p>
      
      <p>The purpose of this study is to better understand how well previously published studies in the psychological field replicate online and with different populations. Your participation in this research should last approximately <strong>5-30 minutes</strong>. If you agree to take part in this study, you may be asked to view a set of stimuli, including pictures, sounds, written text, or videos and then giving some responses via key-presses, verbally, or with paper-and-pencil. We may also observe your choices or preferences among an array of stimuli. These stimuli will be taken directly from or closely adapted from studies that already exist in the published psychological literature. Stimuli will include, e.g., pictures of objects and human faces, audio and video clips, short text passages, etc. None of the stimuli will be disturbing, threatening, or offensive. The online and in-person experiments described in this protocol will take no more than 30 minutes. An example game you might play would be to click on an image on the screen that matches a word you hear being said out loud. Your total expected time commitment for this study is between 5-30 minutes, and is specified in the study description.</p>
      
      <p>Your participation in this study is completely voluntary and you can withdraw at any time. Choosing not to participate or withdrawing will result in no penalty or loss of benefits to which you are entitled. You are free to skip any question that you choose.</p>
      
      <p>We will not be asking for any personally identifying information, and we will handle responses as confidentially as possible. Your SONA or Prolific IDs will never be tied to your responses on this survey. However, we cannot guarantee the confidentiality of information transmitted over the Internet. To minimize this risk, data containing anything that might be personally identifiable (e.g. Prolific IDs or IP addresses) will be encrypted on transfer and storage and will only be accessible to qualified lab personnel. We will be keeping data collected as part of this experiment indefinitely. This anonymized data (containing neither Prolific IDs nor IP addresses) may be shared with the scientific community or with other participants to be used as stimuli in future studies.</p>
      
      <p>If you have questions about this project or if you have a research-related problem, you may contact the researcher(s), <strong>Dr. Bria Long, <a href="mailto:brlong@ucsd.edu">brlong@ucsd.edu</a></strong>. If you have any questions concerning your rights as a research subject, you may contact the UC San Diego Office of IRB Administration at <a href="mailto:irb@ucsd.edu">irb@ucsd.edu</a> or 858-246-4777.</p>
      
      <h3 style="margin-top: 25px;">Consent Statement</h3>
      <p style="font-weight: bold;">By participating in this research you are indicating that you are at least 18 years old, have read this consent form, and agree to participate in this research study. Please keep this consent form for your records.</p>
    </div>
  `,
  choices: ['I Agree to Participate'],
  data: {
    // Add trial information for data tracking
    trial_id: 'consent_form'
  }
};


/* ---------- Trial: Choose Language ---------- */
const lang_choice = {
  type: jsPsychHtmlButtonResponse,
  stimulus: "<p style='font-size:20px;'>Choose your language:</p>",
  choices: ["中文", "English"],
  on_finish: data => {
  const lang = data.response === 0 ? "zh" : "en";
  jsPsych.data.addProperties({ language: lang });

  // Create an automatic participant number (short, unique)
  // Format: <random10>_<base36timestamp6> e.g. "a1b2c3d4e5_k9f2z1"
  const autoId = `${subject_id}_${Date.now().toString(36).slice(-6)}`;
  window.participantNumber = autoId;

  // Add to global jsPsych properties so it appears on all trials
  jsPsych.data.addProperties({ participant_number: window.participantNumber });
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

const enter_fullscreen = {
  type: jsPsychFullscreen,
  fullscreen_mode: true,
  message: `
    <div style="max-width:900px; margin:0 auto; text-align:center;">
      <h2>Full screen required</h2>
      <p>For best performance this study will switch your browser to full screen. Please allow full screen and press the button below to continue.</p>
      <p><strong>Note:</strong> to exit at any time press ESC (or follow your browser's full screen controls).</p>
    </div>
  `,
  button_label: 'Enter full screen'
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

    // --- make words draggable/selectable ---
    words.forEach(w => {
      w.addEventListener("click", () => w.classList.toggle("selected"));
      w.addEventListener("dragstart", e => {
        e.dataTransfer.setData("text/plain", w.textContent);
        w.classList.add("dragging");
      });
      w.addEventListener("dragend", () => w.classList.remove("dragging"));
    });

    // --- drop-zone logic ---
    const dropZone = document.getElementById("drop-zone");
    function isInsideCircle(x, y, rect) {
      const dx = x - (rect.left + rect.width / 2);
      const dy = y - (rect.top + rect.height / 2);
      return Math.sqrt(dx * dx + dy * dy) <= rect.width / 2;
    }

    dropZone.addEventListener("dragenter", e => {
      const rect = dropZone.getBoundingClientRect();
      if (isInsideCircle(e.clientX, e.clientY, rect)) {
        e.preventDefault();
        dropZone.classList.add("drop-zone-active");
      }
    });
    dropZone.addEventListener("dragover", e => {
      const rect = dropZone.getBoundingClientRect();
      if (isInsideCircle(e.clientX, e.clientY, rect)) {
        e.preventDefault();
        dropZone.classList.add("drop-zone-active");
      } else dropZone.classList.remove("drop-zone-active");
    });
    dropZone.addEventListener("dragleave", () =>
      dropZone.classList.remove("drop-zone-active")
    );
    dropZone.addEventListener("drop", e => {
      e.preventDefault();
      const rect = dropZone.getBoundingClientRect();
      if (!isInsideCircle(e.clientX, e.clientY, rect)) return;
      dropZone.classList.remove("drop-zone-active");
      const dragging = document.querySelector(".dragging");
      if (dragging) {
        dragging.style.left = `${e.clientX - rect.left}px`;
        dragging.style.top = `${e.clientY - rect.top}px`;
        dropZone.appendChild(dragging);
      }
    });

    // --- finish-button setup ---
    const finishBtn = document.getElementById("finish-btn");
    if (!finishBtn) return;

    // helper: are all words inside?
    function allWordsInside() {
      const ws = Array.from(document.querySelectorAll(".word"));
      const rect = dropZone.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const r = rect.width / 2;
      return ws.every(w => {
        const box = w.getBoundingClientRect();
        const wx = box.left + box.width / 2;
        const wy = box.top + box.height / 2;
        return Math.hypot(wx - cx, wy - cy) <= r;
      });
    }

    function updateFinishButton() {
      finishBtn.disabled = !allWordsInside();
    }

    updateFinishButton();
    dropZone.addEventListener("dragover", updateFinishButton);
    dropZone.addEventListener("drop", () => setTimeout(updateFinishButton, 10));
    document.addEventListener("dragend", () => setTimeout(updateFinishButton, 10));

    // --- FINISH-button click handler ---
    finishBtn.addEventListener("click", () => {
      // collect placements
      const placements = Array.from(document.querySelectorAll(".word")).map(w => {
        const rect = w.getBoundingClientRect();
        return {
          word: w.textContent,
          cx: rect.left + rect.width / 2,
          cy: rect.top + rect.height / 2
        };
      });

      const payload = {
        participant_id: subject_id,
        participant_number: window.participantNumber || "unknown",
        timestamp: new Date().toISOString(),
        placements
      };

      // overlay “thank you”
      const overlay = document.createElement("div");
      overlay.id = "finish-overlay";
      Object.assign(overlay.style, {
        position: "fixed",
        left: 0,
        top: 0,
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(255,255,255,0.95)",
        zIndex: 9999
      });
      overlay.innerHTML =
        "<div style='text-align:center;'><h1>You are done! Thank you for your participation!</h1></div>";
      document.body.appendChild(overlay);

      // compute ISC
      let iscResult;
      try {
        if (
          window.ISCProcessor &&
          typeof window.ISCProcessor.processPlacementsForISC === "function"
        ) {
          iscResult = window.ISCProcessor.processPlacementsForISC(placements);
        } else if (typeof processPlacementsForISC === "function") {
          iscResult = processPlacementsForISC(placements);
        } else {
          // fallback computation (short form)
          const n = placements.length;
          const dist = Array(n)
            .fill()
            .map(() => Array(n).fill(0));
          for (let i = 0; i < n; i++)
            for (let j = i + 1; j < n; j++) {
              const d = Math.hypot(
                placements[i].cx - placements[j].cx,
                placements[i].cy - placements[j].cy
              );
              dist[i][j] = dist[j][i] = d;
            }
          const flat = dist.flat().filter((v, i) => i % (n + 1) !== 0);
          const min = Math.min(...flat);
          const max = Math.max(...flat);
          const norm = dist.map(row =>
            row.map(v => (v - min) / (max - min || 1))
          );
          const vec = [];
          for (let i = 0; i < n; i++)
            for (let j = i + 1; j < n; j++) vec.push(norm[i][j]);
          iscResult = {
            n_words: n,
            words: placements.map(p => p.word),
            placements,
            distance_matrix: norm,
            dissimilarity_vector: vec,
            matrix_stats: {
              min_distance: min,
              max_distance: max,
              mean_normalized:
                vec.length > 0
                  ? vec.reduce((a, b) => a + b, 0) / vec.length
                  : null
            }
          };
        }
      } catch (e) {
        console.error("Error computing ISC:", e);
        iscResult = { placements };
      }

      // make csv row
      const csvRow = {
        participant_id: payload.participant_id,
        participant_number: payload.participant_number,
        language:
          jsPsych.data
            .get()
            .filter({ language: { $exists: true } })
            .values()[0]?.language || "unknown",
        timestamp: payload.timestamp,
        n_words: iscResult.n_words || placements.length,
        placements_json: JSON.stringify(iscResult.placements),
        words_json: JSON.stringify(iscResult.words),
        distance_matrix_json: JSON.stringify(iscResult.distance_matrix),
        dissimilarity_vector_json: JSON.stringify(
          iscResult.dissimilarity_vector
        ),
        matrix_min: iscResult.matrix_stats?.min_distance ?? null,
        matrix_max: iscResult.matrix_stats?.max_distance ?? null,
        matrix_mean_normalized:
          iscResult.matrix_stats?.mean_normalized ?? null,
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height
      };

      const combinedData = { ...csvRow, raw_payload: payload, isc_raw: iscResult };

      // finish trial (jsPsych writes data automatically)
      jsPsych.finishTrial(combinedData);

      // remove overlay shortly after
      setTimeout(() => overlay.remove(), 1500);

      // optional direct POST if you keep it
      /*
      try {
        const dpPayload = {
          experiment_id: "dsYOUzAvTYUp",
          filename: filename.replace(".csv", ".json"),
          data_string: JSON.stringify({
            participant_id: subject_id,
            participant_number: window.participantNumber || "unknown",
            timestamp: new Date().toISOString(),
            placements,
            isc: iscResult
          })
        };
        fetch("https://pipe.jspsych.org/api/data/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dpPayload)
        })
          .then(async r => console.log("Datapipe response", r.status, await r.text()))
          .catch(e => console.error("Datapipe POST error", e));
      } catch (e) {
        console.warn("Error attempting datapipe POST", e);
      }
      */
    });
  },

  on_finish: () => {
    /* nothing extra here; data are added by finishTrial above */
  }
};


// Diagnostic trial: check whether the datapipe plugin is available at runtime
const check_datapipe = {
  type: jsPsychCallFunction,
  func: () => {
    console.log('--- Datapipe diagnostic ---');
    console.log('typeof jsPsychPipe:', typeof jsPsychPipe);
    try {
      console.log('jsPsych.plugins["pipe"]:', jsPsych.plugins && jsPsych.plugins['pipe']);
    } catch (e) {
      console.warn('Could not read jsPsych.plugins["pipe"]', e);
    }
    // show counts of data entries and last trial with placements
    try {
      const withPlacements = jsPsych.data.get().filter(tr => tr.raw_payload !== undefined).values();
      console.log('Trials with raw_payload count:', withPlacements.length);
      if (withPlacements.length > 0) console.log('Example raw_payload (first):', withPlacements[0]);
      console.log('window.__lastPlacementsData:', window.__lastPlacementsData);
    } catch (e) {
      console.warn('Error checking jsPsych.data', e);
    }
  }
};

/* ---------- Helper function for Proficiency Select (FIXED: Moved to global scope) ---------- */
function createProficiencySelect(name, required = true) {
  return `
      <select id="${name}" name="${name}" ${required ? 'required' : ''}>
          <option value="">--Select Proficiency--</option>
          <option value="Native">Native Speaker</option>
          <option value="Advanced">Advanced (Fluent, near-native)</option>
          <option value="Intermediate">Intermediate (Conversational)</option>
          <option value="Basic">Basic (Simple phrases, travel use)</option>
          <option value="None">None</option>
      </select>
  `;
}

/* ---------- Trial: Demographics Survey (FIXED) ---------- */
const demographics_survey = {
  type: jsPsychSurveyHtmlForm,
  preamble: '<h2>Demographic Information</h2><p>Please answer the following questions. Your responses will remain confidential.</p>',
  html: `
    <div class="jspsych-survey-html-form-item">
      <label for="age"><strong>1. Age:</strong></label>
      <input type="number" id="age" name="age" min="18" max="100" required>
    </div>
    <br>

    <div class="jspsych-survey-html-form-item">
      <label><strong>2. Gender:</strong></label><br>
      <input type="radio" id="gender_female" name="gender" value="Female" required>
      <label for="gender_female">Female</label><br>
      <input type="radio" id="gender_male" name="gender" value="Male">
      <label for="gender_male">Male</label><br>
      <input type="radio" id="gender_nonbinary" name="gender" value="Non-binary">
      <label for="gender_nonbinary">Non-binary</label><br>
      <input type="radio" id="gender_other" name="gender" value="Other">
      <label for="gender_other">Other (Please specify):</label>
      <input type="text" name="gender_other_text" style="width: 150px;">
    </div>
    <br>

    <div class="jspsych-survey-html-form-item">
      <label for="education"><strong>3. Highest Education Level Completed:</strong></label>
      <select id="education" name="education" required>
        <option value="">--Select One--</option>
        <option value="High School">High School Diploma/GED</option>
        <option value="Some College">Some College (No Degree)</option>
        <option value="Associate">Associate's Degree</option>
        <option value="Bachelor">Bachelor's Degree</option>
        <option value="Master">Master's Degree</option>
        <option value="Doctorate">Doctoral Degree (e.g., PhD, EdD)</option>
        <option value="Professional">Professional Degree (e.g., MD, JD)</option>
        <option value="Other">Other</option>
      </select>
    </div>
    <br>

    <div class="jspsych-survey-html-form-item">
      <label for="english_proficiency"><strong>4. English Proficiency:</strong></label>
      ${createProficiencySelect('english_proficiency')}
    </div>
    <br>

    <div class="jspsych-survey-html-form-item">
      <label for="mandarin_proficiency"><strong>5. Mandarin Chinese (Putonghua/Guoyu) Proficiency:</strong></label>
      ${createProficiencySelect('mandarin_proficiency')}
    </div>
    <br>

    <div class="jspsych-survey-html-form-item">
      <label for="other_languages"><strong>6. List any other languages you speak/understand, and your proficiency level in each:</strong></label><br>
      <textarea id="other_languages" name="other_languages" rows="4" cols="50"></textarea>
      <p style="font-size: small; color: gray;">Example: Cantonese: Native; Spanish: Basic; French: None.</p>
    </div>
  `,
  button_label: 'Continue'
};


/* ---------- Single DataPipe save trial (CSV) ---------- */
const save_data = {
  type: jsPsychPipe,
  action: "save",
  experiment_id: "dsYOUzAvTYUp",
  filename: filename,
  data_string: () => {
    // returns CSV of all jsPsych.data rows (one row per participant)
    return jsPsych.data.get().csv();
  }
};

const debrief = {
  type: jsPsychHtmlButtonResponse,
  stimulus: `
    <div style="max-width:900px; margin:0 auto; text-align:left;">
      <h2>Debriefing</h2>
      <p>Thank you for participating in our study!
      <p> This research investigates how people mentally organize word meanings — in other words, how individuals represent and connect concepts in their “semantic networks.” We are especially interested in whether there are consistent individual differences in how people group words based on meaning, and whether these differences depend on the type of word — for example, whether the words refer to concrete things (like apple or chair) or to more abstract ideas (like justice or freedom).
      By examining patterns across participants, we aim to better understand how people’s mental representations of language vary and what factors might shape those differences. This work may ultimately contribute to our understanding of how experience, culture, and cognition influence the way we structure meaning.
      If you have any questions about the study, please contact the research team at [insert your lab or PI’s email address].</p>
      <p>Thank you again for your time and contribution!</p>
      <p>If you have any questions about the study please contact the experimenter.</p>
    </div>
  `,
  choices: ['Finish'],
  on_finish: () => {
    // exit fullscreen after debrief (optional)
    if (typeof jsPsych !== 'undefined' && jsPsych.pluginAPI) {
      // use fullscreen plugin to exit
      // Add a short fullscreen exit trial instead if plugin requires it; otherwise call requestExitFullscreen
      try { document.exitFullscreen && document.exitFullscreen(); } catch (e) {}
    }
  }
};


/* ---------- Experiment timeline ---------- */
timeline.push(consent_form);      // <-- NEW: Consent form first
timeline.push(lang_choice);
timeline.push(start_screen);
timeline.push(enter_fullscreen);
timeline.push(circleTrial);
// diagnostic check (plugin presence and payload)
timeline.push(check_datapipe);
// Add the new demographics survey here
timeline.push(demographics_survey); 
// single CSV save to datapipe
timeline.push(save_data);
timeline.push(debrief);   

/* ---------- Run experiment ---------- */
jsPsych.run(timeline);